import React, { useCallback, useEffect, useState } from 'react';
import { Radio, RefreshCw } from 'lucide-react';
import { fetchRawInsights, type BackendInsight } from '../services/api';

function loggedTimeAgo(iso: string): string {
  const diffMs = Date.now() - new Date(iso).getTime();
  const diffSec = Math.round(diffMs / 1000);
  if (diffSec < 5) return 'just now';
  if (diffSec < 60) return `${diffSec}s ago`;
  const diffMin = Math.round(diffSec / 60);
  if (diffMin < 60) return `${diffMin}m ago`;
  const diffHr = Math.round(diffMin / 60);
  if (diffHr < 24) return `${diffHr}h ago`;
  return `${Math.round(diffHr / 24)}d ago`;
}

function confidenceColor(score: number): string {
  if (score >= 70) return '#E05A32';
  if (score >= 40) return '#F59E0B';
  return '#10B981';
}

const SCORING_UNAVAILABLE_PREFIX = 'AI_SCORING_UNAVAILABLE:';

function isScoringUnavailable(insight: BackendInsight): boolean {
  return insight.explanation?.startsWith(SCORING_UNAVAILABLE_PREFIX) ?? false;
}

function cleanExplanation(insight: BackendInsight): string {
  return isScoringUnavailable(insight)
    ? insight.explanation.replace(SCORING_UNAVAILABLE_PREFIX, '').trim()
    : insight.explanation;
}

function locationLabel(insight: BackendInsight): string {
  const parts = [insight.town_village, insight.district, insight.state].filter(
    (p): p is string => Boolean(p)
  );
  return parts.length > 0 ? parts.join(', ') : 'Location not reverse-geocoded';
}

const POLL_INTERVAL_MS = 20_000;

export const LiveInsightFeed: React.FC = () => {
  const [insights, setInsights] = useState<BackendInsight[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const load = useCallback(async (isManualRefresh: boolean) => {
    if (isManualRefresh) setIsRefreshing(true);
    const data = await fetchRawInsights();
    setInsights(data);
    setLastUpdated(new Date());
    setIsLoading(false);
    if (isManualRefresh) setIsRefreshing(false);
  }, []);

  useEffect(() => {
    load(false);
    const timer = setInterval(() => load(false), POLL_INTERVAL_MS);
    return () => clearInterval(timer);
  }, [load]);

  return (
    <div className="glass-panel p-5 md:p-6 rounded-xl border border-[#2A303D] shadow-xl w-full flex flex-col">
      <div className="flex items-center justify-between border-b border-[#2A303D] pb-3 flex-wrap gap-2">
        <div className="flex items-center space-x-2 font-mono text-xs md:text-sm font-bold text-white uppercase tracking-wider">
          <Radio className="w-4 h-4 text-[#38BDF8]" />
          <span>Live Insight Feed ({insights.length})</span>
        </div>
        <button
          type="button"
          onClick={() => load(true)}
          disabled={isRefreshing}
          aria-label="Refresh live insight feed"
          className="flex items-center gap-1.5 text-xs font-mono text-[#8E95A5] hover:text-[#38BDF8] transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          {lastUpdated ? `Updated ${loggedTimeAgo(lastUpdated.toISOString())}` : 'Refresh'}
        </button>
      </div>

      <div className="mt-4 max-h-[340px] overflow-y-auto pr-1">
        {isLoading ? (
          <div role="status" aria-live="polite" className="flex items-center justify-center py-8 gap-2 text-[#8E95A5] font-mono text-xs">
            <div className="w-4 h-4 border-2 border-[#2A303D] border-t-[#38BDF8] rounded-full animate-spin" />
            Loading live feed…
          </div>
        ) : insights.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center space-y-1 font-mono">
            <p className="text-sm text-[#8E95A5]">No live insights yet.</p>
            <p className="text-xs text-[#8E95A5]/70">
              Post a source and generate an insight against the backend to see it appear here.
            </p>
          </div>
        ) : (
          <ol className="relative border-l border-[#2A303D] ml-1.5 space-y-5">
            {insights.slice(0, 20).map((insight) => {
              const unavailable = isScoringUnavailable(insight);
              const color = confidenceColor(insight.confidence_score);
              return (
                <li key={insight.id} className="ml-4">
                  <span
                    className="absolute w-2.5 h-2.5 rounded-full -left-[5px] mt-1.5 border border-[#12141C]"
                    style={{ backgroundColor: unavailable ? '#64748B' : color }}
                    aria-hidden="true"
                  />
                  <div className="flex items-start justify-between gap-2 flex-wrap">
                    <span className="font-bold text-white text-xs">{insight.title}</span>
                    <span className="text-[10px] font-mono text-[#8E95A5] whitespace-nowrap" title="When this record was added to the database — not necessarily when the underlying event occurred. Check the summary below for the event's actual date.">
                      Logged {loggedTimeAgo(insight.created_at)}
                    </span>
                  </div>
                  <div className="text-[11px] text-[#8E95A5] mt-0.5">{locationLabel(insight)}</div>
                  <div className="flex items-center gap-2 mt-1.5">
                    {unavailable ? (
                      <span className="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono uppercase border bg-[#64748B]/20 text-[#94A3B8] border-[#64748B]/40">
                        Scoring unavailable
                      </span>
                    ) : (
                      <span
                        className="px-1.5 py-0.5 rounded text-[9px] font-bold font-mono uppercase border"
                        style={{ backgroundColor: `${color}20`, color, borderColor: `${color}40` }}
                      >
                        {Math.round(insight.confidence_score)}% confidence
                      </span>
                    )}
                  </div>
                  <p className="text-[11px] text-[#8E95A5] mt-1.5 leading-relaxed line-clamp-2">
                    {cleanExplanation(insight)}
                  </p>
                </li>
              );
            })}
          </ol>
        )}
      </div>
    </div>
  );
};
