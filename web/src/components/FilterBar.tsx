import React from 'react';
import { Filter, RotateCcw } from 'lucide-react';
import { REGION_NAMES } from '../utils/region';

interface FilterBarProps {
  categories: string[];
  countries: string[];
  selectedRegion: string;
  selectedCountry: string;
  selectedCategory: string;
  onRegionChange: (region: string) => void;
  onCountryChange: (country: string) => void;
  onCategoryChange: (cat: string) => void;
  onClearFilters: () => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  categories,
  countries,
  selectedRegion,
  selectedCountry,
  selectedCategory,
  onRegionChange,
  onCountryChange,
  onCategoryChange,
  onClearFilters,
}) => {
  const hasActiveFilter = selectedRegion !== 'All' || selectedCountry !== 'ALL' || selectedCategory !== 'ALL';

  return (
    <div className="bg-slate-850 bg-slate-800/90 border-b border-slate-700/60 px-4 py-2 flex items-center justify-between text-xs overflow-x-auto gap-3">
      <div className="flex items-center space-x-3 flex-wrap gap-y-2">
        <div className="flex items-center text-slate-400 font-medium">
          <Filter className="w-3.5 h-3.5 mr-1 text-sky-400" />
          <span>Filters:</span>
        </div>

        {/* Region Filter Dropdown (UX-002) */}
        <div className="flex items-center space-x-1.5">
          <label className="text-slate-400 font-medium">Region:</label>
          <select
            value={selectedRegion}
            onChange={(e) => onRegionChange(e.target.value)}
            className="bg-slate-700 text-slate-200 border border-slate-600 rounded px-2.5 py-1 focus:outline-none focus:border-sky-500 font-medium"
          >
            {REGION_NAMES.map((r) => (
              <option key={r} value={r}>
                {r === 'All' ? 'All Regions' : r}
              </option>
            ))}
          </select>
        </div>

        {/* Cascading Country Filter Dropdown */}
        <div className="flex items-center space-x-1.5">
          <label className="text-slate-400 font-medium">Country:</label>
          <select
            value={selectedCountry}
            onChange={(e) => onCountryChange(e.target.value)}
            className="bg-slate-700 text-slate-200 border border-slate-600 rounded px-2.5 py-1 focus:outline-none focus:border-sky-500 font-medium"
          >
            <option value="ALL">All Countries ({countries.length})</option>
            {countries.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </div>

        {/* Category Filter Dropdown */}
        <div className="flex items-center space-x-1.5">
          <label className="text-slate-400 font-medium">Category:</label>
          <select
            value={selectedCategory}
            onChange={(e) => onCategoryChange(e.target.value)}
            className="bg-slate-700 text-slate-200 border border-slate-600 rounded px-2.5 py-1 focus:outline-none focus:border-sky-500 font-medium"
          >
            <option value="ALL">All Categories</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c.toUpperCase()}
              </option>
            ))}
          </select>
        </div>
      </div>

      {/* Clear Filters Reset Button */}
      {hasActiveFilter && (
        <button
          onClick={onClearFilters}
          className="text-slate-400 hover:text-white bg-slate-700/60 hover:bg-slate-700 px-2 py-1 rounded transition flex items-center text-[11px] font-medium flex-shrink-0"
        >
          <RotateCcw className="w-3 h-3 mr-1" /> Reset Filters
        </button>
      )}
    </div>
  );
};
