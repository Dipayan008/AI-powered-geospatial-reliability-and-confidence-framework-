import { useEffect, useState } from 'react';
import { Header } from './components/Header';
import { IndiaHazardMap } from './components/IndiaHazardMap';
import { PatternConfidenceScorecard } from './components/PatternConfidenceScorecard';
import { XAIPatternRecognitionPanel } from './components/XAIPatternRecognitionPanel';
import { ActiveRegionsGrid } from './components/ActiveRegionsGrid';
import { LiveInsightFeed } from './components/LiveInsightFeed';
import { CitizenAlertModal } from './components/CitizenAlertModal';
import { InitialGeolocationAlertModal } from './components/InitialGeolocationAlertModal';
import type { HazardZone, UserLocationHazardAssessment } from './services/api';
import { fetchAllHazardZones, detectUserLocationAndCheckSurroundingHazards, INDIA_HAZARD_ZONES } from './services/api';

export function App() {
  const [hazards, setHazards] = useState<HazardZone[]>([]);
  const [selectedZone, setSelectedZone] = useState<HazardZone | null>(null);
  const [isAlertModalOpen, setIsAlertModalOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initial Geolocation Detection & Surrounding Hazard Check State
  const [geoAssessment, setGeoAssessment] = useState<UserLocationHazardAssessment | null>(null);
  const [isGeoModalOpen, setIsGeoModalOpen] = useState(false);

  useEffect(() => {
    fetchAllHazardZones()
      .then((res) => {
        setHazards(res);
        if (res.length > 0) {
          setSelectedZone(res[0]); // Default to first hazard
        }
      })
      .catch(() => {
        // Never leave the list stuck empty — always show at least the demo zones.
        setHazards(INDIA_HAZARD_ZONES);
        if (INDIA_HAZARD_ZONES.length > 0) {
          setSelectedZone(INDIA_HAZARD_ZONES[0]);
        }
      })
      .finally(() => setIsLoading(false));

    // Run Initial Geolocation Detection & Surrounding Hazard Check
    detectUserLocationAndCheckSurroundingHazards().then((assessment) => {
      setGeoAssessment(assessment);
      if (assessment.isDangerDetected) {
        setIsGeoModalOpen(true);
      }
    });
  }, []);

  const handleInspectHazardFromGeoModal = (zone: HazardZone) => {
    setSelectedZone(zone);
  };

  return (
    <div className="min-h-screen bg-command-bg text-command-text font-sans flex flex-col selection:bg-cyber-purple selection:text-white">
      {/* Top Command Header */}
      <Header
        activeHazardsCount={hazards.length}
        selectedZone={selectedZone}
        onOpenAlertModal={() => setIsAlertModalOpen(true)}
      />

      {/* Main Responsive Vertical Layout with Map on Top */}
      <main className="flex-1 px-4 sm:px-8 md:px-12 py-6 max-w-[1750px] mx-auto w-full flex flex-col space-y-8">
        {isLoading ? (
          <div
            role="status"
            aria-live="polite"
            className="flex-1 min-h-[400px] flex flex-col items-center justify-center gap-3 font-mono text-[#8E95A5]"
          >
            <div className="w-10 h-10 border-2 border-[#2A303D] border-t-[#38BDF8] rounded-full animate-spin" />
            <span className="text-xs uppercase tracking-wider">Initializing Telemetry Feed…</span>
          </div>
        ) : (
        <>
        {/* Top Primary Section: India Geospatial Hazard Map */}
        <section className="w-full h-[380px] md:h-[420px] lg:h-[450px] flex flex-col">
          <IndiaHazardMap
            hazards={hazards}
            selectedZone={selectedZone}
            onSelectZone={(zone) => setSelectedZone(zone)}
            onOpenAlertModal={() => setIsAlertModalOpen(true)}
          />
        </section>

        {/* Bottom Details Section: Telemetry, AI Scorecard & XAI Analysis Panels */}
        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full items-start">
          {/* Left Column: AI Pattern Confidence & Telemetry Scorecard */}
          <div className="w-full">
            <PatternConfidenceScorecard selectedZone={selectedZone} />
          </div>

          {/* Right Column: Explainable AI Pattern Recognition Panel */}
          <div className="w-full">
            <XAIPatternRecognitionPanel selectedZone={selectedZone} />
          </div>
        </section>

        {/* Live Insight Feed: real backend-scored insights, most recent first */}
        <section className="w-full">
          <LiveInsightFeed />
        </section>

        {/* Full-Width Bottom Section: Active Monitored Hazard Regions Grid */}
        <section className="w-full">
          <ActiveRegionsGrid
            allZones={hazards}
            selectedZone={selectedZone}
            onSelectZone={(zone) => setSelectedZone(zone)}
          />
        </section>
        </>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-command-border/40 py-3 px-6 bg-command-surface/80 text-[11px] font-mono text-command-muted flex flex-wrap items-center justify-between gap-2 mt-6">
        <div className="flex items-center space-x-2">
          <span className="text-cyber-neonViolet font-bold">PS07 INDIA HAZARD AI PATTERN MATRIX</span>
          <span>•</span>
          <span className="text-cyber-emerald">Automatic Geolocation Hazard Assessment Active</span>
        </div>
        <div>
          <span>Geospatial Hazard Control & Telemetry System</span>
        </div>
      </footer>

      {/* Citizen Alert Modal */}
      <CitizenAlertModal
        isOpen={isAlertModalOpen}
        onClose={() => setIsAlertModalOpen(false)}
        selectedZone={selectedZone}
      />

      {/* Initial Geolocation Hazard Alert Modal */}
      <InitialGeolocationAlertModal
        isOpen={isGeoModalOpen}
        onClose={() => setIsGeoModalOpen(false)}
        assessment={geoAssessment}
        onInspectHazard={handleInspectHazardFromGeoModal}
      />
    </div>
  );
}

export default App;