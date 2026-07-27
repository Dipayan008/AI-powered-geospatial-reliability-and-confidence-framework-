import React from 'react';
import { X, Navigation, AlertTriangle, ShieldAlert, Crosshair, ArrowRight } from 'lucide-react';
import type { UserLocationHazardAssessment, HazardZone } from '../services/api';

interface InitialGeolocationAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  assessment: UserLocationHazardAssessment | null;
  onInspectHazard: (zone: HazardZone) => void;
}

export const InitialGeolocationAlertModal: React.FC<InitialGeolocationAlertModalProps> = ({
  isOpen,
  onClose,
  assessment,
  onInspectHazard,
}) => {
  if (!isOpen || !assessment) return null;

  const { nearestHazard, userLat, userLng, distanceKm, isDangerDetected, locationName } = assessment;

  const handleInspect = () => {
    onInspectHazard(nearestHazard);
    onClose();
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel-accent border border-rose-500/60 rounded-2xl w-full max-w-lg overflow-hidden shadow-2xl">
        {/* Header Bar */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-command-border/50 bg-rose-950/40">
          <div className="flex items-center space-x-2.5">
            <div className="p-1.5 rounded-lg bg-cyber-rose/20 border border-cyber-rose/40 text-cyber-rose shadow-glow-rose">
              <ShieldAlert className="w-5 h-5 animate-bounce" />
            </div>
            <div>
              <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
                AUTOMATIC GEOLOCATION HAZARD ALERT
              </h3>
              <span className="text-[10px] text-cyber-rose font-mono">
                Initial Load Surrounding Zone Assessment
              </span>
            </div>
          </div>
          <button onClick={onClose} className="text-command-muted hover:text-white p-1 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Modal Body */}
        <div className="p-6 space-y-4 font-sans text-xs">
          {/* User Coordinates Badge */}
          <div className="p-3 rounded-xl bg-command-obsidian border border-cyber-purple/40 flex items-center justify-between text-mono">
            <div className="flex items-center space-x-2 text-cyber-neonViolet">
              <Navigation className="w-4 h-4 animate-pulse" />
              <span className="font-bold text-xs">{locationName}</span>
            </div>
            <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-cyber-purple/20 text-cyber-neonViolet border border-cyber-purple/40 rounded">
              {userLat}°N, {userLng}°E
            </span>
          </div>

          {/* Threat Banner */}
          <div className={`p-4 rounded-xl border space-y-2 ${
            isDangerDetected
              ? 'bg-cyber-rose/10 border-cyber-rose/50 text-white'
              : 'bg-cyber-amber/10 border-cyber-amber/50 text-white'
          }`}>
            <div className="flex items-center justify-between font-mono">
              <span className="text-xs font-bold text-cyber-rose uppercase flex items-center gap-1.5">
                <AlertTriangle className="w-4 h-4 text-cyber-rose" />
                SURROUNDING ZONE HAZARD DETECTED
              </span>
              <span className="px-2 py-0.5 text-[10px] font-bold bg-cyber-rose/20 text-cyber-rose border border-cyber-rose/40 rounded">
                {nearestHazard.riskLevel.toUpperCase()} RISK
              </span>
            </div>

            <div className="text-sm font-bold text-white font-mono">{nearestHazard.name}</div>
            <p className="text-[11px] text-gray-300 font-sans">
              Proximity: <strong className="text-white font-mono">~{distanceKm} km away</strong> from your detected position. Threat Type: <strong className="text-cyber-neonViolet font-mono">{nearestHazard.disasterType}</strong>.
            </p>
          </div>

          {/* Driver & Pattern Match Breakdown */}
          <div className="bg-command-obsidian p-3 rounded-xl border border-command-border/50 space-y-1.5 font-mono text-[11px]">
            <div className="flex justify-between text-gray-300">
              <span className="text-command-muted">Pattern Match Score:</span>
              <span className="text-cyber-rose font-bold">{nearestHazard.confidencePercentage}% Confidence</span>
            </div>
            <div className="flex justify-between text-gray-300">
              <span className="text-command-muted">Primary Anomaly Driver:</span>
              <span className="text-cyber-neonViolet font-semibold truncate max-w-[60%]">{nearestHazard.primaryAnomalyDriver}</span>
            </div>
            <div className="flex justify-between text-gray-300">
              <span className="text-command-muted">Historical Baseline:</span>
              <span className="text-white truncate max-w-[60%]">{nearestHazard.historicalPatternMatch}</span>
            </div>
          </div>

          {/* Operational Action Buttons */}
          <div className="pt-2 flex flex-col sm:flex-row items-center gap-2 font-mono">
            <button
              onClick={handleInspect}
              className="flex-1 w-full py-2.5 bg-gradient-to-r from-purple-700 to-indigo-600 hover:from-purple-600 hover:to-indigo-500 text-white font-mono text-xs font-bold rounded-xl border border-cyber-purple/60 shadow-glow-purple transition-all flex items-center justify-center space-x-2"
            >
              <Crosshair className="w-4 h-4 text-white" />
              <span>INSPECT HAZARD & FOCUS MAP</span>
              <ArrowRight className="w-3.5 h-3.5" />
            </button>

            <button
              onClick={onClose}
              className="w-full sm:w-auto px-4 py-2.5 bg-command-obsidian hover:bg-command-surface text-command-muted hover:text-white border border-command-border/50 font-mono text-xs rounded-xl transition-all"
            >
              ACKNOWLEDGE
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};
