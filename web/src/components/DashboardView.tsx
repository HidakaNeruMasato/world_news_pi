import React, { useState, useEffect } from 'react';
import {
  fetchDashboardSummary,
  fetchDashboardFunnel,
  fetchDashboardRegions,
  fetchDashboardSources,
  fetchDashboardTimeseries,
  fetchDashboardHealth,
  DashboardSummary,
  FunnelMetrics,
  RegionalActivity,
  SourceMetric,
  TimeSeriesPoint,
  SourceHealth
} from '../api/dashboardClient';
import { Radio, Newspaper, Flame, MapPin, Activity, CheckCircle, AlertCircle, Info, ChevronRight } from 'lucide-react';

interface DashboardViewProps {
  onSelectRegion: (region: string) => void;
}

export const DashboardView: React.FC<DashboardViewProps> = ({ onSelectRegion }) => {
  const [period, setPeriod] = useState<string>('24h');
  const [loading, setLoading] = useState<boolean>(true);
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [funnel, setFunnel] = useState<FunnelMetrics | null>(null);
  const [regions, setRegions] = useState<RegionalActivity[]>([]);
  const [sources, setSources] = useState<SourceMetric[]>([]);
  const [timeseries, setTimeseries] = useState<TimeSeriesPoint[]>([]);
  const [health, setHealth] = useState<SourceHealth | null>(null);

  useEffect(() => {
    let isMounted = true;
    setLoading(true);

    Promise.all([
      fetchDashboardSummary(period),
      fetchDashboardFunnel(period),
      fetchDashboardRegions(period),
      fetchDashboardSources(period),
      fetchDashboardTimeseries(period),
      fetchDashboardHealth()
    ])
      .then(([sumData, funnelData, regData, srcData, tsData, healthData]) => {
        if (!isMounted) return;
        setSummary(sumData);
        setFunnel(funnelData);
        setRegions(regData);
        setSources(srcData);
        setTimeseries(tsData);
        setHealth(healthData);
      })
      .catch((err) => console.error('Error fetching dashboard data:', err))
      .finally(() => {
        if (isMounted) setLoading(false);
      });

    return () => {
      isMounted = false;
    };
  }, [period]);

  const maxRegionEvents = Math.max(...regions.map((r) => r.map_events), 1);

  return (
    <div className="flex-1 bg-slate-950 text-slate-100 overflow-y-auto p-4 md:p-6 space-y-6">
      {/* Top Header Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-slate-800 pb-4">
        <div>
          <h1 className="text-xl md:text-2xl font-bold flex items-center gap-2 text-white">
            <Activity className="w-6 h-6 text-sky-400" />
            World News Activity & Pipeline Dashboard
          </h1>
          <p className="text-xs md:text-sm text-slate-400 mt-1">
            RSS入力・パイプライン削減工程・地域別ニュース発生量の可視化
          </p>
        </div>

        <div className="flex items-center space-x-2 bg-slate-900 border border-slate-800 rounded-lg p-1 text-xs">
          <span className="text-slate-400 px-2 font-medium">Period:</span>
          {['24h', '48h', '7d'].map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-3 py-1.5 rounded-md font-semibold transition ${
                period === p ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              {p.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Explanatory Notice Banner */}
      <div className="bg-sky-950/40 border border-sky-800/60 rounded-xl p-3 md:p-4 text-xs md:text-sm text-sky-200 flex items-start space-x-3">
        <Info className="w-5 h-5 text-sky-400 flex-shrink-0 mt-0.5" />
        <div>
          <span className="font-semibold text-sky-100">ニュース発生集計に関するご注意：</span>
          <span className="text-sky-300">
            本ダッシュボードの表示数値は、World News Map が現在監視している RSS ソース（
            {summary?.rss_sources || 0} 媒体）に基づく実測集計です。数が少ない地域であっても、必ずしも現地での現実の発生ニュースが少ないことを意味するものではありません。
          </span>
        </div>
      </div>

      {loading ? (
        <div className="flex items-center justify-center py-20 space-x-3">
          <div className="w-8 h-8 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
          <span className="text-slate-400 text-sm font-medium">Loading Dashboard Analytics...</span>
        </div>
      ) : (
        <>
          {/* Top 4 KPI Cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 md:gap-4">
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold uppercase tracking-wider">RSS Sources</span>
                <Radio className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-2xl md:text-3xl font-bold text-white">{summary?.rss_sources || 0}</span>
                <span className="text-xs text-emerald-400 font-medium flex items-center">
                  <CheckCircle className="w-3 h-3 mr-1" /> Active
                </span>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold uppercase tracking-wider">New Articles</span>
                <Newspaper className="w-4 h-4 text-sky-400" />
              </div>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-2xl md:text-3xl font-bold text-white">
                  {(summary?.new_articles || 0).toLocaleString()}
                </span>
                <span className="text-xs text-slate-400">~{(summary?.rss_items || 0).toLocaleString()} items</span>
              </div>
            </div>

            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 flex flex-col justify-between shadow-sm">
              <div className="flex items-center justify-between text-slate-400">
                <span className="text-xs font-semibold uppercase tracking-wider">LLM Events</span>
                <Flame className="w-4 h-4 text-amber-400" />
              </div>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-2xl md:text-3xl font-bold text-white">
                  {(summary?.event_articles || 0).toLocaleString()}
                </span>
                <span className="text-xs text-amber-400 font-medium">
                  {funnel?.rates.event_rate || 0}% rate
                </span>
              </div>
            </div>

            <div className="bg-slate-900 border border-sky-900/50 rounded-xl p-4 flex flex-col justify-between shadow-sm bg-gradient-to-br from-slate-900 to-sky-950/40">
              <div className="flex items-center justify-between text-sky-300">
                <span className="text-xs font-semibold uppercase tracking-wider">Active Map Events</span>
                <MapPin className="w-4 h-4 text-sky-400" />
              </div>
              <div className="mt-2 flex items-baseline justify-between">
                <span className="text-2xl md:text-3xl font-bold text-sky-200">
                  {(summary?.map_events || 0).toLocaleString()}
                </span>
                <span className="text-xs text-sky-400 font-semibold">
                  {summary?.map_conversion_rate || 0}% Conv
                </span>
              </div>
            </div>
          </div>

          {/* Main Grid Section: Regional Activity & Pipeline Funnel */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Regional Activity Ranking & Bar Chart (2 Cols) */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 flex flex-col space-y-4">
              <div className="flex items-center justify-between border-b border-slate-800 pb-3">
                <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <MapPin className="w-5 h-5 text-sky-400" />
                  Regional News Activity ({period.toUpperCase()})
                </h2>
                <span className="text-xs text-slate-400">Click region to open Map</span>
              </div>

              <div className="space-y-3 overflow-y-auto max-h-[380px] pr-2">
                {regions.map((reg) => {
                  const pct = Math.round((reg.map_events / maxRegionEvents) * 100);
                  return (
                    <div
                      key={reg.region}
                      onClick={() => onSelectRegion(reg.region)}
                      className="group p-2.5 rounded-lg hover:bg-slate-800/80 transition cursor-pointer border border-transparent hover:border-slate-700 flex flex-col space-y-1.5"
                    >
                      <div className="flex items-center justify-between text-xs md:text-sm">
                        <span className="font-semibold text-slate-200 group-hover:text-sky-300 transition flex items-center">
                          {reg.region}
                          <ChevronRight className="w-3.5 h-3.5 ml-1 opacity-0 group-hover:opacity-100 transition" />
                        </span>
                        <div className="flex items-center space-x-3 text-xs">
                          <span className="text-slate-400">
                            Articles: <strong className="text-slate-300">{reg.new_articles}</strong>
                          </span>
                          <span className="text-sky-400 font-bold">
                            Map Events: {reg.map_events}
                          </span>
                        </div>
                      </div>

                      <div className="w-full bg-slate-800 h-2.5 rounded-full overflow-hidden flex">
                        <div
                          className="bg-gradient-to-r from-sky-500 to-indigo-500 h-full rounded-full transition-all duration-500"
                          style={{ width: `${Math.max(pct, reg.map_events > 0 ? 3 : 0)}%` }}
                        />
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Pipeline Funnel Reduction Visualizer (1 Col) */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 flex flex-col space-y-4">
              <div className="border-b border-slate-800 pb-3">
                <h2 className="text-base font-bold text-slate-100 flex items-center gap-2">
                  <Activity className="w-5 h-5 text-indigo-400" />
                  Pipeline Funnel Reduction
                </h2>
                <p className="text-xs text-slate-400 mt-0.5">RSS入力から地図表示までの段階的推移</p>
              </div>

              {funnel && (
                <div className="space-y-3 text-xs">
                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80 flex items-center justify-between">
                    <span className="text-slate-400">1. RSS Items Seen</span>
                    <strong className="text-slate-200 text-sm">{funnel.stages.rss_items_seen.toLocaleString()}</strong>
                  </div>

                  <div className="text-center text-[10px] text-slate-500">
                    ↓ Deduplication ({funnel.rates.deduplication_rate}%)
                  </div>

                  <div className="p-3 bg-slate-950/60 rounded-lg border border-slate-800/80 flex items-center justify-between">
                    <span className="text-slate-400">2. New Articles</span>
                    <strong className="text-slate-200 text-sm">{funnel.stages.new_articles.toLocaleString()}</strong>
                  </div>

                  <div className="text-center text-[10px] text-slate-500">
                    ↓ LLM Event Extraction ({funnel.rates.event_rate}%)
                  </div>

                  <div className="p-3 bg-slate-950/60 rounded-lg border border-amber-900/40 bg-amber-950/10 flex items-center justify-between">
                    <span className="text-amber-300 font-medium">3. Event Candidates</span>
                    <strong className="text-amber-200 text-sm">{funnel.stages.event_candidates.toLocaleString()}</strong>
                  </div>

                  <div className="text-center text-[10px] text-slate-500">
                    ↓ Geocoding Resolved ({funnel.rates.geocoding_rate}%)
                  </div>

                  <div className="p-3 bg-gradient-to-r from-sky-950/60 to-indigo-950/60 rounded-lg border border-sky-700/60 flex items-center justify-between">
                    <span className="text-sky-200 font-bold">4. Active Map Events</span>
                    <strong className="text-sky-300 text-base">{funnel.stages.active_map_events.toLocaleString()}</strong>
                  </div>

                  <div className="mt-4 pt-3 border-t border-slate-800 flex justify-between items-center text-xs">
                    <span className="text-slate-400">Overall Map Conversion:</span>
                    <span className="text-sky-400 font-extrabold text-sm">{funnel.rates.overall_map_conversion}%</span>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Time Series Chart & Media Source Coverage Table */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Time Series Chart */}
            <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 flex flex-col space-y-4">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
                <Activity className="w-5 h-5 text-emerald-400" />
                News Event Activity Trend ({period.toUpperCase()})
              </h2>

              <div className="h-48 flex items-end justify-between space-x-1.5 pt-4 px-2">
                {timeseries.map((ts, idx) => {
                  const maxVal = Math.max(...timeseries.map((t) => t.map_events), 1);
                  const hPct = Math.round((ts.map_events / maxVal) * 100);
                  const timeLabel = new Date(ts.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

                  return (
                    <div key={idx} className="flex-1 flex flex-col items-center group relative h-full justify-end">
                      {/* Tooltip */}
                      <div className="absolute -top-10 opacity-0 group-hover:opacity-100 transition z-10 bg-slate-800 text-slate-200 text-[10px] p-1.5 rounded shadow border border-slate-700 whitespace-nowrap pointer-events-none">
                        {timeLabel}: <strong>{ts.map_events} events</strong> ({ts.new_articles} articles)
                      </div>
                      <div
                        className="w-full bg-sky-500/80 hover:bg-sky-400 rounded-t transition-all"
                        style={{ height: `${Math.max(hPct, 4)}%` }}
                      />
                      <span className="text-[9px] text-slate-500 mt-1 truncate">{timeLabel}</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Media Source Performance & Health */}
            <div className="bg-slate-900 border border-slate-800 rounded-xl p-4 md:p-5 flex flex-col space-y-4">
              <h2 className="text-base font-bold text-slate-100 flex items-center gap-2 border-b border-slate-800 pb-3">
                <Radio className="w-5 h-5 text-indigo-400" />
                Media Source Performance
              </h2>

              <div className="overflow-y-auto max-h-[220px] space-y-2 text-xs pr-1">
                {sources.map((src) => (
                  <div key={src.source_id} className="p-2 bg-slate-950/60 rounded border border-slate-800 flex items-center justify-between">
                    <div>
                      <div className="font-semibold text-slate-200">{src.media_name} ({src.country_code})</div>
                      <div className="text-[10px] text-slate-400">{src.region}</div>
                    </div>
                    <div className="text-right">
                      <div className="font-bold text-sky-400">{src.map_events} map events</div>
                      <div className="text-[10px] text-slate-400">{src.new_articles} articles ({src.conversion_rate}%)</div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default DashboardView;
