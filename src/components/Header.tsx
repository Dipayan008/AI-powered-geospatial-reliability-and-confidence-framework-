import React, { useState, useEffect } from 'react';
import { Activity, Radio, Clock, AlertTriangle } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface HeaderProps {
  activeHazardsCount: number;
  selectedZone: HazardZone | null;
  onOpenAlertModal: () => void;
}

export const Header: React.FC<HeaderProps> = ({
  activeHazardsCount,
  selectedZone,
  onOpenAlertModal,
}) => {
  const [timeStr, setTimeStr] = useState<string>('');

  useEffect(() => {
    const updateTime = () => {
      const now = new Date();
      // toISOString() is always UTC — the label said "IST" but the value
      // wasn't actually offset, so it ran 5.5 hours behind real IST.
      // Format directly in Asia/Kolkata instead of hand-rolling the offset.
      const parts = new Intl.DateTimeFormat('en-CA', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric', month: '2-digit', day: '2-digit',
        hour: '2-digit', minute: '2-digit', second: '2-digit',
        hour12: false,
      }).formatToParts(now);
      const get = (type: string) => parts.find((p) => p.type === type)?.value ?? '';
      setTimeStr(
        `${get('year')}-${get('month')}-${get('day')} ${get('hour')}:${get('minute')}:${get('second')} IST`
      );
    };
    updateTime();
    const timer = setInterval(updateTime, 1000);
    return () => clearInterval(timer);
  }, []);

  return (
    <header className="glass-panel-accent border-b border-[#2A303D] px-6 py-4 flex flex-wrap items-center justify-between gap-4 select-none sticky top-0 z-50">
      {/* Brand Title */}
      <div className="flex items-center space-x-3">
        <div>
          <div className="flex items-center space-x-2">
            <h1 className="text-base font-bold tracking-tight text-white font-mono uppercase">
              INDIA GEOSPATIAL <span className="text-[#38BDF8]">// TELEMETRY CONTROL CENTER</span>
            </h1>
          </div>
          <p className="text-xs text-[#8E95A5] font-sans">
            Advanced geospatial tracking and hazard confidence metrics
          </p>
        </div>
      </div>

      {/* Center Ticker / Status Indicators */}
      <div className="hidden xl:flex items-center space-x-6 text-xs font-mono bg-[#14161B] px-4 py-2 rounded-lg border border-[#2A303D]">
        <div className="flex items-center space-x-2">
          <Activity className="w-4 h-4 text-[#38BDF8]" />
          <span className="text-[#8E95A5]">MONITORED ZONES:</span>
          <span className="text-white font-bold">{activeHazardsCount} REGIONS</span>
        </div>

        <div className="h-3.5 w-px bg-[#2A303D]" />

        <div className="flex items-center space-x-2">
          <Radio className="w-4 h-4 text-[#10B981]" />
          <span className="text-[#8E95A5]">SYSTEM STATUS:</span>
          <span className="text-[#10B981] font-bold">ONLINE</span>
        </div>
      </div>

      {/* Right Controls */}
      <div className="flex items-center space-x-3">
        <div className="hidden sm:flex items-center space-x-2 px-3 py-2 bg-[#14161B] rounded-lg border border-[#2A303D] text-xs font-mono text-white">
          <Clock className="w-4 h-4 text-[#8E95A5]" />
          <span>{timeStr || '2026-07-25 14:30:00 IST'}</span>
        </div>

        <button
          onClick={onOpenAlertModal}
          className="flex items-center space-x-2 px-4 py-2 bg-[#E05A32] hover:bg-[#c94e2a] text-white font-mono text-xs font-bold rounded-lg transition-all shadow-md"
        >
          <AlertTriangle className="w-4 h-4 text-white" />
          <span>ISSUE ALERT {selectedZone ? `[${selectedZone.riskLevel}]` : ''}</span>
        </button>
      </div>
    </header>
  );
};

