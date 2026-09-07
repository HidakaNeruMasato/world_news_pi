# World News Map — T022 UX Priority Matrix (T021/T022-1 Audit)

This matrix classifies all identified UI/UX improvements into 4 priority levels (P0, P1, P2, P3) based on user impact and audit evidence.

## P0 — Critical (Core Navigability & Functionality Fixes)
- None. (The current UI is functional, zero critical crash or data corruption errors).

## P1 — High (Core Map Usability & Multi-Article Density)
1. **UX-001: Dense Marker Handling & Clustering**: Implement proximity marker clustering / density handling for zoom levels 2-4 to eliminate marker overlap in dense regions (Europe, Asia, Africa).
2. **UX-002: Region Filter & Taxonomy**: Add Region Filter dropdown (Africa, Asia, Europe, Middle East, Americas, Oceania) to FilterBar to enable direct region filtering post T021 RSS expansion.
3. **UX-003: 3-Way State Synchronization**: Ensure selecting an event updates Map marker highlight, scrolls list item into view, and opens Event Detail Panel.
4. **UX-004: Multi-Article Event Hierarchy**: Enhance Event Detail Panel and Event List cards to clearly distinguish Multi-Article Events (`Article Count > 1`) and display publisher source badges prominently.
5. **UX-005: Mobile Bottom-Sheet Layout**: Replace vertical stacking on mobile with a responsive Bottom-Sheet overlay for Event List and Event Detail.

## P2 — Medium (Navigation & Overview Enhancements)
6. **UX-006: Global Overview Strip**: Add a top-level overview bar displaying Active Event Count, Region Badges with count indicators, and Quick Region Jumps.
7. **UX-007: Event List Search & Sort**: Add search input (title/location/country) and sort dropdown (newest, highest confidence, article count) to EventList.
8. **UX-008: Country/Category Badges in FilterBar**: Display active event count next to dropdown options (e.g. "Politics (42)").
9. **UX-009: Enhanced Offline/Error Bar**: Improve stale data banner clarity when API polling fails ("Displaying cached data from 14:32 - Server Unreachable").

## P3 — Low (Visual Polish & Accessibility)
10. **UX-010: Keyboard Navigation Shortcuts**: Add `ESC` to close panel, `R` to refresh, `F` to focus search.
11. **UX-011: Color Contrast & ARIA Labels**: Add `aria-label` tags to map markers, close buttons, and improve text contrast ratios.
