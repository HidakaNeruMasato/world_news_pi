/** Region mapping & taxonomy utility for World News Map (T022-2) */

import { ActiveEvent } from '../types/event';

export const REGION_NAMES = [
  'All',
  'Africa',
  'Asia',
  'Europe',
  'Middle East',
  'Americas',
  'Oceania'
] as const;

export type RegionName = (typeof REGION_NAMES)[number];

// ISO 2-letter Country Code to Region taxonomy mapping
const COUNTRY_TO_REGION: Record<string, string> = {
  // Africa
  NG: 'Africa', ZA: 'Africa', KE: 'Africa', EG: 'Africa', MA: 'Africa',
  ET: 'Africa', GH: 'Africa', TZ: 'Africa', UG: 'Africa', DZ: 'Africa',
  TN: 'Africa', SD: 'Africa', CM: 'Africa', CI: 'Africa', AO: 'Africa',
  MZ: 'Africa', ZW: 'Africa', SN: 'Africa', LY: 'Africa', SS: 'Africa',
  // Asia
  JP: 'Asia', CN: 'Asia', KR: 'Asia', IN: 'Asia', PK: 'Asia',
  SG: 'Asia', PH: 'Asia', ID: 'Asia', MY: 'Asia', TH: 'Asia',
  VN: 'Asia', MM: 'Asia', BD: 'Asia', LK: 'Asia', NP: 'Asia',
  TW: 'Asia', HK: 'Asia', KH: 'Asia', LA: 'Asia', AF: 'Asia',
  // Europe
  GB: 'Europe', FR: 'Europe', DE: 'Europe', IT: 'Europe', ES: 'Europe',
  RS: 'Europe', RO: 'Europe', PL: 'Europe', UA: 'Europe', RU: 'Europe',
  NL: 'Europe', BE: 'Europe', CH: 'Europe', SE: 'Europe', NO: 'Europe',
  FI: 'Europe', GR: 'Europe', PT: 'Europe', CZ: 'Europe', HU: 'Europe',
  AT: 'Europe', IE: 'Europe', DK: 'Europe', BG: 'Europe', HR: 'Europe',
  // Middle East
  QA: 'Middle East', IL: 'Middle East', SA: 'Middle East', AE: 'Middle East',
  TR: 'Middle East', IR: 'Middle East', IQ: 'Middle East', SY: 'Middle East',
  JO: 'Middle East', LB: 'Middle East', KW: 'Middle East', OM: 'Middle East',
  YE: 'Middle East', BH: 'Middle East', PS: 'Middle East',
  // Americas
  US: 'Americas', CA: 'Americas', MX: 'Americas', AR: 'Americas', UY: 'Americas',
  BR: 'Americas', CL: 'Americas', CO: 'Americas', PE: 'Americas', GT: 'Americas',
  CR: 'Americas', PA: 'Americas', SV: 'Americas', HN: 'Americas', NI: 'Americas',
  EC: 'Americas', VE: 'Americas', BO: 'Americas', PY: 'Americas', DO: 'Americas',
  // Oceania
  AU: 'Oceania', NZ: 'Oceania', FJ: 'Oceania', PG: 'Oceania', SB: 'Oceania',
  VU: 'Oceania', WS: 'Oceania', TO: 'Oceania'
};

// Region Center Coordinates for map flyTo
export const REGION_BOUNDS: Record<string, { lat: number; lon: number; zoom: number }> = {
  Africa: { lat: 2.0, lon: 16.0, zoom: 3.5 },
  Asia: { lat: 28.0, lon: 85.0, zoom: 3.5 },
  Europe: { lat: 50.0, lon: 15.0, zoom: 4.0 },
  'Middle East': { lat: 29.0, lon: 45.0, zoom: 4.5 },
  Americas: { lat: 10.0, lon: -75.0, zoom: 3.0 },
  Oceania: { lat: -25.0, lon: 135.0, zoom: 4.0 }
};

/** Determines the region name for an active event based on region property or country code */
export function getEventRegion(event: ActiveEvent): string {
  if (event.region) {
    const regLower = event.region.toLowerCase();
    if (regLower.includes('africa')) return 'Africa';
    if (regLower.includes('asia')) return 'Asia';
    if (regLower.includes('europe')) return 'Europe';
    if (regLower.includes('middle east')) return 'Middle East';
    if (regLower.includes('america')) return 'Americas';
    if (regLower.includes('oceania') || regLower.includes('pacific')) return 'Oceania';
  }
  if (event.event_country) {
    const mapped = COUNTRY_TO_REGION[event.event_country.toUpperCase()];
    if (mapped) return mapped;
  }
  return 'Other';
}

/** Computes regional active event distribution count map */
export function computeRegionalCounts(events: ActiveEvent[]): Record<string, number> {
  const counts: Record<string, number> = {
    Africa: 0,
    Asia: 0,
    Europe: 0,
    'Middle East': 0,
    Americas: 0,
    Oceania: 0
  };

  events.forEach((evt) => {
    const reg = getEventRegion(evt);
    if (reg in counts) {
      counts[reg] += 1;
    }
  });

  return counts;
}
