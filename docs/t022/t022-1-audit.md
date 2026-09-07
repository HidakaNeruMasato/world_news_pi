# T022-1 Repository & Web UI Architecture Audit Report

## Executive Summary
This document summarizes the repository structure audit, component mapping, and state management flow of the World News Map Web UI (`web/src/`) conducted during T022-1.

## 1. Web Source Directory Structure
```text
web/
├── package.json
├── index.html
├── vite.config.ts
└── src/
    ├── App.tsx                    # Root application container & tab router
    ├── main.tsx                   # React DOM entry point
    ├── index.css                  # Tailwind CSS imports & map styles
    ├── api/
    │   ├── client.ts              # FastAPI active events & articles client
    │   └── dashboardClient.ts     # T019 Dashboard telemetry API client
    ├── components/
    │   ├── Header.tsx             # Navigation header & tab bar
    │   ├── FilterBar.tsx          # Category & Country filter selectors
    │   ├── MapView.tsx            # Leaflet map canvas & circle markers
    │   ├── EventList.tsx          # Active event sidebar list
    │   ├── EventDetailPanel.tsx   # Floating event detail overlay
    │   ├── DashboardView.tsx      # Telemetry & regional dashboard
    │   └── StatusBar.tsx          # Footer status & connection indicator
    ├── types/
    │   └── event.ts               # ActiveEvent, Article, Dashboard types
    └── utils/
        └── time.ts                # Time decay opacity & relative formatting helpers
```

## 2. Component Dependency & Data Flow Matrix
- **State Source**: `App.tsx` holds top-level state: `events`, `selectedEvent`, `selectedCategory`, `selectedCountry`, `activeTab`.
- **API Fetching**:
  - `fetchActiveEvents()` in `api/client.ts` polls `/api/events/active` every 30 seconds.
  - `fetchEventArticles(eventId)` in `api/client.ts` fetches `/api/events/{id}/articles` on demand when an event is selected.
  - `DashboardView.tsx` fetches `/api/dashboard/*` endpoints when the Dashboard tab is active.
- **Child Components**:
  - `MapView.tsx`: Pure Leaflet circle marker renderer.
  - `EventList.tsx`: Scrollable card list.
  - `EventDetailPanel.tsx`: Floating panel on map.
  - `FilterBar.tsx`: Controlled dropdown selectors.

## 3. Compliance Verification
- Production Backend / Pipeline Logic: **FROZEN** (0 changes).
- Production Database: **READ-ONLY** (`Production DB writes = 0`).
- AI Models / Prompts / Thresholds: **FROZEN** (0 changes).
- Existing Unit Tests: **PASS** (303/303 PASS).
