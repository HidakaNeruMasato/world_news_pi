# T023 User Journey Validation Specification & Execution Logs

## Overview

This document contains detailed evaluation logs for all 16 target User Journeys (UJ-001 through UJ-016) tested against the Production Web environment (`http://192.168.0.185:8080/`).

---

## UJ-001: Global Overview (初見ユーザー)
* **Goal**: A first-time user lands on the Map view and immediately grasps world news activity.
* **Steps**:
  1. Open Production Web URL in browser.
  2. Inspect Header & Global Overview Strip (`Active Events (120)`).
  3. Observe regional count pills (`Africa: 26`, `Americas: 18`, `Europe: 27`, `Middle East: 17`, `Asia: 24`, `Oceania: 8`).
  4. Inspect Map view showing marker clusters and event cards in EventList.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `4s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-002: Region Exploration (地域からの探訪)
* **Goal**: Filter news by specific region (e.g. Africa, Europe, Asia) and cascade country choices.
* **Steps**:
  1. Open FilterBar region dropdown and select `Africa`.
  2. Map updates to display 26 events across African countries.
  3. Country dropdown updates options dynamically to show only African countries (`KE`, `EG`, `NG`, etc.).
  4. Select `NG` (Nigeria) -> Map and EventList update to show 6 Nigerian events.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `6s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-003: Cluster Exploration (Marker Clustering)
* **Goal**: Explore high-density event clusters at zoom levels 2-4 and zoom in to individual markers at level 5+.
* **Steps**:
  1. View global map at zoom level 3 (dense clusters e.g. `[27]` Europe cluster).
  2. Click `[27]` Europe cluster badge.
  3. Map smoothly zooms to level 6 over Western/Central Europe.
  4. Individual category-colored circle markers (e.g. Red for Politics, Green for Economy) appear with clickability.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `5s` | Errors: `0`
  * Discoverability: `5` | Clarity: `4` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `4.8 / 5`

---

## UJ-004: Map → List → Detail Navigation
* **Goal**: Click an individual event marker on the Map, scroll the corresponding list card into view, and inspect the Detail panel.
* **Steps**:
  1. Click an individual marker in Tokyo, Japan.
  2. `selectedEventId` updates to target event.
  3. EventList card `event-card-X` highlights and smoothly scrolls into view.
  4. EventDetailPanel slides in displaying category, country flag, coordinates, confidence score, and article metadata.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `4s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-005: List → Map → Detail Navigation
* **Goal**: Select an event card from EventList, pan map camera to event coordinates, and open Detail panel.
* **Steps**:
  1. Select event card in Berlin, Germany (`DE`) from EventList.
  2. Map camera pans to `(52.3963, 13.0749)`.
  3. Marker highlights with pulse effect.
  4. DetailPanel updates to show German event details.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `3s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-006: Multi-Article Event Validation
* **Goal**: Identify events covered by multiple news sources and review source breakdown.
* **Steps**:
  1. Locate multi-article event in EventList or Sandbox.
  2. Observe `[N Articles]` blue font-mono badge on event card.
  3. Open DetailPanel to view "Covered by N Media Sources" list.
  4. Verify publisher names, country tags, and timestamps.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `5s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `4` | Satisfaction: `4.5`
  * **Journey Score**: `4.6 / 5`

---

## UJ-007: Source Article Navigation
* **Goal**: Click external source article link in Detail panel to open original news report in new tab.
* **Steps**:
  1. Open EventDetailPanel.
  2. Inspect article link with title and publisher domain.
  3. Click link.
  4. Confirm link opens in new browser tab with `target="_blank"` and `rel="noopener noreferrer"`.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `3s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-008: Search Exploration
* **Goal**: Filter active events by keyword search in EventList.
* **Steps**:
  1. Enter `"Kenya"` into search input.
  2. EventList instantly filters to 10 events matching `"Kenya"`.
  3. Map updates active markers to reflect search results.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `2s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-009: Combined Filter Exploration
* **Goal**: Apply multiple overlapping filter criteria simultaneously (Region + Country + Category + Search).
* **Steps**:
  1. Select Region = `Asia`.
  2. Select Country = `JP`.
  3. Select Category = `earthquake`.
  4. Type Search = `"Tokyo"`.
  5. Confirm AND condition evaluates strictly and accurately.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `7s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-010: Sorting Execution
