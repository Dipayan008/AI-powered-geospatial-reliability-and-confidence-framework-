import React from 'react';
import { Target, BarChart3, Compass, AlertCircle, Users } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface PatternConfidenceScorecardProps {
  selectedZone: HazardZone | null;
}

export const PatternConfidenceScorecard: React.FC<PatternConfidenceScorecardProps> = ({
  selectedZone,
}) => {
  if (!selectedZone) return null;

  return (
    <div className="glass-panel p-6 md:p-7 rounded-xl border border-[#2A303D] space-y-5 flex flex-col shadow-xl">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-[#2A303D] pb-4">
        <div className="flex items-center space-x-2.5">
          <Target className="w-5 h-5 text-[#38BDF8]" />
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
            AI PATTERN CONFIDENCE SCORECARD
          </h2>
        </div>
      </div>

      {/* High Danger Epicenter & Coordinates Box */}
      <div className="bg-[#14161B] p-4 rounded-xl border border-[#E05A32]/50 space-y-3 font-mono">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <span className="text-xs text-[#8E95A5] uppercase font-bold flex items-center gap-1.5">
            <Compass className="w-4 h-4 text-[#E05A32]" />
            TARGET TOWN / VILLAGE FOCAL POINT
          </span>
          <span className="px-2 py-0.5 rounded text-xs font-bold bg-[#E05A32]/20 text-[#E05A32] border border-[#E05A32]/40">
            PRIORITY ALERT ZONE
          </span>
        </div>

        <div>
          <span className="text-base font-bold text-white block">{selectedZone.targetTownVillage}</span>
          <span className="text-xs text-[#8E95A5]">{selectedZone.subDistrictDistrict}, {selectedZone.stateRegion}</span>
        </div>

        <div className="flex items-center justify-between pt-2 border-t border-[#2A303D] text-xs">
          <div>
            <span className="text-[11px] text-[#8E95A5] block">FOCAL LATITUDE</span>
            <span className="text-[#38BDF8] font-bold text-sm">{selectedZone.coordinates[0].toFixed(4)}° N</span>
          </div>
          <div className="text-right">
            <span className="text-[11px] text-[#8E95A5] block">FOCAL LONGITUDE</span>
            <span className="text-[#38BDF8] font-bold text-sm">{selectedZone.coordinates[1].toFixed(4)}° E</span>
          </div>
        </div>

        <div className="text-xs text-[#E05A32] pt-2 border-t border-[#2A303D]/60 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0 text-[#E05A32]" />
          <span className="leading-snug">{selectedZone.epicenterFocalPoint || 'Max Impact Epicenter Focal Point'}</span>
        </div>
      </div>

      {/* Pattern Confidence Score Widget */}
      <div className="glass-panel-accent p-5 rounded-xl border border-[#2A303D] relative overflow-hidden text-center space-y-3">
        <div className="text-xs font-mono text-[#8E95A5] uppercase tracking-widest">
          Pattern Match Confidence Score
        </div>

        <div className="flex items-center justify-center space-x-4 my-1">
          <div className="text-5xl font-extrabold font-mono tracking-tight text-white">
            {selectedZone.confidencePercentage}%
          </div>
          <div className="text-left font-mono">
            <div className="text-sm font-bold uppercase text-[#38BDF8]">
              {selectedZone.confidencePercentage >= 85 ? 'HIGH MATCH' : 'STANDARD CORRELATION'}
            </div>
            <div className="text-xs text-[#8E95A5]">
              Margin of Error: ± 2.1%
            </div>
          </div>
        </div>

        <div className="w-full bg-[#12141C] h-3 rounded-full overflow-hidden border border-[#2A303D]">
          <div
            className="h-full bg-[#38BDF8] transition-all duration-700"
            style={{ width: `${selectedZone.confidencePercentage}%` }}
          />
        </div>

        <div className="text-xs font-mono text-[#8E95A5]">
          Target: <strong className="text-white">{selectedZone.name}</strong> ({selectedZone.disasterType})
        </div>
      </div>

      {/* Surrounding High-Density Social Gathering Places System */}
      {selectedZone.socialGatheringHotspots && selectedZone.socialGatheringHotspots.length > 0 && (
        <div className="space-y-3 pt-3 border-t border-[#2A303D]">
          <div className="flex items-center justify-between text-xs font-mono font-bold text-white uppercase flex-wrap gap-2">
            <span className="flex items-center gap-1.5 text-[#F59E0B]">
              <Users className="w-4 h-4" />
              SURROUNDING SOCIAL GATHERING HOTSPOTS ({selectedZone.socialGatheringHotspots.length})
            </span>
            <span className="text-[#8E95A5] text-[11px]">HIGH DENSITY WARNING</span>
          </div>

          <div className="space-y-3">
            {selectedZone.socialGatheringHotspots.map((hotspot) => (
              <div key={hotspot.id} className="p-3.5 rounded-xl bg-[#14161B] border border-[#2A303D] space-y-2 font-mono text-xs">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <span className="font-bold text-white block text-sm">{hotspot.name}</span>
                    <span className="text-[#8E95A5] text-xs">{hotspot.category} • {hotspot.distanceKm} km from origin</span>
                  </div>
                  <span className="px-2 py-0.5 rounded text-[10px] font-bold bg-[#F59E0B]/20 text-[#F59E0B] border border-[#F59E0B]/40 uppercase flex-shrink-0">
                    {hotspot.peakCrowdEstimate}
                  </span>
                </div>
                <div className="text-[#8E95A5] text-xs leading-relaxed pt-1.5 border-t border-[#2A303D]/60">
                  <strong className="text-[#E05A32]">Directive:</strong> {hotspot.evacuationDirective}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Telemetry Metrics */}
      <div className="space-y-3 pt-3 border-t border-[#2A303D]">
        <div className="text-xs font-mono text-[#8E95A5] uppercase font-bold flex items-center justify-between">
          <span className="flex items-center gap-1.5">
            <BarChart3 className="w-4 h-4 text-[#38BDF8]" />
            TELEMETRY METRICS
          </span>
          <span className="text-[#10B981] font-bold text-xs">ONLINE</span>
        </div>

        <div className="grid grid-cols-2 gap-3 text-xs font-mono">
          <div className="bg-[#181C24] p-3 rounded-xl border border-[#2A303D] space-y-1">
            <span className="text-[#8E95A5] block text-[11px]">SATELLITE BACKSCATTER:</span>
            <span className="text-white font-bold text-sm">-85.4 dB</span>
          </div>

          <div className="bg-[#181C24] p-3 rounded-xl border border-[#2A303D] space-y-1">
            <span className="text-[#8E95A5] block text-[11px]">PRECIPITATION:</span>
            <span className="text-[#10B981] font-bold text-sm">+145mm</span>
          </div>
        </div>
      </div>
    </div>
  );
};
