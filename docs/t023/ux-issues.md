# T023 UX Issues & T024 Candidate Recommendations

## Summary

* **P0 Critical Issues**: `0`
* **P1 Major Issues**: `0`
* **P2 Moderate Issues**: `1` (T024 Candidate)
* **P3 Minor Issues**: `1` (Backlog Candidate)

---

## Issue Reports

### Issue ID: UX-ISSUE-001
* **Category**: `UX-SEARCH` / `UX-A11Y`
* **Severity**: `P2 Moderate`
* **Journey**: `UJ-008 Keyword Search`, `UJ-011 Mobile Exploration`
* **Viewport**: All Viewports (Desktop & Mobile 390px)
* **Steps**:
  1. User wants to quickly search events using keyboard shortcut (e.g. `/` or `Ctrl+K`).
  2. Currently, the user must manually click or tap the search input in the EventList sidebar.
* **Expected**: Pressing `/` or `Ctrl+K` automatically focuses the search bar input.
* **Actual**: User must click the search input manually.
* **Impact**: Slight friction for power users and keyboard-only desktop navigation.
* **Recommendation**: Add a global keydown event listener in `App.tsx` / `EventList.tsx` for `/` key shortcut to focus search input.
* **T024 Priority**: `P2 - T024 Candidate`

---

### Issue ID: UX-ISSUE-002
* **Category**: `UX-FILTER` / `UX-VIS`
* **Severity**: `P3 Minor`
* **Journey**: `UJ-002 Region Exploration`, `UJ-013 Filter Reset`
* **Viewport**: Desktop & Mobile
* **Steps**:
  1. Apply an active region filter (e.g. `Africa`).
  2. Inspect the FilterBar header.
  3. The dropdown reflects `Africa`, but there is no explicit visual "active filter badge" icon next to the region dropdown label.
* **Expected**: An active filter pill badge (e.g. blue indicator dot or active count tag) signals that filtering is currently active.
* **Actual**: Filter state is visible in the select box value, but lacks a high-contrast accent indicator dot.
* **Impact**: Minor visual polish opportunity.
* **Recommendation**: Render a subtle sky-blue indicator badge on the FilterBar when `selectedRegion !== 'All'`.
* **T024 Priority**: `P3 - Backlog`

---

## T024 Feature Candidate Backlog

| Candidate ID | Priority | Issue Ref | Feature Summary | Estimated Effort |
|---|---|---|---|---|
| **T024-FEAT-01** | `P2` | `UX-ISSUE-001` | Add `/` and `Ctrl+K` keyboard shortcut for Search focus | 0.5 Days |
| **T024-FEAT-02** | `P3` | `UX-ISSUE-002` | Add visual active filter indicator badge on FilterBar | 0.5 Days |
