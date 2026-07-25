import React, { useState } from 'react';
import { X, AlertTriangle, CheckCircle2, Radio, Users, MapPin } from 'lucide-react';
import type { HazardZone } from '../services/api';

interface CitizenAlertModalProps {
  isOpen: boolean;
  onClose: () => void;
  selectedZone: HazardZone | null;
}

export const CitizenAlertModal: React.FC<CitizenAlertModalProps> = ({
  isOpen,
  onClose,
  selectedZone,
}) => {
  // Mode controls which SECTION is visible and alerted
  // 'all'      → Origin section shown + Hotspot list shown (both alerted)
  // 'origin'   → Only Origin section shown, Hotspot list hidden
  // 'hotspots' → Origin section hidden, Hotspot list shown only
  const [alertTargetMode, setAlertTargetMode] = useState<'all' | 'origin' | 'hotspots'>('all');

  const [channels, setChannels] = useState({
    cellBroadcast: true,
    emergencySms: true,
    pushNotification: true,
    sirenNetwork: true,
  });

  const [alertMessage, setAlertMessage] = useState('');
  const [isDispatched, setIsDispatched] = useState(false);

  if (!isOpen || !selectedZone) return null;

  const hotspots = selectedZone.socialGatheringHotspots ?? [];

  // Derived booleans that control which sections render
  const showOrigin   = alertTargetMode === 'all' || alertTargetMode === 'origin';
  const showHotspots = alertTargetMode === 'all' || alertTargetMode === 'hotspots';

  // Dispatch summary line changes based on mode
  const dispatchSummary =
    alertTargetMode === 'all'
      ? `Origin (${selectedZone.targetTownVillage}) + ${hotspots.length} surrounding Social Gathering Venues`
      : alertTargetMode === 'origin'
      ? `Primary Origin only — ${selectedZone.targetTownVillage}`
      : `${hotspots.length} Surrounding Social Gathering Venues (Bazars, Malls, Parks, Transit)`;

  const defaultMsg =
    alertTargetMode === 'origin'
      ? `EMERGENCY ALERT [${selectedZone.riskLevel.toUpperCase()} RISK]: Critical ${selectedZone.disasterType} threat at ${selectedZone.targetTownVillage} — Focal Coords: ${selectedZone.coordinates[0].toFixed(4)}° N, ${selectedZone.coordinates[1].toFixed(4)}° E. Evacuate immediately.`
      : alertTargetMode === 'hotspots'
      ? `HIGH-DENSITY AREA ALERT: Emergency ${selectedZone.disasterType} imminent near ${selectedZone.targetTownVillage}. All Bazars, Malls, Parks & Transit Hubs in the area — please clear crowd & follow emergency directives immediately.`
      : `EMERGENCY ALERT [${selectedZone.riskLevel.toUpperCase()} RISK]: Critical ${selectedZone.disasterType} at ${selectedZone.targetTownVillage} — Focal Coords: ${selectedZone.coordinates[0].toFixed(4)}° N, ${selectedZone.coordinates[1].toFixed(4)}° E. Evacuate & PA Siren alerts active at all surrounding Bazars, Malls, Parks & Transit Hubs.`;

  const handleDispatch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsDispatched(true);
    setTimeout(() => {
      setIsDispatched(false);
      onClose();
    }, 2200);
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/85 backdrop-blur-md animate-fadeIn">
      <div className="glass-panel-accent border border-rose-500/50 rounded-2xl w-full max-w-xl overflow-hidden shadow-2xl">

        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-command-border/50 bg-rose-950/40">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-[#E05A32] animate-bounce" />
            <h3 className="text-sm font-bold text-white font-mono uppercase tracking-wider">
              DISASTER MANAGEMENT CITIZEN ALERT ENGINE
            </h3>
          </div>
          <button onClick={onClose} className="text-command-muted hover:text-white p-1 transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Content Body */}
        {isDispatched ? (
          <div className="p-8 text-center space-y-3 font-mono text-xs">
            <CheckCircle2 className="w-12 h-12 text-[#10B981] mx-auto animate-bounce" />
            <div className="text-base font-bold text-white uppercase font-mono">EMERGENCY ALERTS TRANSMITTED!</div>
            <p className="text-[#10B981] text-[11px] leading-relaxed">
              Alert dispatched to: {dispatchSummary}
            </p>
          </div>
        ) : (
          <form onSubmit={handleDispatch} className="p-6 space-y-4 font-sans text-xs max-h-[85vh] overflow-y-auto">

            {/* ── STEP 1: Select Scope Strategy ── */}
            <div className="space-y-2 font-mono">
              <label className="block text-[11px] text-[#8E95A5] uppercase font-bold">
                1. Select Alert Scope — Choose what gets alerted
              </label>
              <div className="grid grid-cols-3 gap-2 text-[10px]">

                {/* Origin + All Hotspots */}
                <button
                  type="button"
                  onClick={() => setAlertTargetMode('all')}
                  className={`p-3 rounded-xl border text-center transition-all space-y-1 ${
                    alertTargetMode === 'all'
                      ? 'bg-[#E05A32]/20 border-[#E05A32] text-white'
                      : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5] hover:border-[#E05A32]/40'
                  }`}
                >
                  <div className="text-base">🚨</div>
                  <div className="font-bold text-[10px] leading-tight">Origin + All Hotspots</div>
                  <div className="text-[8px] text-[#8E95A5] leading-tight">Both areas alerted</div>
                </button>

                {/* Primary Origin Only */}
                <button
                  type="button"
                  onClick={() => setAlertTargetMode('origin')}
                  className={`p-3 rounded-xl border text-center transition-all space-y-1 ${
                    alertTargetMode === 'origin'
                      ? 'bg-[#38BDF8]/20 border-[#38BDF8] text-white'
                      : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5] hover:border-[#38BDF8]/40'
                  }`}
                >
                  <div className="text-base">📍</div>
                  <div className="font-bold text-[10px] leading-tight">Primary Origin Only</div>
                  <div className="text-[8px] text-[#8E95A5] leading-tight">Hazard focal point</div>
                </button>

                {/* Social Hotspots Only */}
                <button
                  type="button"
                  onClick={() => setAlertTargetMode('hotspots')}
                  className={`p-3 rounded-xl border text-center transition-all space-y-1 ${
                    alertTargetMode === 'hotspots'
                      ? 'bg-[#F59E0B]/20 border-[#F59E0B] text-white'
                      : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5] hover:border-[#F59E0B]/40'
                  }`}
                >
                  <div className="text-base">🛍️</div>
                  <div className="font-bold text-[10px] leading-tight">Social Hotspots Only</div>
                  <div className="text-[8px] text-[#8E95A5] leading-tight">Bazars, Malls, Parks</div>
                </button>
              </div>
            </div>

            {/* ── STEP 2a: Origin Section (shown when mode = 'all' or 'origin') ── */}
            {showOrigin && (
              <div className="p-3 rounded-xl bg-[#14161B] border border-[#38BDF8]/40 space-y-1 font-mono">
                <div className="flex items-center gap-1.5 text-[10px] text-[#38BDF8] font-bold uppercase mb-1">
                  <MapPin className="w-3.5 h-3.5" />
                  Primary Hazard Origin — ALERT ACTIVE
                </div>
                <div className="text-sm font-bold text-white">{selectedZone.targetTownVillage}</div>
                <div className="text-[10px] font-mono text-[#38BDF8]">
                  📍 {selectedZone.coordinates[0].toFixed(4)}° N, {selectedZone.coordinates[1].toFixed(4)}° E
                </div>
                <div className="text-[10px] text-[#8E95A5]">
                  {selectedZone.subDistrictDistrict}, {selectedZone.stateRegion} • ~{selectedZone.affectedPopulationEstimate}
                </div>
                <div className="flex items-center justify-end mt-1">
                  <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-[#E05A32] text-white animate-pulse">
                    {selectedZone.riskLevel.toUpperCase()} THREAT — BROADCASTING
                  </span>
                </div>
              </div>
            )}

            {/* ── STEP 2b: Social Gathering Hotspots (shown when mode = 'all' or 'hotspots') ── */}
            {showHotspots && hotspots.length > 0 && (
              <div className="space-y-2 bg-[#14161B] p-3 rounded-xl border border-[#F59E0B]/40 font-mono">
                <div className="flex items-center justify-between text-[11px]">
                  <span className="font-bold text-[#F59E0B] uppercase flex items-center gap-1.5">
                    <Users className="w-4 h-4" />
                    Surrounding Social Gathering Places — ALERT ACTIVE
                  </span>
                  <span className="text-[10px] text-[#F59E0B] font-bold">
                    {hotspots.length} Venues
                  </span>
                </div>

                <div className="space-y-1.5 max-h-[200px] overflow-y-auto pr-1">
                  {hotspots.map((hotspot) => (
                    <div
                      key={hotspot.id}
                      className="p-2 rounded-lg border bg-[#181C24] border-[#F59E0B]/40 text-white"
                    >
                      <div className="flex items-start justify-between">
                        <div>
                          <span className="font-bold block text-xs">{hotspot.name}</span>
                          <span className="text-[9px] text-[#8E95A5]">
                            {hotspot.category} • {hotspot.distanceKm} km away • {hotspot.peakCrowdEstimate}
                          </span>
                        </div>
                        <span className="px-2 py-0.5 rounded text-[9px] font-bold bg-[#F59E0B] text-black whitespace-nowrap ml-2">
                          ALERT ACTIVE
                        </span>
                      </div>
                      <div className="text-[9px] text-[#8E95A5] leading-tight pt-1 border-t border-[#2A303D]/60 mt-1">
                        <strong className="text-[#E05A32]">Directive:</strong> {hotspot.evacuationDirective}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* ── STEP 3: Transmission Channels ── */}
            <div>
              <label className="block text-[11px] font-mono text-[#8E95A5] uppercase mb-1.5 font-bold">
                2. Select Transmission Channels
              </label>
              <div className="grid grid-cols-2 gap-2 text-[11px] font-mono">
                <button
                  type="button"
                  onClick={() => setChannels(p => ({ ...p, cellBroadcast: !p.cellBroadcast }))}
                  className={`p-2 rounded-lg border text-left flex items-center justify-between transition-all ${
                    channels.cellBroadcast ? 'bg-[#E05A32]/20 border-[#E05A32] text-white font-bold' : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5]'
                  }`}
                >
                  <span>📡 Cell Broadcast</span>
                  <span>{channels.cellBroadcast ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setChannels(p => ({ ...p, emergencySms: !p.emergencySms }))}
                  className={`p-2 rounded-lg border text-left flex items-center justify-between transition-all ${
                    channels.emergencySms ? 'bg-[#E05A32]/20 border-[#E05A32] text-white font-bold' : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5]'
                  }`}
                >
                  <span>📱 Mass SMS</span>
                  <span>{channels.emergencySms ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setChannels(p => ({ ...p, pushNotification: !p.pushNotification }))}
                  className={`p-2 rounded-lg border text-left flex items-center justify-between transition-all ${
                    channels.pushNotification ? 'bg-[#E05A32]/20 border-[#E05A32] text-white font-bold' : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5]'
                  }`}
                >
                  <span>🔔 Mobile Push</span>
                  <span>{channels.pushNotification ? 'ON' : 'OFF'}</span>
                </button>

                <button
                  type="button"
                  onClick={() => setChannels(p => ({ ...p, sirenNetwork: !p.sirenNetwork }))}
                  className={`p-2 rounded-lg border text-left flex items-center justify-between transition-all ${
                    channels.sirenNetwork ? 'bg-[#E05A32]/20 border-[#E05A32] text-white font-bold' : 'bg-[#14161B] border-[#2A303D] text-[#8E95A5]'
                  }`}
                >
                  <span>🚨 Market / Mall Sirens</span>
                  <span>{channels.sirenNetwork ? 'ON' : 'OFF'}</span>
                </button>
              </div>
            </div>

            {/* Broadcast Message */}
            <div>
              <label className="block text-[11px] font-mono text-[#8E95A5] uppercase mb-1 font-bold">
                Emergency Broadcast Directive Text
              </label>
              <textarea
                rows={3}
                value={alertMessage || defaultMsg}
                onChange={(e) => setAlertMessage(e.target.value)}
                className="w-full bg-[#14161B] border border-[#E05A32]/40 rounded-xl px-3 py-2 text-white font-mono text-xs focus:outline-none focus:border-[#E05A32]"
              />
            </div>

            {/* Submit */}
            <div className="pt-2">
              <button
                type="submit"
                className="w-full py-3 bg-[#E05A32] hover:bg-[#c94e2a] text-white font-mono text-xs font-bold rounded-xl border border-[#E05A32] shadow-lg transition-all flex items-center justify-center space-x-2"
              >
                <Radio className="w-4 h-4 text-white animate-pulse" />
                <span>CONFIRM & TRANSMIT CITIZEN ALERTS</span>
              </button>
            </div>
          </form>
        )}
      </div>
    </div>
  );
};
