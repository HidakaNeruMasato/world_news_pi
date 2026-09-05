# T019 Web Dashboard Specification & Design

This document details the architecture, UI layout, components, and interaction patterns for the **World News Activity & Pipeline Funnel Dashboard** implemented in T019.

---

## 1. Component Architecture

```text
[Header.tsx]
  ├── Title & Version Badge
  ├── Active Tab Switcher ("Map View" | "Dashboard")
  └── Action Buttons (Reset View, Refresh)

[App.tsx] (Tab Router & Filter State)
  │
  ├──► [MapView.tsx] (Map View - Leaflet Map Canvas & Event Markers)
  │
  └──► [DashboardView.tsx] (Dashboard View - Analytics & Activity)
        ├── Explanatory Notice Banner ("News activity reflects monitored sources...")
        ├── Top 4 KPI Cards (Sources, New Articles, LLM Events, Active Map Events)
        ├── Regional News Activity Ranking & Bar Chart
        ├── Pipeline Funnel Reduction Visualizer (Stages 1..4)
        ├── Time Series Trend Chart (Hourly Map Events / Articles)
        └── Media Source Performance & Health Table
```

---

## 2. UI Layout Specifications

### Responsive Grid System
* **Desktop (≥ 1024px)**:
  * Top KPI Row: 4 columns.
  * Main Section: 2 columns for Regional Activity, 1 column for Pipeline Funnel.
  * Bottom Section: 2 columns for Time-series Trend, 1 column for Media Performance.
* **Mobile (< 768px)**:
  * Top KPI Row: 2 columns.
  * All charts and funnel sections collapse into single vertical column.

---

## 3. Interactive Behaviors

1. **Timeframe Selector**:
   * Controls period filtering (`24h`, `48h`, `7d`).
   * Clicking a timeframe updates all dashboard KPI cards, funnel metrics, regional ranking, time-series, and media performance asynchronously.
2. **Region Selection Navigation**:
   * Clicking any region item in the Regional Activity Ranking triggers `onSelectRegion(region)`.
   * Automatically switches the UI tab to **Map View** and applies the selected region filter.
3. **Graceful Outage Handling**:
   * If API connection fails during polling, dashboard displays cached data with a notification banner without wiping active metrics.
