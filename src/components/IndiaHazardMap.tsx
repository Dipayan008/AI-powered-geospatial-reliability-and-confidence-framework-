import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { Layers } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface IndiaHazardMapProps {
  hazards: HazardZone[];
  selectedZone: HazardZone | null;
  onSelectZone: (zone: HazardZone) => void;
  onOpenAlertModal: () => void;
}

export const IndiaHazardMap: React.FC<IndiaHazardMapProps> = ({
  hazards,
  selectedZone,
  onSelectZone,
  onOpenAlertModal,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const markersGroupRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    if (!mapContainerRef.current) return;

    if (!mapInstanceRef.current) {
      const map = L.map(mapContainerRef.current, {
        center: [20.5937, 78.9629],
        zoom: 5,
        zoomControl: false,
        scrollWheelZoom: false,
      });

      L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; CARTO &copy; OpenStreetMap',
        subdomains: 'abcd',
        maxZoom: 19,
      }).addTo(map);

      L.control.zoom({ position: 'topright' }).addTo(map);

      setTimeout(() => {
        map.invalidateSize();
      }, 100);

      markersGroupRef.current = L.layerGroup().addTo(map);
      mapInstanceRef.current = map;
    }

    return () => {
      if (mapInstanceRef.current) {
        mapInstanceRef.current.remove();
        mapInstanceRef.current = null;
      }
    };
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current || !markersGroupRef.current) return;

    mapInstanceRef.current.invalidateSize();
    markersGroupRef.current.clearLayers();

    // 1. Draw connecting vector lines and origin hazard radius for selected zone
    if (selectedZone) {
      // Connect Pin Point Origin to each Surrounding Social Hotspot with dashed vectors
      if (selectedZone.socialGatheringHotspots) {
        selectedZone.socialGatheringHotspots.forEach((hotspot) => {
          const connectionLine = L.polyline([selectedZone.coordinates, hotspot.coordinates], {
            color: '#F59E0B',
            weight: 1.5,
            dashArray: '4, 6',
            opacity: 0.75,
          });
          connectionLine.addTo(markersGroupRef.current!);
        });
      }

      // Render Epicenter Pulse Circle around Pin Point Origin
      const riskColor = selectedZone.riskLevel === 'High' ? '#E05A32' : selectedZone.riskLevel === 'Medium' ? '#F59E0B' : '#10B981';
      const originPulseCircle = L.circle(selectedZone.coordinates, {
        color: riskColor,
        fillColor: riskColor,
        fillOpacity: 0.12,
        radius: 1000,
        weight: 1.5,
        dashArray: '4, 4',
      });
      originPulseCircle.addTo(markersGroupRef.current!);
    }

    // 2. Render Primary Hazard Pin Point Origin Markers
    hazards.forEach((zone) => {
      let colorHex = '#10B981'; // Green
      let labelText = 'LOW';

      if (zone.riskLevel === 'High') {
        colorHex = '#E05A32'; // Red/Orange accent
        labelText = 'HIGH';
      } else if (zone.riskLevel === 'Medium') {
        colorHex = '#F59E0B'; // Yellow
        labelText = 'MED';
      }

      const isSelected = selectedZone?.id === zone.id;

      const originMarkerIcon = L.divIcon({
        className: 'custom-hazard-marker',
        html: `
          <div style="border: 2px solid ${isSelected ? '#38BDF8' : colorHex}; background: #181C24;"
               class="flex flex-col items-center justify-center w-[52px] h-[52px] rounded-xl cursor-pointer text-white font-mono font-bold transition-transform hover:scale-110 shadow-lg">
            <span style="color: ${colorHex}" class="text-[14px] font-black leading-none">${zone.confidencePercentage}%</span>
            <span class="text-[8px] tracking-tighter uppercase font-bold text-[#8E95A5] leading-none mt-0.5">${labelText}</span>
          </div>
        `,
        iconSize: [52, 52],
        iconAnchor: [26, 26],
      });

      const marker = L.marker(zone.coordinates, { 
        icon: originMarkerIcon,
        zIndexOffset: isSelected ? 3000 : 1000,
      });

      const popupHtml = `
        <div class="p-2 space-y-2 font-sans text-xs">
          <div class="flex items-center justify-between border-b border-[#2A303D] pb-1.5">
            <span class="font-bold text-white font-mono text-[10px] uppercase">📍 PIN POINT ORIGIN // ${zone.id}</span>
            <span class="px-2 py-0.5 rounded text-[9px] font-mono font-bold" style="background-color: ${colorHex}25; color: ${colorHex}">
              ${zone.riskLevel.toUpperCase()} RISK (${zone.confidencePercentage}%)
            </span>
          </div>
          
          <div>
            <div class="font-bold text-white text-xs">${zone.targetTownVillage}</div>
            <div class="text-[#8E95A5] text-[10px]">${zone.subDistrictDistrict}, ${zone.stateRegion}</div>
          </div>

          <div class="bg-[#12141C] p-2 rounded border border-[#2A303D] space-y-1 font-mono text-[10px]">
            <div class="text-[#38BDF8] font-bold">📍 Origin Coords: ${zone.coordinates[0].toFixed(4)}° N, ${zone.coordinates[1].toFixed(4)}° E</div>
            <div class="text-[#E05A32] font-semibold text-[9px]">⚠️ Focal Point: ${zone.epicenterFocalPoint}</div>
            <div class="text-[#8E95A5] truncate pt-0.5">Alert Scope: ${zone.affectedPopulationEstimate}</div>
          </div>

          <div class="pt-1">
            <button id="btn-alert-${zone.id}" class="w-full py-1.5 bg-[#E05A32] hover:bg-[#c94e2a] text-white font-mono text-[10px] font-bold rounded transition-all flex items-center justify-center gap-1">
              🚨 TRIGGER ALERT
            </button>
          </div>
        </div>
      `;

      marker.bindPopup(popupHtml, { maxWidth: 270, autoPan: true });

      marker.on('click', () => {
        onSelectZone(zone);
        setTimeout(() => {
          const btn = document.getElementById(`btn-alert-${zone.id}`);
          if (btn) btn.onclick = () => onOpenAlertModal();
        }, 100);
      });

      marker.addTo(markersGroupRef.current!);
    });

    // 3. Render Secondary Surrounding Social Gathering Hotspot Markers
    if (selectedZone && selectedZone.socialGatheringHotspots) {
      selectedZone.socialGatheringHotspots.forEach((hotspot) => {
        let categoryEmoji = '🛍️';
        if (hotspot.category.includes('Mall')) categoryEmoji = '🏬';
        else if (hotspot.category.includes('Park')) categoryEmoji = '🌳';
        else if (hotspot.category.includes('Transit')) categoryEmoji = '🚉';

        const hotspotIcon = L.divIcon({
          className: 'social-hotspot-marker',
          html: `
            <div style="border: 1.5px solid #F59E0B; background: #14161B; width: 36px; height: 36px; overflow: hidden;"
                 class="flex flex-col items-center justify-center rounded-full cursor-pointer text-[#F59E0B] font-mono shadow-md hover:scale-110 transition-transform"
                 title="${hotspot.name}">
              <span style="font-size: 14px; line-height: 1;">${categoryEmoji}</span>
              <span style="font-size: 7px; color: #F59E0B; font-weight: 800; text-transform: uppercase; letter-spacing: 0.02em; line-height: 1; margin-top: 1px;">HUB</span>
            </div>
          `,
          iconSize: [36, 36],
          iconAnchor: [18, 18],
        });

        const hotspotMarker = L.marker(hotspot.coordinates, { 
          icon: hotspotIcon,
          zIndexOffset: -100,
        });

        const hotspotPopup = `
          <div class="p-2 space-y-1.5 font-sans text-xs">
            <div class="font-bold text-[#F59E0B] font-mono text-[10px] uppercase">SURROUNDING SOCIAL HUB // ${hotspot.category}</div>
            <div class="font-bold text-white text-xs">${hotspot.name}</div>
            <div class="text-[#8E95A5] text-[10px] font-mono">📍 ${hotspot.distanceKm} km from Pin Point Origin (${selectedZone.targetTownVillage})</div>
            <div class="text-[#38BDF8] font-mono text-[9.5px]">Coords: ${hotspot.coordinates[0].toFixed(4)}° N, ${hotspot.coordinates[1].toFixed(4)}° E</div>
            <div class="text-white font-mono text-[10px] bg-[#12141C] p-2 rounded border border-[#2A303D] mt-1 space-y-1">
              <div class="text-[#F59E0B] font-bold">Crowd Density: ${hotspot.peakCrowdEstimate}</div>
              <div class="text-[#E05A32] text-[9.5px] leading-tight">Evacuation Directive: ${hotspot.evacuationDirective}</div>
            </div>
          </div>
        `;
        hotspotMarker.bindPopup(hotspotPopup, { maxWidth: 260 });
        hotspotMarker.addTo(markersGroupRef.current!);
      });
    }
  }, [hazards, selectedZone, onSelectZone, onOpenAlertModal]);

  return (
    <div className="glass-panel rounded-xl overflow-hidden border border-[#2A303D] flex flex-col h-full min-h-[380px] shadow-xl relative">
      <div className="px-5 py-3.5 bg-[#181C24] border-b border-[#2A303D] flex flex-wrap items-center justify-between gap-3 select-none">
        <div className="flex items-center space-x-2 font-mono text-sm">
          <Layers className="w-4 h-4 text-[#38BDF8]" />
          <span className="font-bold text-white uppercase tracking-wider">
            GEOSPATIAL HAZARD MAP
          </span>
        </div>

        <div className="flex items-center space-x-4 font-mono text-xs">
          <span className="flex items-center gap-1.5 text-[#8E95A5]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#10B981]"></span>
            <span>Low Risk</span>
          </span>
          <span className="flex items-center gap-1.5 text-[#8E95A5]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#F59E0B]"></span>
            <span>Medium Risk</span>
          </span>
          <span className="flex items-center gap-1.5 text-[#8E95A5]">
            <span className="w-2.5 h-2.5 rounded-full bg-[#E05A32]"></span>
            <span>High Risk</span>
          </span>
        </div>
      </div>

      <div className="relative flex-1 w-full overflow-hidden">
        <div ref={mapContainerRef} className="w-full h-full" />
      </div>
    </div>
  );
};

