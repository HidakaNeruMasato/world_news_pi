# T022-2 Implementation Specification: UI/UX & Information Architecture Refinement

## Document Purpose
This specification details the exact implementation requirements for T022-2. The implementing engineer/AI can proceed directly from this specification without needing additional design clarification.

---

## 1. Specification Items Overview

| ID | Title | Priority | Target Component | Main Change |
|---|---|:---:|---|---|
| UX-001 | Marker Density & Proximity Clustering | P1 | `MapView.tsx` | Cluster markers at zoom 2-4; expand at zoom 5+ |
| UX-002 | Global Region Filter & Taxonomy | P1 | `FilterBar.tsx` | Add Region dropdown (Africa, Asia, Europe, Middle East, Americas, Oceania) |
| UX-003 | 3-Way State Synchronization | P1 | `App.tsx`, `EventList.tsx` | Scroll selected item into view and elevate selected map marker |
| UX-004 | Multi-Article & Source Hierarchy | P1 | `EventDetailPanel.tsx`, `EventList.tsx` | Add multi-article badges & publisher source flags |
| UX-005 | Mobile Bottom-Sheet Layout | P1 | `App.tsx`, `EventList.tsx`, `EventDetailPanel.tsx` | Mobile Bottom-Sheet drawer for List & Detail |
| UX-006 | Integrated Global Overview Strip | P2 | `App.tsx`, `Header.tsx` | Add top overview strip with active event count & region pills |
| UX-007 | Event List Search & Sorting | P2 | `EventList.tsx` | Add text search input and sort selection |

---

## 2. Detailed Technical Specifications

### Item UX-001: Marker Density & Proximity Clustering
- **ID**: UX-001
- **Title**: Marker Density & Proximity Clustering
- **Priority**: P1
- **Current Behavior**: Renders individual circle markers (`L.circleMarker`) for every active event regardless of zoom level or marker overlap.
- **Problem**: Severe overlap in dense regions (Europe 50+, East Asia 40+, South Asia 55+) makes individual markers unclickable and obscures event counts.
- **User Impact**: Users cannot select underlying events in high-density areas.
- **Proposed Behavior**:
  - Integrate Leaflet marker clustering / proximity grouping for zoom levels 2 to 4.
  - Display cluster badge with total contained event count (e.g. `[12]`).
  - Tapping a cluster zooms in to expand markers (`zoom = 5+`).
  - At zoom level 5 and above, expand into individual category-colored circle markers at exact geocoded coordinates.
- **UI Location**: `web/src/components/MapView.tsx`
- **Required State**: `events: ActiveEvent[]`, `selectedEvent: ActiveEvent | null`
- **API Dependency**: None (`/api/events/active` schema unchanged).
- **Data Dependency**: `latitude`, `longitude`, `category`
- **Desktop Behavior**: Smooth Leaflet cluster markers with hover tooltips.
- **Mobile Behavior**: Larger tap target clusters (minimum 44x44px).
- **Acceptance Criteria**:
  1. 100+ events remain clean and navigable at global zoom level 2.5.
  2. Selecting an event within a cluster expands the cluster and highlights the selected marker.
  3. No event coordinates are altered or falsified (zero fake coordinate policy).
  4. Existing `/api/events/active` contract remains unchanged.
- **Regression Risk**: Low. Leaflet map rendering layer isolated to `MapView.tsx`.

---

### Item UX-002: Global Region Filter & Taxonomy
- **ID**: UX-002
- **Title**: Global Region Filter & Taxonomy
- **Priority**: P1
- **Current Behavior**: `FilterBar.tsx` only offers Category and Country dropdowns.
- **Problem**: Following T021 Phase 3 RSS expansion across 8 world regions, users looking for specific regional news (e.g. Africa or South America) must scroll through all global events manually.
- **User Impact**: Impairs discoverability of news in newly expanded regions.
- **Proposed Behavior**:
  - Add `Region` dropdown to `FilterBar.tsx` with options: `All Regions`, `Africa`, `Asia`, `Europe`, `Middle East`, `North America`, `South America`, `Oceania`, `Central America`.
  - Selecting a Region filters the Event List and Map markers, and cascades available options in the `Country` dropdown to matching countries within that region.
- **UI Location**: `web/src/components/FilterBar.tsx`, `web/src/App.tsx`
- **Required State**: `selectedRegion`, `selectedCountry`, `selectedCategory`
- **API Dependency**: None (Client-side region mapping derived from `event_country` or `region` fields).
- **Data Dependency**: `ActiveEvent.region`, `ActiveEvent.event_country`
- **Desktop Behavior**: Horizontal inline select box in `FilterBar`.
- **Mobile Behavior**: Horizontal scrolling filter strip with touch-friendly select boxes.
- **Acceptance Criteria**:
  1. Selecting `Africa` immediately filters the map and list to show only events in African countries/regions.
  2. Selecting `All Regions` resets the regional filter.
  3. Active event counts in `StatusBar` update immediately.
- **Regression Risk**: None.

---

### Item UX-003: 3-Way State Synchronization
- **ID**: UX-003
- **Title**: 3-Way State Synchronization (Map <-> List <-> Detail)
- **Priority**: P1
- **Current Behavior**: Selecting an event from Map updates `selectedEvent` and opens `EventDetailPanel`, but `EventList` does not automatically scroll the selected card into view.
- **Problem**: Disconnect between sidebar list position and selected map marker.
- **User Impact**: User loses track of which list item corresponds to the selected map marker.
- **Proposed Behavior**:
  - When `selectedEvent` changes (from Map marker click OR List item click):
    1. Map camera smoothly pans/zooms to `[latitude, longitude]`.
    2. Selected Marker style updates with pulsing ring or enlarged radius (12px, white border).
    3. `EventList` automatically scrolls selected item into view (`scrollIntoView({ behavior: 'smooth', block: 'nearest' })`).
    4. `EventDetailPanel` opens displaying related articles.
