import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import { ActiveEvent } from '../types/event';
import { calculateMarkerOpacity } from '../utils/time';

interface MapViewProps {
  events: ActiveEvent[];
  selectedEvent: ActiveEvent | null;
  onSelectEvent: (evt: ActiveEvent) => void;
  resetViewTrigger: number;
}

// カテゴリ別マーカー色マッピング
const CATEGORY_COLORS: Record<string, string> = {
  earthquake: '#ef4444',       // 赤
  tsunami: '#3b82f6',          // 青
  volcanic_eruption: '#f97316',// オレンジ
  flood: '#06b6d4',            // シアン
  wildfire: '#dc2626',         // 深紅
  storm: '#8b5cf6',            // 紫
  accident: '#eab308',         // 黄
  aviation_accident: '#f59e0b',// アンバー
  maritime_accident: '#0284c7',// ディープブルー
  crime: '#64748b',            // スレート
  terrorism: '#991b1b',        // ボルドー
  armed_conflict: '#451a03',   // ダークブラウン
  war: '#1e1b4b',              // インディゴ
  explosion: '#d97706',        // ダークオレンジ
  fire: '#ea580c',             // 朱色
  politics: '#10b981',         // エメラルド
  economy: '#6366f1',          // インディゴ
  sports: '#84cc16',           // ライム
  other: '#94a3b8',            // グレー
};

export const MapView: React.FC<MapViewProps> = ({
  events,
  selectedEvent,
  onSelectEvent,
  resetViewTrigger,
}) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<L.Map | null>(null);
  const markersRef = useRef<Record<number, L.CircleMarker>>({});

  // Leaflet Map 初期化
  useEffect(() => {
    if (!mapContainerRef.current || mapRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [20.0, 0.0],
      zoom: 2.5,
      zoomControl: true,
      minZoom: 2,
      maxZoom: 18,
    });

    // OpenStreetMap タイルレイヤー + Attribution (要件 33 遵守)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Reset World View リセット操作
  useEffect(() => {
    if (mapRef.current && resetViewTrigger > 0) {
      mapRef.current.flyTo([20.0, 0.0], 2.5, { duration: 1.2 });
    }
  }, [resetViewTrigger]);

  // マーカー描画 & 更新
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    const currentMarkers = markersRef.current;
    const activeIds = new Set(events.map((e) => e.id));

    // 消失したマーカーの削除
    Object.keys(currentMarkers).forEach((idStr) => {
      const id = Number(idStr);
      if (!activeIds.has(id)) {
        currentMarkers[id].remove();
        delete currentMarkers[id];
      }
    });

    // 各イベントに対するマーカー作成/更新
    events.forEach((evt) => {
      const isSelected = selectedEvent?.id === evt.id;
      const catColor = CATEGORY_COLORS[evt.category.toLowerCase()] || CATEGORY_COLORS.other;
      const opacity = calculateMarkerOpacity(evt.last_seen_at, evt.expires_at);

      if (currentMarkers[evt.id]) {
        // 既存マーカーの位置・スタイル更新
        const marker = currentMarkers[evt.id];
        marker.setLatLng([evt.latitude, evt.longitude]);
        marker.setStyle({
          fillColor: catColor,
          color: isSelected ? '#ffffff' : '#000000',
          weight: isSelected ? 3 : 1.5,
          radius: isSelected ? 12 : 8,
          fillOpacity: isSelected ? 1.0 : opacity,
          opacity: isSelected ? 1.0 : opacity,
        });
      } else {
        // 新規 CircleMarker 作成
        const marker = L.circleMarker([evt.latitude, evt.longitude], {
          radius: isSelected ? 12 : 8,
          fillColor: catColor,
          color: isSelected ? '#ffffff' : '#000000',
          weight: isSelected ? 3 : 1.5,
          opacity: opacity,
          fillOpacity: opacity,
        }).addTo(map);

        marker.on('click', () => {
          onSelectEvent(evt);
        });

        currentMarkers[evt.id] = marker;
      }
    });
  }, [events, selectedEvent, onSelectEvent]);

  // 選択されたマーカーへのフォーカス移動
  useEffect(() => {
    if (mapRef.current && selectedEvent) {
      mapRef.current.flyTo([selectedEvent.latitude, selectedEvent.longitude], 7, {
        duration: 1.0,
      });
    }
  }, [selectedEvent]);

  return <div ref={mapContainerRef} className="w-full h-full bg-slate-950" />;
};
