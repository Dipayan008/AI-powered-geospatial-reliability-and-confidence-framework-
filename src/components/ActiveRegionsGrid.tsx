import React from 'react';
import { Compass, CheckCircle } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface ActiveRegionsGridProps {
  allZones: HazardZone[];
  selectedZone: HazardZone | null;
  onSelectZone: (zone: HazardZone) => void;
}

export const ActiveRegionsGrid: React.FC<ActiveRegionsGridProps> = ({
  allZones,
  selectedZone,
  onSelectZone,
}) => {
  return (
    <div className="glass-panel p-5 md:p-6 rounded-xl border border-[#2A303D] space-y-4 shadow-xl w-full">
      <div className="flex items-center justify-between border-b border-[#2A303D] pb-3 flex-wrap gap-2">
        <div className="flex items-center space-x-2 font-mono text-xs md:text-sm font-bold text-white uppercase tracking-wider">
          <Compass className="w-4 h-4 text-[#38BDF8]" />
          <span>ACTIVE MONITORED HAZARD REGIONS ({allZones.length})</span>
        </div>
        <span className="text-xs font-mono text-[#38BDF8]">Select Region to Inspect Telemetry & Map</span>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
        {allZones.map((zone) => {
          const isSelected = selectedZone?.id === zone.id;
          let riskColor = '#10B981';
          if (zone.riskLevel === 'High') riskColor = '#E05A32';
          else if (zone.riskLevel === 'Medium') riskColor = '#F59E0B';

          return (
            <div
              key={zone.id}
              onClick={() => onSelectZone(zone)}
              className={`p-3.5 rounded-xl cursor-pointer transition-all flex flex-col justify-between h-full min-h-[140px] space-y-2 border relative overflow-hidden ${
                isSelected
                  ? 'bg-[#191D26] border-[#38BDF8] shadow-lg ring-1 ring-[#38BDF8]/50'
                  : 'bg-[#14161B] border-[#2A303D] hover:border-[#38BDF8]/40 hover:bg-[#181C24]'
              }`}
            >
              <div className="flex items-start justify-between gap-1">
                <span className="font-bold text-white text-xs block leading-tight line-clamp-2">
                  {zone.name}
                </span>
                {isSelected && (
                  <CheckCircle className="w-3.5 h-3.5 text-[#38BDF8] flex-shrink-0" />
                )}
              </div>

              <div className="space-y-1 pt-1 border-t border-[#2A303D]/60 text-[11px]">
                <div className="text-[#8E95A5] truncate">{zone.disasterType}</div>
                <div className="text-[#8E95A5] text-[10px] truncate">{zone.stateRegion}</div>
              </div>

              <div className="flex items-center justify-between pt-1">
                <span
                  className="px-1.5 py-0.5 rounded text-[9px] font-bold uppercase border"
                  style={{ backgroundColor: `${riskColor}20`, color: riskColor, borderColor: `${riskColor}40` }}
                >
                  {zone.riskLevel}
                </span>
                <span className="font-bold text-xs text-white">
                  {zone.confidencePercentage}%
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