- **UI Location**: `web/src/App.tsx`, `web/src/components/EventList.tsx`, `web/src/components/MapView.tsx`
- **Required State**: `selectedEvent: ActiveEvent | null`
- **API Dependency**: None.
- **Data Dependency**: `ActiveEvent.id`
- **Desktop Behavior**: Smooth scroll in list container + Leaflet `flyTo`.
- **Mobile Behavior**: Smooth scroll + Bottom Sheet focus.
- **Acceptance Criteria**:
  1. Clicking any map marker automatically scrolls the corresponding card in `EventList` into view.
  2. Clicking any card in `EventList` centers the map camera on the marker.
  3. Deselecting (`ESC` or Close button) clears highlights across all 3 components.
- **Regression Risk**: Low.

---

### Item UX-004: Multi-Article & Source Hierarchy
- **ID**: UX-004
- **Title**: Multi-Article & Source Hierarchy
- **Priority**: P1
- **Current Behavior**: `EventList` cards display title, category, and time, but do not show article count. `EventDetailPanel` lists related articles as plain text blocks.
- **Problem**: Multi-Article events (which represent 56% of production events) look identical to single-article events in the list.
- **User Impact**: Users cannot easily identify major events covered by multiple international publishers.
- **Proposed Behavior**:
  - In `EventList`: Display a prominent badge `[N Articles]` (e.g. `3 Articles`) for events with `article_count > 1`.
  - In `EventDetailPanel`: Show a summary header `Covered by N Media Sources (e.g. BBC, Reuters, Premium Times)` and style article links with clear publisher tags and source country badges.
- **UI Location**: `web/src/components/EventList.tsx`, `web/src/components/EventDetailPanel.tsx`
- **Required State**: `event.article_count`, `article.source_name`, `article.source_country`
- **API Dependency**: `/api/events/{id}/articles` (schema already contains `source_name`, `url`, `title`).
- **Data Dependency**: `Article.source_name`, `Article.url`
- **Desktop & Mobile Behavior**: Clean card layout with external link icon.
- **Acceptance Criteria**:
  1. Events with > 1 article show `N Articles` badge in `EventList`.
  2. Related articles display publisher source name and valid external links.
- **Regression Risk**: None.

---

### Item UX-005: Mobile Bottom-Sheet Layout
- **ID**: UX-005
- **Title**: Mobile Bottom-Sheet Layout
- **Priority**: P1
- **Current Behavior**: On screens `< 768px`, `EventList` stacks above `MapView`, and `EventDetailPanel` covers the entire screen.
- **Problem**: Destroys map exploration experience on mobile devices.
- **User Impact**: Mobile users cannot interact with the map effectively.
- **Proposed Behavior**:
  - On screens `< 768px`, render Map Canvas full screen.
  - Provide a draggable/collapsible **Bottom Sheet** drawer:
    - Collapsed: Displays compact summary bar `Active Events (135) - Drag up`.
    - Half-Expanded: Displays scrollable `EventList`.
    - Event Selected: Displays `EventDetailPanel` content in the Bottom Sheet with a Back button.
- **UI Location**: `web/src/App.tsx`, `web/src/components/EventList.tsx`, `web/src/components/EventDetailPanel.tsx`
- **Required State**: `isMobile`, `bottomSheetState: 'collapsed' | 'half' | 'full'`
- **API Dependency**: None.
- **Data Dependency**: Screen viewport width (`window.innerWidth < 768`).
- **Desktop Behavior**: Unchanged side-by-side split layout.
- **Mobile Behavior**: Interactive Bottom Sheet overlay.
- **Acceptance Criteria**:
  1. On mobile viewports (390px width), map canvas is visible by default.
  2. Tapping a map marker slides up the Bottom Sheet displaying event detail.
  3. Dragging or tapping the drag handle expands/collapses the event list.
- **Regression Risk**: Low. Styled via CSS media queries / responsive container wrapper.

---

### Item UX-006: Integrated Global Overview Strip
- **ID**: UX-006
- **Title**: Integrated Global Overview Strip
- **Priority**: P2
- **Current Behavior**: User must switch to the `Dashboard` tab to see regional event distributions.
- **Problem**: Violates "Map is primary surface" principle by obscuring the map during high-level exploration.
- **Proposed Behavior**: Add a compact Overview Strip below the Header containing: `Active Events: 135` | `Africa: 51` | `Asia: 55` | `Europe: 33` | `Middle East: 44` | `Americas: 58` | `Oceania: 26`. Clicking any region pill applies the Region filter and zooms to that continent.
- **UI Location**: `web/src/App.tsx`, `web/src/components/Header.tsx`
- **Acceptance Criteria**: Region pills show live active event counts and filter map/list on click.

---

### Item UX-007: Event List Search & Sorting
- **ID**: UX-007
- **Title**: Event List Search & Sorting
- **Priority**: P2
- **Current Behavior**: No search bar or sorting options in `EventList`.
- **Proposed Behavior**: Add text search input (`Filter by keyword, city, country...`) and sort dropdown (`Newest First`, `Highest Confidence`, `Most Articles`).
- **UI Location**: `web/src/components/EventList.tsx`
- **Acceptance Criteria**: Typing "Nigeria" in search bar instantly filters `EventList` and Map markers to matching items.
