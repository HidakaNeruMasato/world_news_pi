# World News Map — Target Information Architecture (T022-1)

## 1. Core Principles
1. **Map as Primary Surface**: The interactive World Map remains the core interface for news exploration.
2. **Unified Global Overview**: Integrate top-level regional and event volume indicators above/alongside the map rather than hiding them in a separate Dashboard tab.
3. **Strict 3-Way State Synchronization**: Selected Event ID is synchronized across Map, Event List, and Event Detail Panel.
4. **Clean Information Hierarchy**: Primary (Map + Selected Event Title), Secondary (Region, Country, Category, Occurred Time, Confidence), Tertiary (Publisher Sources, External Links, System Telemetry).

## 2. Target IA Tree

```text
World News Map (App Root)
│
├── Top Global Header
│   ├── Application Title & Live Indicator
│   ├── Compact Global Stats Banner (Active Events, Regional Breakdown Badges)
│   ├── View Mode Toggle (Map Overview vs Full Pipeline Telemetry)
│   └── Manual Refresh & View Reset Controls
│
├── Global Filter Bar
│   ├── Region Filter Dropdown (All, Africa, Asia, Europe, Middle East, Americas, Oceania)
│   ├── Country Filter Dropdown (Filtered by selected Region)
│   ├── Category Filter Dropdown (Disaster, Politics, Conflict, Economy, etc.)
│   └── Clear Filters Button
│
├── Main Interactive View Area
│   ├── Left Sidebar: Event List
│   │   ├── List Header (Filtered Event Count, Search Input)
│   │   └── Event Cards
│   │       ├── Category Badge & Time Decay Indicator
│   │       ├── Location Name & Country Code
│   │       ├── Article Count Badge (for Multi-Article Events)
│   │       └── Confidence Score (%)
│   │
│   └── Center Canvas: World Map (MapView)
│       ├── Zoom Controls & Scale Indicator
│       ├── Region Aggregation & Zoom-Dependent Density Handling
│       ├── Category Circle Markers (Decay Opacity, Selection Pulse)
│       └── Selected Event Marker Highlight
│
└── Event Detail Panel (Right Sidebar on Desktop / Bottom Sheet on Mobile)
    ├── Panel Header (Location Title, Category Badge, Close Button)
    ├── Event Overview Card (Country, Region, City, Coordinates, Confidence, Status)
    ├── Timestamp Breakdown (Occurred At, Last Updated, Expires At)
    └── Related News Articles Section
        ├── Article Count & Publisher Count Summary
        └── Article Cards
            ├── Headline Title
            ├── Publisher Name & Source Country Flag
            └── Direct Link to Original Article ("Read Source")
```

## 3. Data Flow & Synchronization Contract
- **Selecting an Event**:
  1. Click Marker on Map OR Click Card in Event List.
  2. `selectedEventId` state updates globally.
  3. Map centers smoothly on event coordinates (`flyTo`).
  4. Event List scrolls selected item into view with visual highlight border.
  5. Event Detail Panel opens displaying detailed article breakdown.
- **Applying Filters**:
  1. User changes Region, Country, or Category in FilterBar.
  2. Map markers and Event List update synchronously.
  3. Active count in StatusBar updates immediately.
