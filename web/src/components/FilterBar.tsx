import React from 'react';
import { Filter } from 'lucide-react';

interface FilterBarProps {
  categories: string[];
  countries: string[];
  selectedCategory: string;
  selectedCountry: string;
  onCategoryChange: (cat: string) => void;
  onCountryChange: (country: string) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({
  categories,
  countries,
  selectedCategory,
  selectedCountry,
  onCategoryChange,
  onCountryChange,
}) => {
  return (
    <div className="bg-slate-850 bg-slate-800/80 border-b border-slate-700/60 px-4 py-2 flex items-center space-x-3 text-xs overflow-x-auto">
      <div className="flex items-center text-slate-400 font-medium">
        <Filter className="w-3.5 h-3.5 mr-1" />
        <span>Filter:</span>
      </div>

      <div className="flex items-center space-x-2">
        <label className="text-slate-400">Category:</label>
        <select
          value={selectedCategory}
          onChange={(e) => onCategoryChange(e.target.value)}
          className="bg-slate-700 text-slate-200 border border-slate-600 rounded px-2 py-1 focus:outline-none focus:border-sky-500"
        >
          <option value="ALL">All Categories</option>
          {categories.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>

      <div className="flex items-center space-x-2">
        <label className="text-slate-400">Country:</label>
        <select
          value={selectedCountry}
          onChange={(e) => onCountryChange(e.target.value)}
          className="bg-slate-700 text-slate-200 border border-slate-600 rounded px-2 py-1 focus:outline-none focus:border-sky-500"
        >
          <option value="ALL">All Countries</option>
          {countries.map((c) => (
            <option key={c} value={c}>
              {c}
            </option>
          ))}
        </select>
      </div>
    </div>
  );
};
