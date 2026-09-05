export interface DashboardSummary {
  period: string;
  rss_sources: number;
  rss_items: number;
  new_articles: number;
  analyzed_articles: number;
  event_articles: number;
  geocoding_resolved: number;
  map_events: number;
  map_conversion_rate: number;
  generated_at: string;
}

export interface FunnelMetrics {
  period: string;
  stages: {
    rss_items_seen: number;
    new_articles: number;
    llm_analyzed: number;
    event_candidates: number;
    geocoding_resolved: number;
    active_map_events: number;
  };
  rates: {
    deduplication_rate: number;
    analysis_rate: number;
    event_rate: number;
    geocoding_rate: number;
    map_display_rate: number;
    overall_map_conversion: number;
  };
}

export interface RegionalActivity {
  region: string;
  rss_sources: number;
  new_articles: number;
  event_articles: number;
  map_events: number;
  coverage_status: string;
}

export interface SourceMetric {
  source_id: string;
  media_name: string;
  country_code: string;
  region: string;
  new_articles: number;
  event_articles: number;
  map_events: number;
  conversion_rate: number;
  health: string;
}

export interface TimeSeriesPoint {
  timestamp: string;
  new_articles: number;
  events: number;
  map_events: number;
}

export interface SourceHealth {
  overall: string;
  rss_collector: string;
  pipeline: string;
  llm_analyzer: string;
  geocoder: string;
  event_engine: string;
  consecutive_failures: number;
  last_check_at: string;
}

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

async function fetchJson<T>(endpoint: string): Promise<T> {
  const res = await fetch(`${API_BASE_URL}${endpoint}`);
  if (!res.ok) {
    throw new Error(`HTTP Error ${res.status} fetching ${endpoint}`);
  }
  return res.json() as Promise<T>;
}

export async function fetchDashboardSummary(period = '24h'): Promise<DashboardSummary> {
  return fetchJson<DashboardSummary>(`/api/dashboard/summary?period=${period}`);
}

export async function fetchDashboardFunnel(period = '24h'): Promise<FunnelMetrics> {
  return fetchJson<FunnelMetrics>(`/api/dashboard/funnel?period=${period}`);
}

export async function fetchDashboardRegions(period = '24h'): Promise<RegionalActivity[]> {
  return fetchJson<RegionalActivity[]>(`/api/dashboard/regions?period=${period}`);
}

export async function fetchDashboardSources(period = '24h'): Promise<SourceMetric[]> {
  return fetchJson<SourceMetric[]>(`/api/dashboard/sources?period=${period}`);
}

export async function fetchDashboardTimeseries(period = '24h'): Promise<TimeSeriesPoint[]> {
  return fetchJson<TimeSeriesPoint[]>(`/api/dashboard/timeseries?period=${period}`);
}

export async function fetchDashboardHealth(): Promise<SourceHealth> {
  return fetchJson<SourceHealth>(`/api/dashboard/source-health`);
}
