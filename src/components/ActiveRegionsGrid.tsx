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

      {allZones.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-10 text-center space-y-2 font-mono">
          <Compass className="w-8 h-8 text-[#2A303D]" />
          <p className="text-sm text-[#8E95A5]">No hazard regions loaded yet.</p>
          <p className="text-xs text-[#8E95A5]/70">Waiting for live or demo data to arrive.</p>
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3 font-mono">
          {allZones.map((zone) => {
            const isSelected = selectedZone?.id === zone.id;
            let riskColor = '#10B981';
            if (zone.riskLevel === 'High') riskColor = '#E05A32';
            else if (zone.riskLevel === 'Medium') riskColor = '#F59E0B';

            return (
              <button
                key={zone.id}
                type="button"
                onClick={() => onSelectZone(zone)}
                aria-pressed={isSelected}
                aria-label={`${zone.name}, ${zone.disasterType}, ${zone.riskLevel} risk, ${zone.confidencePercentage}% confidence${zone.isLive ? ', live data' : ''}`}
                className={`text-left p-3.5 rounded-xl cursor-pointer transition-all flex flex-col justify-between h-full min-h-[140px] space-y-2 border relative overflow-hidden ${
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

                {zone.isLive === true && (
                  <span className="inline-flex items-center gap-1 px-1.5 py-0.5 rounded text-[9px] font-bold uppercase bg-[#10B981]/20 text-[#10B981] border border-[#10B981]/40 w-fit">
                    <span className="w-1.5 h-1.5 rounded-full bg-[#10B981] animate-pulse" />
                    LIVE
                  </span>
                )}

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
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
};