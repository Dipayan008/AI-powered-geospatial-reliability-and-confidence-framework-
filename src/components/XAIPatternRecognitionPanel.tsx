import React from 'react';
import { Brain, Sparkles, CheckCircle2, FileSearch, Layers, MapPin } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface XAIPatternRecognitionPanelProps {
  selectedZone: HazardZone | null;
}

export const XAIPatternRecognitionPanel: React.FC<XAIPatternRecognitionPanelProps> = ({
  selectedZone,
}) => {
  if (!selectedZone) return null;

  return (
    <div className="glass-panel p-6 md:p-7 rounded-xl border border-[#2A303D] space-y-5 flex flex-col shadow-xl">
      {/* Panel Header */}
      <div className="flex items-center justify-between border-b border-[#2A303D] pb-4">
        <div className="flex items-center space-x-2.5">
          <Brain className="w-5 h-5 text-[#38BDF8]" />
          <h2 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
            EXPLAINABLE AI RECOGNITION PANEL
          </h2>
        </div>
      </div>

      {/* Primary Pattern Matching Explanation Box */}
      <div className="glass-panel-accent p-4 md:p-5 rounded-xl border border-[#2A303D] space-y-3">
        <div className="flex items-center justify-between font-mono text-xs flex-wrap gap-2">
          <span className="text-[#38BDF8] font-bold flex items-center gap-2 uppercase text-xs md:text-sm">
            <Sparkles className="w-4.5 h-4.5 text-[#38BDF8]" />
            AI Rationale: Why Area is Flagged
          </span>
          <span className="text-[#10B981] font-bold text-xs bg-[#10B981]/10 px-2 py-0.5 rounded border border-[#10B981]/30">
            {selectedZone.confidencePercentage}% AGREEMENT
          </span>
        </div>

        <p className="text-xs md:text-sm text-[#F4F5F7] leading-relaxed font-sans bg-[#12141C] p-4 rounded-xl border border-[#2A303D]">
          "{selectedZone.xaiReasoning}"
        </p>
      </div>

      {/* Maximum Impact Focal Coordinates Banner */}
      <div className="p-4 rounded-xl bg-[#14161B] border border-[#38BDF8]/40 space-y-2 font-mono">
        <div className="flex items-center justify-between flex-wrap gap-2">
          <span className="text-xs text-[#38BDF8] font-bold uppercase flex items-center gap-1.5">
            <MapPin className="w-4 h-4 text-[#38BDF8]" />
            FOCAL DANGER COORDINATES
          </span>
          <span className="text-xs text-white font-bold bg-[#1D212A] px-2.5 py-1 rounded border border-[#2A303D]">
            {selectedZone.coordinates[0].toFixed(4)}° N, {selectedZone.coordinates[1].toFixed(4)}° E
          </span>
        </div>
        <p className="text-xs md:text-sm text-[#8E95A5] leading-relaxed pt-1.5 border-t border-[#2A303D]">
          Priority evacuation notice targeting citizens at epicenter: <strong className="text-white">{selectedZone.epicenterFocalPoint}</strong>
        </p>
      </div>

      {/* Detailed Spatial Pattern Correlations & Drivers */}
      <div className="space-y-3">
        <div className="text-xs font-mono text-white uppercase font-bold flex items-center gap-2">
          <Layers className="w-4 h-4 text-[#38BDF8]" />
          <span>Matched Spatial Pattern Drivers</span>
        </div>

        <div className="space-y-3 text-xs md:text-sm font-sans">
          {/* Driver 1 */}
          <div className="p-3.5 rounded-xl bg-[#181C24] border border-[#2A303D] flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-[#10B981] flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-mono font-bold text-white text-xs md:text-sm uppercase block">
                1. Spaceborne SAR Anomaly Signature
              </span>
              <p className="text-[#8E95A5] text-xs md:text-sm leading-relaxed">
                {selectedZone.satelliteRadarSig}
              </p>
            </div>
          </div>

          {/* Driver 2 */}
          <div className="p-3.5 rounded-xl bg-[#181C24] border border-[#2A303D] flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-[#38BDF8] flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-mono font-bold text-white text-xs md:text-sm uppercase block">
                2. Meteorological Radar Correlation
              </span>
              <p className="text-[#8E95A5] text-xs md:text-sm leading-relaxed">
                {selectedZone.weatherCorrelation}
              </p>
            </div>
          </div>

          {/* Driver 3 */}
          <div className="p-3.5 rounded-xl bg-[#181C24] border border-[#2A303D] flex items-start space-x-3">
            <CheckCircle2 className="w-5 h-5 text-[#F59E0B] flex-shrink-0 mt-0.5" />
            <div className="space-y-1">
              <span className="font-mono font-bold text-white text-xs md:text-sm uppercase block">
                3. OpenStreetMap Topography & Slope Angle
              </span>
              <p className="text-[#8E95A5] text-xs md:text-sm leading-relaxed">
                {selectedZone.topographyFactor}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Historical Pattern Precedent Card */}
      <div className="bg-[#181C24] p-4 rounded-xl border border-[#2A303D] flex items-start space-x-3">
        <FileSearch className="w-5 h-5 text-[#38BDF8] flex-shrink-0 mt-0.5" />
        <div className="space-y-1">
          <span className="text-xs font-mono font-bold text-[#38BDF8] uppercase block">
            HISTORICAL PATTERN PRECEDENT MATCH
          </span>
          <p className="text-xs md:text-sm font-mono text-white">
            {selectedZone.historicalPatternMatch}
          </p>
        </div>
      </div>
    </div>
  );
};

