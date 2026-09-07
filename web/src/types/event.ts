/** World News Map Frontend TypeScript 型定義 (要件 31 遵守) */

export type EventCategory =
  | 'earthquake'
  | 'tsunami'
  | 'volcanic_eruption'
  | 'flood'
  | 'wildfire'
  | 'storm'
  | 'accident'
  | 'aviation_accident'
  | 'maritime_accident'
  | 'crime'
  | 'terrorism'
  | 'armed_conflict'
  | 'war'
  | 'explosion'
  | 'fire'
  | 'infrastructure_failure'
  | 'politics'
  | 'economy'
  | 'sports'
  | 'other';

export interface ActiveEvent {
  id: number;
  category: EventCategory | string;
  event_country: string | null;
  country_name?: string | null;
  region?: string | null;
  city?: string | null;
  location_name: string | null;
  latitude: number;
  longitude: number;
  confidence: number;
  status: 'active' | 'expired' | string;
  geocoding_status: 'resolved' | 'unresolved' | string;
  occurred_at: string | null;
  detected_at: string | null;
  last_seen_at: string | null;
  expires_at: string | null;
  article_count?: number;
}


export interface ActiveEventsResponse {
  events: ActiveEvent[];
  count: number;
  generated_at: string;
}

export interface Article {
  id: number;
  source_id: number;
  source_country: string | null;
  source_name?: string | null;
  title: string;
  description: string | null;
  url: string | null;
  published_at: string | null;
  fetched_at: string;
  language: string | null;
}

export interface EventArticlesResponse {
  articles: Article[];
  count: number;
}
