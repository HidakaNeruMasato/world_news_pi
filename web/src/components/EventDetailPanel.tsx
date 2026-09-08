import React, { useEffect, useState } from 'react';
import { ActiveEvent, Article } from '../types/event';
import { fetchEventArticles } from '../api/client';
import { formatFullDateTime, formatRelativeTime } from '../utils/time';
import { isSafeHttpUrl } from '../utils/url';
import { X, ExternalLink, ShieldCheck, MapPin, Clock, Newspaper, ArrowLeft, Globe, AlertCircle } from 'lucide-react';

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
      {/* ヘッダー領域 */}
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

      {/* メインコンテンツ */}
      <div className="p-4 overflow-y-auto space-y-3.5 text-xs text-slate-300 flex-1">
        {/* 位置情報ブレイクダウン */}
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

        {/* 確信度 & ステータス */}
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

        {/* タイムスタンプ情報 */}
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

        {/* 関連ニュース記事 & 記事プレビューカード (T023-1 UX-008) */}
        <div className="border-t border-slate-700/80 pt-3 space-y-2">
          <h4 className="font-semibold text-slate-200 mb-2 flex items-center justify-between">
            <span className="flex items-center text-xs">
              <Newspaper className="w-4 h-4 mr-1.5 text-sky-400" /> Covered by {articles.length} Media {articles.length === 1 ? 'Source' : 'Sources'}
            </span>
          </h4>

          {loadingArticles ? (
            <div className="text-slate-500 py-4 text-center text-xs">Loading media reports...</div>
          ) : articles.length === 0 ? (
            <div className="text-slate-500 py-4 text-center text-xs">No linked articles available.</div>
          ) : (
            <div className="space-y-3">
              {articles.map((art) => {
                const hasValidUrl = isSafeHttpUrl(art.url);
                const publishedTimeStr = art.published_at || art.fetched_at;

                return (
                  <article
                    key={art.id}
                    className="bg-slate-900/90 p-3 rounded-lg border border-slate-700/80 shadow-md space-y-2 hover:border-slate-600 transition"
                  >
                    {/* メディア発行元・国タグ・日時 */}
                    <div className="flex items-center justify-between text-[11px] text-slate-400 border-b border-slate-800 pb-1.5">
                      <span className="flex items-center font-medium text-slate-300">
                        <Globe className="w-3.5 h-3.5 mr-1 text-indigo-400" />
                        {art.source_name || 'Publisher Source'}
                        {art.source_country && (
                          <span className="ml-1.5 text-[10px] bg-slate-800 px-1.5 py-0.2 rounded border border-slate-700 uppercase font-mono text-slate-400">
                            {art.source_country}
                          </span>
                        )}
                      </span>

                      {publishedTimeStr && (
                        <span className="text-[10px] text-slate-400 flex items-center">
                          <Clock className="w-3 h-3 mr-1 text-slate-500" />
                          {formatRelativeTime(publishedTimeStr)}
                        </span>
                      )}
                    </div>

                    {/* 記事タイトル */}
                    <h5 className="font-bold text-slate-100 text-xs leading-snug">
                      {art.title}
                    </h5>

                    {/* 記事プレビュー概要 (descriptionが存在する場合表示) */}
                    {art.description && (
                      <p className="text-[11px] text-slate-300 leading-relaxed bg-slate-950/50 p-2 rounded border border-slate-800/80 line-clamp-3">
                        {art.description}
                      </p>
                    )}

                    {/* 明示的な元記事遷移 CTA ボタン (最低44pxのタップ領域確保) */}
                    <div className="pt-1">
                      {hasValidUrl ? (
                        <a
                          href={art.url!}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="inline-flex items-center justify-center w-full px-3 py-2 text-xs font-bold text-white bg-sky-600 hover:bg-sky-500 active:bg-sky-700 rounded border border-sky-400/30 transition shadow-sm min-h-[44px]"
                        >
                          元記事を読む <ExternalLink className="w-3.5 h-3.5 ml-1.5" />
                        </a>
                      ) : (
                        <span className="inline-flex items-center justify-center w-full px-3 py-2 text-xs font-semibold text-slate-500 bg-slate-800/60 rounded border border-slate-700/50 min-h-[44px]">
                          <AlertCircle className="w-3.5 h-3.5 mr-1 text-slate-500" /> 元記事URLを取得できません
                        </span>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
