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
import { AlertTriangle, RefreshCw, ChevronUp, ChevronDown, ListFilter } from 'lucide-react';
import { getEventRegion, computeRegionalCounts, REGION_BOUNDS } from './utils/region';

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

  // UX-002 / UX-007 / Mobile State
  const [selectedRegion, setSelectedRegion] = useState<string>('All');
  const [selectedCountry, setSelectedCountry] = useState<string>('ALL');
  const [selectedCategory, setSelectedCategory] = useState<string>('ALL');
  const [searchQuery, setSearchQuery] = useState<string>('');
  const [sortMode, setSortMode] = useState<'newest' | 'confidence' | 'articles'>('newest');

  const [bottomSheetState, setBottomSheetState] = useState<'collapsed' | 'half' | 'full'>('collapsed');
  const [isMobile, setIsMobile] = useState<boolean>(window.innerWidth < 768);

  // Responsive Viewport Resize Detector
  useEffect(() => {
    const handleResize = () => {
      setIsMobile(window.innerWidth < 768);
    };
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Keyboard ESC Key Listener (UX-003 Deselect)
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        setSelectedEvent(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

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

  // 地域別イベント集計 (UX-006)
  const regionalCounts = useMemo(() => {
    return computeRegionalCounts(events);
  }, [events]);

  // Cascading Country Dropdown Option Derivation (UX-002)
  const availableCountries = useMemo(() => {
    const set = new Set<string>();
    events.forEach((e) => {
      if (!e.event_country) return;
      if (selectedRegion === 'All' || getEventRegion(e) === selectedRegion) {
        set.add(e.event_country);
      }
    });
    return Array.from(set).sort();
  }, [events, selectedRegion]);

  // Categories Option Derivation
  const categories = useMemo(() => {
    const set = new Set(events.map((e) => e.category).filter(Boolean));
    return Array.from(set).sort();
  }, [events]);

  // Region 変更時の Country cascading リセット
  const handleRegionChange = (reg: string) => {
    setSelectedRegion(reg);
    setSelectedCountry('ALL');
    if (reg !== 'All' && REGION_BOUNDS[reg]) {
      setResetViewTrigger((prev) => prev + 1);
    }
  };

  // Region Pill Click (UX-006)
  const handleSelectRegionPill = (reg: string) => {
    if (selectedRegion === reg) {
      setSelectedRegion('All');
      setSelectedCountry('ALL');
    } else {
      handleRegionChange(reg);
    }
  };

  // Reset Filters Action
  const handleClearFilters = () => {
    setSelectedRegion('All');
    setSelectedCountry('ALL');
    setSelectedCategory('ALL');
    setSearchQuery('');
  };

  // Filter & Search & Sort Pipeline
  const filteredEvents = useMemo(() => {
    let result = events.filter((e) => {
      // 1. Region Filter (UX-002)
      if (selectedRegion !== 'All' && getEventRegion(e) !== selectedRegion) {
        return false;
      }
      // 2. Country Filter
      if (selectedCountry !== 'ALL' && e.event_country !== selectedCountry) {
        return false;
      }
      // 3. Category Filter
      if (selectedCategory !== 'ALL' && e.category.toLowerCase() !== selectedCategory.toLowerCase()) {
        return false;
      }
      // 4. Keyword Search Filter (UX-007)
      if (searchQuery.trim() !== '') {
        const q = searchQuery.toLowerCase();
        const text = `${e.location_name || ''} ${e.city || ''} ${e.region || ''} ${e.event_country || ''} ${e.category || ''}`.toLowerCase();
        if (!text.includes(q)) return false;
      }
      return true;
    });

    // 5. Sorting Pipeline (UX-007)
    return result.sort((a, b) => {
      if (sortMode === 'confidence') {
        return (b.confidence || 0) - (a.confidence || 0);
      }
      if (sortMode === 'articles') {
        return (b.article_count || 1) - (a.article_count || 1);
      }
      // Default: Newest First
      const timeA = new Date(a.occurred_at || a.detected_at || a.last_seen_at || 0).getTime();
      const timeB = new Date(b.occurred_at || b.detected_at || b.last_seen_at || 0).getTime();
      return timeB - timeA;
    });
  }, [events, selectedRegion, selectedCountry, selectedCategory, searchQuery, sortMode]);

  // Dashboard から Region 選択時
  const handleSelectRegionFromDashboard = (region: string) => {
    setActiveTab('map');
    handleRegionChange(region);
  };

  // Event Selection & Mobile Sheet Control
  const handleSelectEvent = (evt: ActiveEvent) => {
    setSelectedEvent(evt);
    if (isMobile) {
      setBottomSheetState('half');
    }
  };

  return (
    <div className="flex flex-col h-screen w-screen bg-slate-900 text-slate-100 overflow-hidden font-sans">
      {/* Header with UX-006 Overview Strip */}
      <Header
        onRefresh={() => loadEvents(true)}
        onResetView={() => setResetViewTrigger((prev) => prev + 1)}
        isRefreshing={isRefreshing}
        activeTab={activeTab}
        onTabChange={setActiveTab}
        totalEvents={filteredEvents.length}
        regionalCounts={regionalCounts}
        onSelectRegionPill={handleSelectRegionPill}
        selectedRegion={selectedRegion}
      />

      {activeTab === 'dashboard' ? (
        <DashboardView onSelectRegion={handleSelectRegionFromDashboard} />
      ) : (
        <>
          {/* Filter Bar with UX-002 Region Dropdown */}
          <FilterBar
            categories={categories}
            countries={availableCountries}
            selectedRegion={selectedRegion}
            selectedCountry={selectedCountry}
            selectedCategory={selectedCategory}
            onRegionChange={handleRegionChange}
            onCountryChange={setSelectedCountry}
            onCategoryChange={setSelectedCategory}
            onClearFilters={handleClearFilters}
          />

          {/* Main Body */}
          <div className="flex-1 flex flex-col md:flex-row relative overflow-hidden">
            {/* Error Notification Bar */}
            {!isConnected && (
              <div className="absolute top-2 left-1/2 -translate-x-1/2 z-[2000] bg-rose-900/90 text-rose-100 px-4 py-2 rounded-lg shadow-xl border border-rose-600 flex items-center space-x-2 text-xs md:text-sm">
                <AlertTriangle className="w-4 h-4 text-amber-300 flex-shrink-0" />
                <span>Unable to connect to World News server. Displaying cached data.</span>
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
              <div className="absolute inset-0 z-[3000] bg-slate-950/80 backdrop-blur-sm flex flex-col items-center justify-center space-y-3">
                <div className="w-10 h-10 border-4 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
                <p className="text-sm font-medium text-slate-300">Loading World Events...</p>
              </div>
            )}

            {/* Desktop View (>= 768px): Split Sidebar & Map */}
            {!isMobile && (
              <>
                <EventList
                  events={filteredEvents}
                  selectedEventId={selectedEvent?.id || null}
                  onSelectEvent={handleSelectEvent}
                  searchQuery={searchQuery}
                  onSearchChange={setSearchQuery}
                  sortMode={sortMode}
                  onSortChange={setSortMode}
                />

                <div className="flex-1 h-full relative">
                  <MapView
                    events={filteredEvents}
                    selectedEvent={selectedEvent}
                    onSelectEvent={handleSelectEvent}
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
              </>
            )}

            {/* Mobile View (< 768px): UX-005 Fullscreen Map + Bottom Sheet Drawer */}
            {isMobile && (
              <div className="flex-1 h-full w-full relative overflow-hidden">
                <MapView
                  events={filteredEvents}
                  selectedEvent={selectedEvent}
                  onSelectEvent={handleSelectEvent}
                  resetViewTrigger={resetViewTrigger}
                />

                {/* Mobile Bottom Sheet Drawer */}
                <div
                  className={`absolute left-0 right-0 bottom-0 z-[1500] bg-slate-850 bg-slate-900/95 border-t border-slate-700 rounded-t-2xl shadow-2xl transition-all duration-300 flex flex-col ${
                    bottomSheetState === 'collapsed'
                      ? 'h-14'
                      : bottomSheetState === 'half'
                      ? 'h-[50vh]'
                      : 'h-[85vh]'
                  }`}
                >
                  {/* Bottom Sheet Handle */}
                  <div
                    onClick={() => {
                      if (selectedEvent) {
                        setSelectedEvent(null);
                        setBottomSheetState('half');
                      } else {
                        setBottomSheetState(
                          bottomSheetState === 'collapsed'
                            ? 'half'
                            : bottomSheetState === 'half'
                            ? 'full'
                            : 'collapsed'
                        );
                      }
                    }}
                    className="py-2.5 px-4 cursor-pointer flex items-center justify-between border-b border-slate-800 bg-slate-850 rounded-t-2xl flex-shrink-0"
                  >
                    <div className="flex items-center space-x-2 text-xs font-bold text-slate-200">
                      <ListFilter className="w-4 h-4 text-sky-400" />
                      <span>
                        {selectedEvent
                          ? selectedEvent.location_name || 'Event Detail'
                          : `Active Events (${filteredEvents.length})`}
                      </span>
                    </div>
                    <div className="flex items-center text-slate-400">
                      {bottomSheetState === 'collapsed' ? (
                        <ChevronUp className="w-5 h-5 text-sky-400" />
                      ) : (
                        <ChevronDown className="w-5 h-5" />
                      )}
                    </div>
                  </div>

                  {/* Bottom Sheet Body */}
                  <div className="flex-1 overflow-hidden relative">
                    {selectedEvent ? (
                      <EventDetailPanel
                        event={selectedEvent}
                        onClose={() => setSelectedEvent(null)}
                        isMobile={true}
                      />
                    ) : (
                      <EventList
                        events={filteredEvents}
                        selectedEventId={null}
                        onSelectEvent={handleSelectEvent}
                        searchQuery={searchQuery}
                        onSearchChange={setSearchQuery}
                        sortMode={sortMode}
                        onSortChange={setSortMode}
                      />

                    )}
                  </div>
                </div>
              </div>
            )}
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
