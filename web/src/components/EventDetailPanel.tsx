import React, { useEffect, useState } from 'react';
import { ActiveEvent, Article } from '../types/event';
import { fetchEventArticles } from '../api/client';
import { formatFullDateTime } from '../utils/time';
import { X, ExternalLink, ShieldCheck, MapPin, Clock, Newspaper, ArrowLeft, Globe } from 'lucide-react';

interface EventDetailPanelProps {
  event: ActiveEvent | null;
  onClose: () => void;
  isMobile?: boolean;
}

export const EventDetailPanel: React.FC<EventDetailPanelProps> = ({ event, onClose, isMobile = false }) => {
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

  const panelClasses = isMobile
    ? 'w-full h-full bg-slate-800 text-slate-100 flex flex-col'
    : 'absolute top-4 right-4 z-[1000] w-96 max-w-[calc(100vw-2rem)] bg-slate-800/95 backdrop-blur border border-slate-700 rounded-lg shadow-2xl overflow-hidden flex flex-col max-h-[calc(100vh-6rem)]';

  return (
    <div className={panelClasses}>
      {/* Header */}
      <div className="p-3.5 bg-slate-850 border-b border-slate-700 flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {isMobile && (
            <button onClick={onClose} className="p-1 text-slate-400 hover:text-white mr-1">
              <ArrowLeft className="w-5 h-5" />
            </button>
          )}
          <div>
            <span className="text-[10px] font-bold uppercase px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
              {event.category}
            </span>
            <h3 className="text-sm font-bold text-white mt-1">
              {event.location_name || event.city || event.region || 'Event Details'}
            </h3>
          </div>
        </div>
        <button
          onClick={onClose}
          className="text-slate-400 hover:text-white p-1 rounded hover:bg-slate-700 transition"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Content */}
      <div className="p-4 overflow-y-auto space-y-3.5 text-xs text-slate-300 flex-1">
        {/* Geographic Info */}
        <div className="bg-slate-900/60 p-3 rounded border border-slate-700/60 space-y-1.5">
          <div className="flex items-center text-slate-400 font-semibold">
            <MapPin className="w-3.5 h-3.5 mr-1 text-rose-400" /> Location Breakdown
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Country:</span>
            <strong className="text-slate-100">{event.event_country || 'Global'}</strong>
          </div>
          {event.region && (
            <div className="flex justify-between">
              <span className="text-slate-400">Region:</span>
              <span className="text-slate-200">{event.region}</span>
            </div>
          )}
          {event.city && (
            <div className="flex justify-between">
              <span className="text-slate-400">City:</span>
              <span className="text-slate-200">{event.city}</span>
            </div>
          )}
          {event.latitude != null && event.longitude != null && (
            <div className="text-slate-500 text-[11px] font-mono mt-1 text-right">
              Lat: {event.latitude.toFixed(4)}, Lon: {event.longitude.toFixed(4)}
            </div>
          )}
        </div>

        {/* Confidence & Status */}
        <div className="grid grid-cols-2 gap-2">
          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-700/60">
            <div className="text-slate-400 flex items-center mb-1 text-[11px]">
              <ShieldCheck className="w-3.5 h-3.5 mr-1 text-emerald-400" /> System Confidence
            </div>
            <div className="text-base font-bold text-emerald-400">{(event.confidence * 100).toFixed(0)}%</div>
          </div>
          <div className="bg-slate-900/60 p-2.5 rounded border border-slate-700/60">
            <div className="text-slate-400 flex items-center mb-1 text-[11px]">
              <Clock className="w-3.5 h-3.5 mr-1 text-amber-400" /> Status
            </div>
            <div className="text-xs font-semibold uppercase text-amber-300">{event.status}</div>
          </div>
        </div>

        {/* Timestamps */}
        <div className="bg-slate-900/60 p-3 rounded border border-slate-700/60 space-y-1 text-[11px] text-slate-400">
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

        {/* Related Media Articles (UX-004) */}
        <div className="border-t border-slate-700/80 pt-3">
          <h4 className="font-semibold text-slate-200 mb-2 flex items-center justify-between">
            <span className="flex items-center">
              <Newspaper className="w-4 h-4 mr-1 text-sky-400" /> Covered by {articles.length} Media Sources
            </span>
          </h4>

          {loadingArticles ? (
            <div className="text-slate-500 py-3 text-center text-xs">Loading media reports...</div>
          ) : articles.length === 0 ? (
            <div className="text-slate-500 py-3 text-center text-xs">No linked articles available.</div>
          ) : (
            <div className="space-y-2">
              {articles.map((art) => (
                <div key={art.id} className="bg-slate-900/90 p-2.5 rounded border border-slate-700/80 space-y-1">
                  <div className="font-semibold text-slate-100 text-xs leading-snug line-clamp-2">{art.title}</div>
                  <div className="flex items-center justify-between text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                    <span className="flex items-center font-medium text-slate-300">
                      <Globe className="w-3 h-3 mr-1 text-indigo-400" />
                      {art.source_name || 'Publisher Source'}
                      {art.source_country && (
                        <span className="ml-1.5 text-[10px] bg-slate-800 px-1 py-0.2 rounded border border-slate-700 uppercase">
                          {art.source_country}
                        </span>
                      )}
                    </span>
                    {art.url && (
                      <a
                        href={art.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sky-400 hover:text-sky-300 font-semibold hover:underline flex items-center ml-2 flex-shrink-0"
                      >
                        Read <ExternalLink className="w-3 h-3 ml-0.5" />
                      </a>
                    )}
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
