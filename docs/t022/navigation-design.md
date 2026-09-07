# World News Map — Navigation Design Specification (T022-1)

## 1. Primary Navigation Flow
```text
[Global Header]
  │
  ├── [Global Overview Strip] ─── Displays Active Event counts & Region badges
  │
  ├── [Filter Bar] ────────────── Region -> Country -> Category -> Search Text
  │
  └── [Split View / Canvas]
        │
        ├── [Left Sidebar: Event List] ───── Click card -> Map pans & Detail opens
        │
        ├── [Center: Map Canvas] ────────── Click marker -> List highlights & Detail opens
        │
        └── [Right Panel: Event Detail] ──── View articles -> Click external source link
```

## 2. Interactive Navigation Mechanics

### A. Map Marker Navigation
- Hover over marker: Displays compact tooltip with `Location Name | Category | Relative Time`.
- Click marker:
  1. Sets `selectedEvent` state.
  2. Smoothly flies map camera to `[latitude, longitude]` at zoom level 7.
  3. Highlights marker with enlarged radius (12px) and white border ring.
  4. Scrolls corresponding item in Event List into view.
  5. Opens Event Detail Panel.

### B. Event List Navigation
- Hover over card: Highlights card border.
- Click card:
  1. Sets `selectedEvent` state.
  2. Flies map camera to marker coordinates.
  3. Opens Event Detail Panel.

### C. Dashboard to Map Region Jump
- In Dashboard or Regional Overview: Clicking a region card (e.g. "Africa") switches view to Map, applies `Region = Africa` filter, and flies map camera to Africa regional bounds (`[0.0, 20.0]`, zoom 3.5).

### D. Keyboard Accessibility Shortcuts
- `ESC`: Closes Event Detail Panel & deselects active event.
- `R`: Triggers manual data refresh.
- `F`: Focuses filter/search bar.
- `TAB / Shift+TAB`: Navigates through list cards and control buttons smoothly.
