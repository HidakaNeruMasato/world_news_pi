import React from 'react';
import { Wifi, WifiOff } from 'lucide-react';

interface StatusBarProps {
  activeCount: number;
  lastUpdated: string | null;
  isConnected: boolean;
}

export const StatusBar: React.FC<StatusBarProps> = ({ activeCount, lastUpdated, isConnected }) => {
  return (
    <div className="bg-slate-800 border-t border-slate-700 px-4 py-2 text-xs text-slate-400 flex flex-wrap items-center justify-between gap-2 shadow-inner">
      <div className="flex items-center space-x-4">
        <span>
          Active Events: <strong className="text-sky-400">{activeCount}</strong>
        </span>
        <span>
          Last Updated: <span className="text-slate-300">{lastUpdated || 'Never'}</span>
        </span>
      </div>

      <div className="flex items-center space-x-2">
        {isConnected ? (
          <span className="flex items-center text-emerald-400 font-medium">
            <Wifi className="w-3.5 h-3.5 mr-1" /> API Connected
          </span>
        ) : (
          <span className="flex items-center text-rose-400 font-medium">
            <WifiOff className="w-3.5 h-3.5 mr-1 animate-bounce" /> Connection Error
          </span>
        )}
      </div>
    </div>
  );
};
