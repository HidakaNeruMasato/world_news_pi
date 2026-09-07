# World News Map — Current UI Inventory (T022-1 Audit)

This document provides a comprehensive inventory of all Web UI components, their purpose, data sources, user actions, and current UX issues identified during the T022-1 audit.

| Area | Component | Purpose | Data Source | User Action | Current Issue |
|---|---|---|---|---|---|
| Header | `Header.tsx` | Top navigation, logo, tab switching (Map/Dashboard), manual refresh, reset view | Props | Click tab, click refresh, click reset view | Tab switching completely hides Map when Dashboard is active. No unified view option. |
| Filter | `FilterBar.tsx` | Category and Country filtering | Derived from active events (`categories`, `countries`) | Select Category dropdown, Select Country dropdown | Missing Region filter despite T021 expanding 8 global regions. Dropdown values lack event count indicators. |
| Map Canvas | `MapView.tsx` | Interactive world map with Leaflet circle markers | `/api/events/active` via props | Click marker, pan, zoom, reset view | Dense event markers (e.g. 200+ events) severely overlap in Europe, East Asia, and South Asia. No marker clustering or zoom-dependent aggregation. |
| Event List | `EventList.tsx` | Sidebar listing active events | `/api/events/active` via props | Click event item to select | Occupies fixed 320px sidebar width on desktop; stacks vertically on mobile without collapsing. Lacks region filter or search bar. |
| Event Detail | `EventDetailPanel.tsx` | Overlay panel showing event metadata & related articles | `/api/events/{id}/articles` | Click close (X), click article link | Positioned as floating overlay on top-right of map; can obscure map markers on smaller desktop screens and covers entire map on mobile viewports. |
| Dashboard | `DashboardView.tsx` | Pipeline telemetry & regional statistics dashboard | `/api/dashboard/*` | Period selector (24h/48h/7d), Click region to open Map | Completely replaces Map view when selected. Combines user-facing news metrics with operational pipeline health (RSS failures, queue retries). |
| Status Bar | `StatusBar.tsx` | Footer bar showing active event count, connection status, last updated time | Props (`activeCount`, `lastUpdated`, `isConnected`) | None (information display) | Compact info text; displays connection status banner in header overlay during API connection failures. |
