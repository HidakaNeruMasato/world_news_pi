import React, { useEffect, useRef } from 'react';
import { ActiveEvent } from '../types/event';
import { formatRelativeTime } from '../utils/time';
import { MapPin, Clock, Search, ArrowUpDown, Newspaper } from 'lucide-react';

interface EventListProps {
  events: ActiveEvent[];
  selectedEventId: number | null;
  onSelectEvent: (event: ActiveEvent) => void;
  searchQuery: string;
  onSearchChange: (query: string) => void;
  sortMode: 'newest' | 'confidence' | 'articles';
  onSortChange: (mode: 'newest' | 'confidence' | 'articles') => void;
}

export const EventList: React.FC<EventListProps> = ({
  events,
  selectedEventId,
  onSelectEvent,
  searchQuery,
  onSearchChange,
  sortMode,
  onSortChange,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);

  // UX-003 3-Way Synchronization: selectedEventID 変更時にスクロール位置を調整
  useEffect(() => {
    if (selectedEventId != null) {
      const cardElem = document.getElementById(`event-card-${selectedEventId}`);
      if (cardElem) {
        cardElem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }
  }, [selectedEventId]);

  return (
    <div className="flex flex-col h-full bg-slate-800 border-r border-slate-700 w-full md:w-80 flex-shrink-0">
      {/* Header & Count */}
      <div className="p-3 border-b border-slate-700 bg-slate-850 flex items-center justify-between">
        <h2 className="text-xs font-bold text-slate-200 uppercase tracking-wider flex items-center">
          <MapPin className="w-4 h-4 mr-1.5 text-sky-400" /> Active Events ({events.length})
        </h2>
      </div>

      {/* UX-007: Search Bar & Sort Dropdown */}
      <div className="p-2.5 bg-slate-900/60 border-b border-slate-700/80 space-y-2">
        <div className="relative">
          <Search className="w-3.5 h-3.5 absolute left-2.5 top-2.5 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            placeholder="Filter by keyword, city, country..."
            className="w-full bg-slate-800 border border-slate-700 rounded pl-8 pr-3 py-1 text-xs text-slate-200 placeholder-slate-400 focus:outline-none focus:border-sky-500"
          />
        </div>

        <div className="flex items-center justify-between text-xs text-slate-400 px-1">
          <span className="flex items-center text-[11px] font-medium">
            <ArrowUpDown className="w-3 h-3 mr-1 text-slate-400" /> Sort by:
          </span>
          <select
            value={sortMode}
            onChange={(e) => onSortChange(e.target.value as any)}
            className="bg-slate-800 text-slate-200 border border-slate-700 rounded px-2 py-0.5 text-[11px] focus:outline-none focus:border-sky-500"
          >
            <option value="newest">Newest First</option>
            <option value="confidence">Highest Confidence</option>
            <option value="articles">Most Articles</option>
          </select>
        </div>
      </div>

      {/* Scrollable Event List */}
      <div ref={containerRef} className="flex-1 overflow-y-auto divide-y divide-slate-700/50">
        {events.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-xs">No matching events found.</div>
        ) : (
          events.map((evt) => {
            const isSelected = selectedEventId === evt.id;
            const articleCount = evt.article_count || 1;

            return (
              <div
                key={evt.id}
                id={`event-card-${evt.id}`}
                onClick={() => onSelectEvent(evt)}
                className={`p-3 cursor-pointer transition ${
                  isSelected
                    ? 'bg-sky-950/70 border-l-4 border-sky-400 text-white shadow-md'
                    : 'hover:bg-slate-700/50 text-slate-300'
                }`}
              >
                <div className="flex items-start justify-between gap-1">
                  <span className="text-[11px] font-bold uppercase px-2 py-0.5 rounded bg-slate-700 text-slate-200 border border-slate-600">
                    {evt.category}
                  </span>
                  <span className="text-[11px] text-slate-400 flex items-center flex-shrink-0">
                    <Clock className="w-3 h-3 mr-1 text-slate-400" />
                    {formatRelativeTime(evt.occurred_at || evt.detected_at)}
                  </span>
                </div>

                <div className="mt-2 text-xs font-semibold text-slate-100">
                  {evt.location_name || evt.city || evt.region || evt.event_country || 'Unknown Location'}
                </div>

                <div className="mt-1.5 flex items-center justify-between text-[11px] text-slate-400">
                  <span>{evt.event_country ? `Country: ${evt.event_country}` : 'Global'}</span>

                  <div className="flex items-center space-x-2">
                    {/* UX-004: Multi-Article Badge */}
                    {articleCount > 1 && (
                      <span className="bg-sky-500/20 text-sky-300 border border-sky-500/40 text-[10px] px-1.5 py-0.5 rounded font-mono flex items-center font-semibold">
                        <Newspaper className="w-3 h-3 mr-1" />
                        {articleCount} Articles
                      </span>
                    )}
                    <span className="text-sky-400 font-mono text-[11px]">{(evt.confidence * 100).toFixed(0)}%</span>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
