import React from 'react';
import { Globe, RefreshCw, RotateCcw, LayoutDashboard, Map as MapIcon } from 'lucide-react';

interface HeaderProps {
  onRefresh: () => void;
  onResetView: () => void;
  isRefreshing: boolean;
  activeTab: 'map' | 'dashboard';
  onTabChange: (tab: 'map' | 'dashboard') => void;
}

export const Header: React.FC<HeaderProps> = ({
  onRefresh,
  onResetView,
  isRefreshing,
  activeTab,
  onTabChange
}) => {
  return (
    <header className="bg-slate-800 border-b border-slate-700 px-4 py-3 flex items-center justify-between shadow-md">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-2">
          <Globe className="w-6 h-6 text-sky-400 animate-pulse" />
          <h1 className="text-lg md:text-xl font-bold tracking-wide text-white">
            WORLD NEWS MAP <span className="text-xs px-2 py-0.5 rounded bg-sky-500/20 text-sky-300 border border-sky-500/30">PROTOTYPE</span>
          </h1>
        </div>

        {/* View Switcher Tabs */}
        <div className="flex items-center bg-slate-900 border border-slate-700 rounded-lg p-0.5 text-xs">
          <button
            onClick={() => onTabChange('map')}
            className={`flex items-center space-x-1 px-3 py-1 rounded font-semibold transition ${
              activeTab === 'map' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <MapIcon className="w-3.5 h-3.5" />
            <span>Map View</span>
          </button>
          <button
            onClick={() => onTabChange('dashboard')}
            className={`flex items-center space-x-1 px-3 py-1 rounded font-semibold transition ${
              activeTab === 'dashboard' ? 'bg-sky-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            <LayoutDashboard className="w-3.5 h-3.5" />
            <span>Dashboard</span>
          </button>
        </div>
      </div>

      <div className="flex items-center space-x-2">
        {activeTab === 'map' && (
          <button
            onClick={onResetView}
            className="flex items-center space-x-1 text-xs md:text-sm bg-slate-700 hover:bg-slate-600 text-slate-200 px-3 py-1.5 rounded transition"
            title="Reset World View"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            <span className="hidden md:inline">Reset View</span>
          </button>
        )}
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center space-x-1 text-xs md:text-sm bg-sky-600 hover:bg-sky-500 text-white px-3 py-1.5 rounded transition disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin' : ''}`} />
          <span>Refresh</span>
        </button>
      </div>
    </header>
  );
};