* **Goal**: Sort events by `Newest First`, `Highest Confidence`, and `Most Articles`.
* **Steps**:
  1. Select `Newest First` -> verified timestamp ordering.
  2. Select `Highest Confidence` -> verified confidence score descending (e.g. 97% down to 75%).
  3. Select `Most Articles` -> verified article count descending.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `4s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-011: Mobile Exploration (390px Viewport)
* **Goal**: Navigate map and events on mobile viewports (390x844, 375x667, 430x932) using the Bottom Sheet drawer.
* **Steps**:
  1. Open site at 390px viewport.
  2. Confirm Map is prominent and visible initially with collapsed Bottom Sheet.
  3. Drag / tap Bottom Sheet header to expand to Half view (showing EventList).
  4. Expand to Full view for dense list scanning.
  5. Confirm zero horizontal scrollbar overflow (`scrollWidth <= innerWidth`).
* **Result**:
  * Desktop: `N/A` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `6s` | Errors: `0`
  * Discoverability: `4.5` | Clarity: `4.5` | Navigation: `4.5` | Satisfaction: `4.5`
  * **Journey Score**: `4.5 / 5`

---

## UJ-012: Mobile Event Detail & Back Navigation
* **Goal**: Tap a marker on mobile map to open Detail sheet and return smoothly.
* **Steps**:
  1. Tap marker on mobile map view.
  2. Bottom Sheet automatically expands to Detail view.
  3. Inspect details and click "Back to List" button.
  4. Bottom Sheet returns to EventList half state cleanly.
* **Result**:
  * Desktop: `N/A` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `5s` | Errors: `0`
  * Discoverability: `4.5` | Clarity: `4.5` | Navigation: `4.5` | Satisfaction: `4.5`
  * **Journey Score**: `4.5 / 5`

---

## UJ-013: Filter Reset
* **Goal**: Reset all active filters back to global view without leftover state artifacts.
* **Steps**:
  1. Set Region = `Africa`, Country = `KE`, Category = `politics`, Search = `"Nairobi"`.
  2. Click "Clear Filters" or select "All Regions".
  3. Verify Region resets to All, Country resets to All, Category resets to All, Search resets to empty.
  4. Map and List restore full 120 events population.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `3s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-014: Empty Search Result State
* **Goal**: Handle zero matching events query gracefully.
* **Steps**:
  1. Enter non-existent keyword `"zzzzzzzz_test_no_result"`.
  2. EventList displays clear empty state message: `"No matching events found."`.
  3. Map clears markers without throwing JavaScript errors.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `2s` | Errors: `0`
  * Discoverability: `5` | Clarity: `5` | Navigation: `5` | Satisfaction: `5`
  * **Journey Score**: `5.0 / 5`

---

## UJ-015: API Outage & Degraded Network Resiliency
* **Goal**: Gracefully handle network disconnect or API outage without crashing UI.
* **Steps**:
  1. Simulate API failure / network throttle in browser dev tools.
  2. UI displays non-intrusive warning while maintaining existing rendered map markers.
  3. Retrying API fetch recovers state cleanly.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `5s` | Errors: `0`
  * Discoverability: `4` | Clarity: `4.5` | Navigation: `4.5` | Satisfaction: `4.5`
  * **Journey Score**: `4.4 / 5`

---

## UJ-016: High-Density Region Exploration
* **Goal**: Explore high-density event clusters (e.g. Europe 27 events, Africa 26 events) with 60 FPS smoothness.
* **Steps**:
  1. Select Region = `Europe`.
  2. Pan and zoom across European capital markers.
  3. Verify cluster rendering and individual marker rendering remain responsive with no lag or layout shifts.
* **Result**:
  * Desktop: `PASS` | Mobile: `PASS`
  * Task Success: `1` | Time on Task: `4s` | Errors: `0`
  * Discoverability: `5` | Clarity: `4.5` | Navigation: `5` | Satisfaction: `4.8`
  * **Journey Score**: `4.8 / 5`
