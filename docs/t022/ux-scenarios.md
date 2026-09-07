# World News Map — UX Density & Production Scenario Evaluation (T022-1)

This report documents the UX evaluation of the current Web UI against 10 real-world production density scenarios (Scenarios A through J) following the T021 Phase 3 RSS expansion.

## Scenario Evaluation Summary

### Scenario A — World Overview (Default Zoom 2.5)
- **Description**: User opens the application showing global event distribution across 8 world regions.
- **Current UX Finding**: Displays 200+ circle markers across the map. Good initial visual impression of global activity, but lack of top-level summary metrics forces the user to scan the entire screen or switch to Dashboard.
- **Score**: 3 / 5

### Scenario B — Dense Events in Europe (50+ Events)
- **Description**: Zooming into Western & Eastern Europe with 50+ overlapping markers.
- **Current UX Finding**: High marker overlap. Circle markers obscure one another, making individual event selection difficult without zooming in significantly.
- **Score**: 2 / 5

### Scenario C — Dense Events in East Asia (40+ Events)
- **Description**: Dense concentration of news events across Japan, Korea, and China.
- **Current UX Finding**: Markers cluster tightly around major metropolitan areas (Tokyo, Seoul, Beijing). Selection by clicking markers requires high mouse precision.
- **Score**: 2 / 5

### Scenario D — Dense Events in Africa (50+ Events)
- **Description**: Newly expanded African news events across West Africa (Nigeria), East Africa (Kenya), and South Africa.
- **Current UX Finding**: Events are geographically spread out across the continent, but without a Region Filter, users looking specifically for African news must scroll manually through the unsorted sidebar list.
- **Score**: 3 / 5

### Scenario E — Co-Located / Adjacent Events in Same City
- **Description**: Multiple distinct events occurring within 10-30km of the same location (e.g. Lagos or Kyiv).
- **Current UX Finding**: Markers land directly on top of each other. The topmost marker receives clicks while underlying markers become unreachable on the map canvas.
- **Score**: 1 / 5

### Scenario F — Multi-Article Event (Article Count > 1)
- **Description**: Event covered by 3-5 distinct news articles.
- **Current UX Finding**: `EventDetailPanel` fetches and displays related articles in a vertical list. Shows title, source name, and external URL link. The hierarchy is clean, but multi-article event cards in `EventList` do not highlight article count prominently.
- **Score**: 4 / 5

### Scenario G — Cross-Border Multi-Publisher Reporting
- **Description**: Event in Nigeria reported by BBC Africa (GB), Premium Times (NG), and Reuters.
- **Current UX Finding**: Panel lists articles from different source countries. Clear presentation of publisher diversity, though source count breakdown is not summarized at the top of the detail panel.
- **Score": 4 / 5

### Scenario H — Low Event Volume (5-10 Active Events)
- **Description**: Off-peak period or filtered state resulting in few active events.
- **Current UX Finding**: Map looks clean and markers are easily clickable. Floating banner shows "No active events matching filter criteria" when 0 results match.
- **Score**: 4 / 5

### Scenario I — API Server Unavailable / Connection Lost
- **Description**: Backend server or network drops while user is navigating.
- **Current UX Finding**: Display banner "Unable to connect to World News server. Displaying last cached events" with Retry button. Previously loaded markers remain on map. Good error recovery UX.
- **Score**: 4 / 5

### Scenario J — Geocoding Unresolved / Country-Only Event
- **Description**: Event where location could not be pinpointed to a specific city/coordinates.
- **Current UX Finding**: Unresolved events have no lat/lon, so they do not render circle markers on MapView. They appear in `EventList` with "Unknown Location". Prevents fake coordinate placement (conforms to zero fake location principle).
- **Score**: 4 / 5
