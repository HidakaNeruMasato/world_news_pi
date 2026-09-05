import { ActiveEventsResponse, EventArticlesResponse } from '../types/event';

// 開発環境と本番統合環境で柔軟にエンドポイントを切り替え
const BASE_URL = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchActiveEvents(): Promise<ActiveEventsResponse> {
  const response = await fetch(`${BASE_URL}/api/events/active`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}

export async function fetchEventArticles(eventId: number): Promise<EventArticlesResponse> {
  const response = await fetch(`${BASE_URL}/api/events/${eventId}/articles`);
  if (!response.ok) {
    throw new Error(`API Error: ${response.status} ${response.statusText}`);
  }
  return response.json();
}
