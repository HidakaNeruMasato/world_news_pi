import React, { useEffect, useState } from 'react';
import { ActiveEvent, Article } from '../types/event';
import { fetchEventArticles } from '../api/client';
import { formatFullDateTime } from '../utils/time';
import { X, ExternalLink, ShieldCheck, MapPin, Calendar, Clock, Newspaper } from 'lucide-react';

interface EventDetailPanelProps {
  event: ActiveEvent | null;
  onClose: () => void;
}

export const EventDetailPanel: React.FC<EventDetailPanelProps> = ({ event, onClose }) => {
  const [articles, setArticles] = useState<Article[]>([]);
  const [loadingArticles, setLoadingArticles] = useState<boolean>(false);

  useEffect(() => {
    if (event) {
      setLoadingArticles(true);
      fetchEventArticles(event.id)
        .then((res) => setArticles(res.articles || []))
        .catch(() => setArticles([]))
        .finally(() => setLoadingArticles(false));
    }
  }, [event]);

  if (!event) return null;

  return (
    <div className="absolute top-4 right-4 z-[1000] w-96 max-w-[calc(100vw-2rem)] bg-slate-800/95 backdrop-blur border border-slate-700 rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[calc(100vh-6rem)]">
      {/* Header */}
      <div className="p-4 bg-slate-850 border-b border-slate-700 flex items-center justify-between">
        <div>
          <span className="text-xs font-bold uppercase px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
            {event.category}
          </span>
          <h3 className="text-base font-bold text-white mt-1">
            {event.location_name || event.city || event.region || 'Event Details'}
          </h3>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-700 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Detail Content */}
      <div className="p-4 overflow-y-auto space-y-4 text-xs text-slate-300 flex-1">
        {/* Geographic Info */}
        <div className="bg-slate-900/60 p-3 rounded border border-slate-700/60 space-y-1.5">
          <div className="flex items-center text-slate-400 font-semibold">
            <MapPin className="w-3.5 h-3.5 mr-1 text-rose-400" /> Location
          </div>
          <div>
            Country: <strong className="text-slate-100">{event.event_country || 'Global'}</strong>
          </div>
          {event.region && <div>Region/State: {event.region}</div>}
          {event.city && <div>City: {event.city}</div>}
          <div className="text-slate-500 text-[11px] font-mono mt-1">
            Lat: {event.latitude.toFixed(4)}, Lon: {event.longitude.toFixed(4)}
          </div>
        </div>

        {/* System Confidence & Expiration */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-700/60">
            <div className="text-slate-400 flex items-center mb-1">
              <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-400" /> Confidence
            </div>
            <div className="text-lg font-bold text-emerald-400">{(event.confidence * 100).toFixed(0)}%</div>
          </div>
          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-700/60">
            <div className="text-slate-400 flex items-center mb-1">
              <Clock className="w-3.5 h-3.5 mr-1 text-amber-400" /> Status
            </div>
            <div className="text-sm font-semibold uppercase text-amber-300">{event.status}</div>
          </div>
        </div>

        {/* Timestamps */}
        <div className="bg-slate-900/60 p-3 rounded border border-slate-700/60 space-y-1 text-slate-400">
          <div className="flex justify-between">
            <span>Occurred:</span>
            <span className="text-slate-200">{formatFullDateTime(event.occurred_at)}</span>
          </div>
          <div className="flex justify-between">
            <span>Last Updated:</span>
            <span className="text-slate-200">{formatFullDateTime(event.last_seen_at)}</span>
          </div>
          <div className="flex justify-between">
            <span>Expires At:</span>
            <span className="text-slate-200">{formatFullDateTime(event.expires_at)}</span>
          </div>
        </div>

        {/* Related News Articles */}
        <div className="border-t border-slate-700 pt-3">
          <h4 className="font-semibold text-slate-200 mb-2 flex items-center">
            <Newspaper className="w-4 h-4 mr-1 text-sky-400" /> Related News ({articles.length})
          </h4>
          {loadingArticles ? (
            <div className="text-slate-500 py-2 text-center">Loading news reports...</div>
          ) : articles.length === 0 ? (
            <div className="text-slate-500 py-2 text-center">No linked articles.</div>
          ) : (
            <div className="space-y-2">
              {articles.map((art) => (
                <div key={art.id} className="bg-slate-900/80 p-2.5 rounded border border-slate-700/80">
                  <div className="font-medium text-slate-200 text-xs line-clamp-2">{art.title}</div>
                  <div className="mt-1 flex items-center justify-between text-[11px] text-slate-400">
                    <span>{art.source_name || art.source_country || 'News Source'}</span>
                    {art.url ? (
                      <a
                        href={art.url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-sky-400 hover:underline flex items-center"
                      >
                        Read <ExternalLink className="w-3 h-3 ml-0.5" />
                      </a>
                    ) : null}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
