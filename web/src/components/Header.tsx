import React from 'react';
import { Globe, RefreshCw, RotateCcw, LayoutDashboard, Map as MapIcon } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  onResetView: () => void;
  isRefreshing: boolean;
  activeTab: 'map' | 'dashboard';
  onTabChange: (tab: 'map' | 'dashboard') => void;
  totalEvents: number;
  regionalCounts: Record<string, number>;
  onSelectRegionPill: (region: string) => void;
  selectedRegion: string;
}

export const Header: React.FC<HeaderProps> = ({
  onRefresh,
  onResetView,
  isRefreshing,
  activeTab,
  onTabChange,
  totalEvents,
  regionalCounts,
  onSelectRegionPill,
  selectedRegion,
}) => {
  const regions = [
    { name: 'Africa', count: regionalCounts['Africa'] || 0 },
    { name: 'Asia', count: regionalCounts['Asia'] || 0 },
    { name: 'Europe', count: regionalCounts['Europe'] || 0 },
    { name: 'Middle East', count: regionalCounts['Middle East'] || 0 },
    { name: 'Americas', count: regionalCounts['Americas'] || 0 },
    { name: 'Oceania', count: regionalCounts['Oceania'] || 0 },
  ];

  return (
    <header className="bg-slate-800 border-b border-slate-700 shadow-md">
      {/* Primary Top Bar */}
      <div className="px-4 py-2.5 flex items-center justify-between gap-3">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            <Globe className="w-5 h-5 text-sky-400 animate-pulse" />
            <h1 className="text-base md:text-lg font-bold tracking-wide text-white flex items-center gap-1.5">
              WORLD NEWS MAP
              <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">
                LIVE
              </span>
            </h1>
          </div>

          {/* View Mode Switcher */}
          <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs">
            <button
              onClick={() => onTabChange('map')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${
                activeTab === 'map' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <MapIcon className="w-3.5 h-3.5" />
              <span>Map View</span>
            </button>
            <button
              onClick={() => onTabChange('dashboard')}
              className={`flex items-center space-x-1 px-2.5 py-1 rounded font-semibold transition ${
                activeTab === 'dashboard' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <LayoutDashboard className="w-3.5 h-3.5" />
              <span>Analytics</span>
            </button>
          </div>
        </div>

        {/* Top Actions */}
        <div className="flex items-center space-x-2">
          {activeTab === 'map' && (
            <button
              onClick={onResetView}
              className="flex items-center space-x-1 text-xs bg-slate-700 hover:bg-slate-600 text-slate-200 px-2.5 py-1.5 rounded transition font-medium"
              title="Reset World View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
              <span className="hidden md:inline">Reset View</span>
            </button>
          )}
          <button
            onClick={onRefresh}
            disabled={isRefreshing}
            className="flex items-center space-x-1 text-xs bg-sky-600 hover:bg-sky-500 text-white px-3 py-1.5 rounded transition font-semibold disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
            <span>Refresh</span>
          </button>
        </div>
      </div>

      {/* UX-006: Integrated Global Overview Strip */}
      {activeTab === 'map' && (
        <div className="bg-slate-900/90 border-t border-slate-700/60 px-4 py-1.5 flex items-center justify-between text-xs overflow-x-auto gap-4">
          <div className="flex items-center space-x-2 text-slate-300 font-semibold flex-shrink-0">
            <span className="text-sky-400 font-mono text-sm font-bold">{totalEvents}</span>
            <span className="text-slate-400 text-[11px] uppercase tracking-wider">Active Events</span>
          </div>

          <div className="flex items-center space-x-2 flex-shrink-0">
            <span className="text-slate-400 text-[11px] font-medium hidden sm:inline">Regions:</span>
            {regions.map((reg) => {
              const isSelected = selectedRegion === reg.name;
              return (
                <button
                  key={reg.name}
                  onClick={() => onSelectRegionPill(reg.name)}
                  className={`px-2 py-0.5 rounded text-[11px] font-medium transition flex items-center space-x-1 border ${
                    isSelected
                      ? 'bg-sky-600 text-white border-sky-400 shadow'
                      : 'bg-slate-800 text-slate-300 border-slate-700 hover:bg-slate-700'
                  }`}
                >
                  <span>{reg.name}</span>
                  <span className="font-mono text-[10px] bg-slate-950/50 px-1 rounded text-sky-300 font-bold">
                    {reg.count}
                  </span>
                </button>
              );
            })}
          </div>
        </div>
      )}
    </header>
  );
};
