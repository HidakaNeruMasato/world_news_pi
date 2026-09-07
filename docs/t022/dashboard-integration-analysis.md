# World News Map — Dashboard Integration Architecture Analysis (T022-1)

## 1. Evaluation of Dashboard Integration Options

### Option A — Completely Separate Tabs (Current Implementation)
- **Description**: Header tabs `[Map | Dashboard]` switch between standalone full-screen views.
- **Pros**: Clean separation of code. Full screen available for Dashboard charts.
- **Cons**: Hides Map when user views Dashboard. Forces mode-switching cognitive load.

### Option B — Floating Dashboard Strip / Banner on Map
- **Description**: Compact dashboard overlay bar positioned at the top of the map.
- **Pros**: Map remains visible at all times.
- **Cons**: Clutters map canvas; limited space for complex charts like timeseries and funnel.

### Option C — Integrated Overview Header + Map + Expandable Analytics Drawer (Recommended)
- **Description**: Integrate top-level Global Overview (Active Events, Regional Pills with event count badges) directly above the Map. Clicking "Pipeline Analytics" opens a collapsible drawer/modal with deep T019 telemetry.
- **Pros**: Preserves "Map is the primary surface" principle. Immediate visibility of global activity without losing map context. Deep operational analytics remain accessible on demand.
- **Cons**: Requires minor layout reorganization in Header/Overview strip.

## 2. Comparison Matrix

| Criteria | Option A (Current) | Option B (Overlay Strip) | Option C (Integrated Overview - Recommended) |
|---|:---:|:---:|:---:|
| **Map Primary Principle** | Medium | High | **High (Top Priority)** |
| **First Impression (0-3s)** | Good | Medium | **Excellent (Immediate counts & map)** |
| **Information Density** | High | Low | **Optimal (Layered)** |
| **Mobile Usability** | Medium | Low | **High (Clean breakdown)** |
| **Operational Telemetry Isolation** | High | Low | **High (Drawer/Tab for Admin)** |

## 3. Recommendation & Decision
Select **Option C**:
- Place a **Compact Global Overview Strip** above the FilterBar showing `Active Events (135)`, `Regions Active (8)`, and clickable region badges (e.g. `Africa: 51`, `Asia: 55`, `Europe: 33`).
- Keep full T019 Pipeline Analytics (Funnel, Source Health, Timeseries) accessible via an "Analytics" button in the Header.
