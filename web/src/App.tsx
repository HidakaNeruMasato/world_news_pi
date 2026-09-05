import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { ActiveEvent } from './types/event';
import { fetchActiveEvents } from './api/client';
import { Header } from './components/Header';
import { StatusBar } from './components/StatusBar';
import { FilterBar } from './components/FilterBar';
import { EventList } from './components/EventList';
import { MapView } from './components/MapView';
import { EventDetailPanel } from './components/EventDetailPanel';
import { DashboardView } from './components/DashboardView';
import { AlertTriangle, RefreshCw } from 'lucide-react';

const REFRESH_INTERVAL_MS = 30000; // 30秒 Polling

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'map' | 'dashboard'>('map');
  const [events, setEvents] = useState<ActiveEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<ActiveEvent | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [isRefreshing, setIsRefreshing] = useState<boolean>(false);
  const [isConnected, setIsConnected] = useState<boolean>(true);
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [resetViewTrigger, setResetViewTrigger] = useState<number>(0);

  // フィルタ状態
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [selectedCountry, setSelectedCountry] = useState<string>('ALL');

  // イベント取得処理
  const loadEvents = useCallback(async (isManualRefresh = false) => {
    if (isManualRefresh) setIsRefreshing(true);

    try {
      const data = await fetchActiveEvents();
      setEvents(data.events || []);
      setIsConnected(true);
      setLastUpdated(new Date().toLocaleTimeString());
    } catch (err) {
      console.error('Failed to fetch active events:', err);
      setIsConnected(false);
    } finally {
      setLoading(false);
      setIsRefreshing(false);
    }
  }, []);

  // 初回ロード & 30秒 Polling
  useEffect(() => {
    loadEvents();
    const interval = setInterval(() => {
      loadEvents();
    }, REFRESH_INTERVAL_MS);
    return () => clearInterval(interval);
  }, [loadEvents]);

  // カテゴリ・国フィルタ候補リストの算出
  const categories = useMemo(() => {
    const set = new Set(events.map((e) => e.category).filter(Boolean));
    return Array.from(set).sort();
  }, [events]);

  const countries = useMemo(() => {
    const set = new Set(events.map((e) => e.event_country).filter(Boolean) as string[]);
    return Array.from(set).sort();
  }, [events]);

  // フィルタ適用後イベント一覧
  const filteredEvents = useMemo(() => {
    return events.filter((e) => {
      if (selectedCategory !== 'ALL' && e.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return false;
      }
      if (selectedCountry !== 'ALL' && e.event_country !== selectedCountry) {
        return false;
      }
      return true;
    });
  }, [events, selectedCategory, selectedCountry]);

  const handleSelectRegionFromDashboard = (region: string) => {
    setActiveTab('map');
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-900 text-slate-100 overflow-hidden font-sans">
      {/* Header */}
      <Header
        onRefresh={() => loadEvents(true)}
        onResetView={() => setResetViewTrigger((prev) => prev + 1)}
        isRefreshing={isRefreshing}
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />

      {activeTab === 'dashboard' ? (
        <DashboardView onSelectRegion={handleSelectRegionFromDashboard} />
      ) : (
        <>
          {/* Filter Bar */}
          <FilterBar
            categories={categories}
            countries={countries}
            selectedCategory={selectedCategory}
            selectedCountry={selectedCountry}
            onCategoryChange={setSelectedCategory}
            onCountryChange={setSelectedCountry}
          />

          {/* Main Body */}
          <div className="flex-1 flex flex-col md:flex-row relative overflow-hidden">
            {/* Error Notification Bar */}
            {!isConnected && (
              <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[1000] bg-rose-900/90 text-rose-100 px-4 py-2 rounded-lg shadow-xl border border-rose-600 flex items-center space-x-2 text-xs md:text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-300 flex-shrink-0" />
                <span>Unable to connect to World News server. Displaying last cached events.</span>
                <button
                  onClick={() => loadEvents(true)}
                  className="ml-2 bg-rose-700 hover:bg-rose-600 px-2 py-1 rounded font-semibold text-white transition flex items-center"
                >
                  <RefreshCw className="w-3 h-3 mr-1" /> Retry
                </button>
              </div>
            )}

            {/* Loading Overlay */}
            {loading && (
              <div className="absolute inset-0 z-[2000] bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
                <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm font-medium text-slate-300">Loading World Events...</p>
              </div>
            )}

            {/* Left Side: Event List */}
            <EventList
              events={filteredEvents}
              selectedEventId={selectedEvent?.id || null}
              onSelectEvent={(evt) => setSelectedEvent(evt)}
            />

            {/* Right Side: Map Canvas */}
            <div className="flex-1 h-full relative">
              <MapView
                events={filteredEvents}
                selectedEvent={selectedEvent}
                onSelectEvent={(evt) => setSelectedEvent(evt)}
                resetViewTrigger={resetViewTrigger}
              />

              {/* Empty State Banner */}
              {!loading && isConnected && filteredEvents.length === 0 && (
                <div className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[900] bg-slate-800/90 backdrop-blur px-4 py-2 rounded border border-slate-700 text-xs text-slate-400">
                  No active events matching filter criteria.
                </div>
              )}

              {/* Detail Overlay Panel */}
              <EventDetailPanel event={selectedEvent} onClose={() => setSelectedEvent(null)} />
            </div>
          </div>

          {/* Footer Status Bar */}
          <StatusBar
            activeCount={filteredEvents.length}
            lastUpdated={lastUpdated}
            isConnected={isConnected}
          />
        </>
      )}
    </div>
  );
};

export default App;
