import React from 'react';
import { ActiveEvent } from '../types/event';
import { formatRelativeTime } from '../utils/time';
import { MapPin, Clock } from 'lucide-react';

interface EventListProps {
  events: ActiveEvent[];
  selectedEventId: number | null;
  onSelectEvent: (event: ActiveEvent) => void;
}

export const EventList: React.FC<EventListProps> = ({ events, selectedEventId, onSelectEvent }) => {
  return (
    <div className="flex flex-col h-full bg-slate-800 border-r border-slate-700 w-full md:w-80 flex-shrink-0">
      <div className="p-3 border-b border-slate-700 bg-slate-850">
        <h2 className="text-sm font-semibold text-slate-200 uppercase tracking-wider flex items-center">
          <MapPin className="w-4 h-4 mr-1.5 text-sky-400" /> Active Events ({events.length})
        </h2>
      </div>

      <div className="flex-1 overflow-y-auto divide-y divide-slate-700/50">
        {events.length === 0 ? (
          <div className="p-6 text-center text-slate-500 text-sm">No active events found.</div>
        ) : (
          events.map((evt) => {
            const isSelected = selectedEventId === evt.id;
            return (
              <div
                key={evt.id}
                onClick={() => onSelectEvent(evt)}
                className={`p-3 cursor-pointer transition ${
                  isSelected
                    ? 'bg-sky-950/60 border-l-4 border-sky-500 text-white'
                    : 'hover:bg-slate-700/50 text-slate-300'
                }`}
              >
                <div className="flex items-start justify-between">
                  <span className="text-xs font-semibold px-2 py-0.5 rounded uppercase bg-slate-700 text-slate-200 border border-slate-600">
                    {evt.category}
                  </span>
                  <span className="text-xs text-slate-400 flex items-center">
                    <Clock className="w-3 h-3 mr-1" />
                    {formatRelativeTime(evt.occurred_at || evt.detected_at)}
                  </span>
                </div>

                <div className="mt-2 text-sm font-medium">
                  {evt.location_name || evt.city || evt.region || evt.event_country || 'Unknown Location'}
                </div>

                <div className="mt-1 text-xs text-slate-400 flex items-center justify-between">
                  <span>{evt.event_country ? `Country: ${evt.event_country}` : 'Global'}</span>
                  <span className="text-sky-400 font-mono">Conf: {(evt.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};
