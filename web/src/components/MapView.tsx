import React, { useEffect, useRef, useState } from 'react';
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
  const markersRef = useRef<Record<string, L.Layer>>({});
  const [zoomLevel, setZoomLevel] = useState<number>(2.5);

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

    // OpenStreetMap タイルレイヤー + Attribution
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19,
    }).addTo(map);

    map.on('zoomend', () => {
      setZoomLevel(map.getZoom());
    });

    mapRef.current = map;

    return () => {
      map.remove();
      mapRef.current = null;
    };
  }, []);

  // Reset World View 操作
  useEffect(() => {
    if (mapRef.current && resetViewTrigger > 0) {
      mapRef.current.flyTo([20.0, 0.0], 2.5, { duration: 1.2 });
    }
  }, [resetViewTrigger]);

  // マーカー & クラスター描画
  useEffect(() => {
    const map = mapRef.current;
    if (!map) return;

    // 既存レイヤーのクリーンアップ
    Object.values(markersRef.current).forEach((layer) => layer.remove());
    markersRef.current = {};

    const isClusteredView = zoomLevel <= 4 && events.length > 15;

    if (isClusteredView) {
      // 空間グリッドクラスター化 (ズームレベル 2-4)
      const gridSize = zoomLevel <= 3 ? 12 : 8; // グリッド角度
      const clusters: Record<string, { events: ActiveEvent[]; lat: number; lon: number }> = {};

      events.forEach((evt) => {
        if (evt.latitude == null || evt.longitude == null) return;
        const gridKey = `${Math.floor(evt.latitude / gridSize)}_${Math.floor(evt.longitude / gridSize)}`;
        if (!clusters[gridKey]) {
          clusters[gridKey] = { events: [], lat: 0, lon: 0 };
        }
        clusters[gridKey].events.push(evt);
        clusters[gridKey].lat += evt.latitude;
        clusters[gridKey].lon += evt.longitude;
      });

      Object.entries(clusters).forEach(([key, group]) => {
        const count = group.events.length;
        const avgLat = group.lat / count;
        const avgLon = group.lon / count;

        if (count === 1) {
          // 単一イベントは個別マーカー
          const evt = group.events[0];
          const isSelected = selectedEvent?.id === evt.id;
          const catColor = CATEGORY_COLORS[evt.category.toLowerCase()] || CATEGORY_COLORS.other;
          const opacity = calculateMarkerOpacity(evt.last_seen_at, evt.expires_at);

          const marker = L.circleMarker([evt.latitude, evt.longitude], {
            radius: isSelected ? 12 : 8,
            fillColor: catColor,
            color: isSelected ? '#ffffff' : '#000000',
            weight: isSelected ? 3 : 1.5,
            opacity: isSelected ? 1.0 : opacity,
            fillOpacity: isSelected ? 1.0 : opacity,
          }).addTo(map);

          marker.on('click', () => onSelectEvent(evt));
          markersRef.current[`evt_${evt.id}`] = marker;
        } else {
          // クラスターバッジ作成 (ズーム 2-4)
          const clusterIcon = L.divIcon({
            html: `<div class="w-11 h-11 rounded-full bg-sky-600/90 border-2 border-white text-white font-bold text-xs flex items-center justify-center shadow-lg hover:scale-110 transition cursor-pointer">${count}</div>`,
            className: 'custom-cluster-marker',
            iconSize: [44, 44],
            iconAnchor: [22, 22],
          });

          const clusterMarker = L.marker([avgLat, avgLon], { icon: clusterIcon }).addTo(map);

          clusterMarker.on('click', () => {
            map.flyTo([avgLat, avgLon], Math.max(map.getZoom() + 2.5, 5), { duration: 0.8 });
          });

          markersRef.current[`cluster_${key}`] = clusterMarker;
        }
      });
    } else {
      // 個別マーカー表示 (ズームレベル 5+)
      events.forEach((evt) => {
        if (evt.latitude == null || evt.longitude == null) return;
        const isSelected = selectedEvent?.id === evt.id;
        const catColor = CATEGORY_COLORS[evt.category.toLowerCase()] || CATEGORY_COLORS.other;
        const opacity = calculateMarkerOpacity(evt.last_seen_at, evt.expires_at);

        const marker = L.circleMarker([evt.latitude, evt.longitude], {
          radius: isSelected ? 13 : 8,
          fillColor: catColor,
          color: isSelected ? '#ffffff' : '#000000',
          weight: isSelected ? 3.5 : 1.5,
          opacity: isSelected ? 1.0 : opacity,
          fillOpacity: isSelected ? 1.0 : opacity,
        }).addTo(map);

        if (isSelected) {
          marker.bringToFront();
        }

        marker.on('click', () => {
          onSelectEvent(evt);
        });

        markersRef.current[`evt_${evt.id}`] = marker;
      });
    }
  }, [events, selectedEvent, onSelectEvent, zoomLevel]);

  // 選択イベントへのフォーカス移動
  useEffect(() => {
    if (mapRef.current && selectedEvent && selectedEvent.latitude != null && selectedEvent.longitude != null) {
      mapRef.current.flyTo([selectedEvent.latitude, selectedEvent.longitude], Math.max(mapRef.current.getZoom(), 7), {
        duration: 1.0,
      });
    }
  }, [selectedEvent]);

  return <div ref={mapContainerRef} className="w-full h-full bg-slate-950" />;
};
