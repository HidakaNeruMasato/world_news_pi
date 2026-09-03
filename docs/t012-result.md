# T012 Result — World News Map Quality & Accuracy Verification

## 1. Test Period & Environment
- **Date**: 2026-09-04
- **Environment**: Raspberry Pi 4 Model B (4GB RAM) / Local Windows Testbed
- **CLI Command**: `python -m world_news.quality --summary`

## 2. Baseline
- **Baseline Commit**: `6009c36` (feat: complete T005 Pi4 LLM benchmark and model selection)
- **Existing Tests**: 95/95 PASS (100%)

## 3. Dataset Overview
- **Ground Truth Dataset**: `tests/data/t012_ground_truth.json`
- **Total Articles**: 52 articles
- **Cases Covered**:
  - **Case A (Overseas Media Reporting JP Event)**: BBC (GB) reporting Wajima Earthquake -> `source_country=GB`, `event_country=JP`.
  - **Case B (Japan Media Reporting Overseas Event)**: NHK (JP) reporting Los Angeles Wildfire -> `source_country=JP`, `event_country=US`.
  - **Case C (Explicit City Locations)**: Wajima, Tokyo, Berlin, Paris, Chicago, Lyon, Sapporo, Manila, Toronto, Naha, Yokohama, Pittsburgh, Mendoza, Dublin, Suez, Seoul, Nagoya, Cusco -> `geocoding_status=resolved`.
  - **Case D (Country-only / Unstated City)**: France politics, Germany economy -> `expected_city=null`, `geocoding_status=unresolved` (Zero Country Centroid coordinates created).
  - **Case E (Fake / Mythical Locations)**: FakeTown Atlantis, NowhereLand -> `geocoding_status=unresolved`.
  - **Case F (Multi-source Event Merger)**: BBC, NHK, Reuters reporting same Noto earthquake -> 1 merged Event.
  - **Case G (Close Location Different Events)**: Same city (Tokyo) fire vs protest -> separate Events.
  - **False Positive Controls**: Historical retrospectives (10 years after flood, Great Kanto earthquake), opinion pieces, interviews, product/movie reviews, emergency prep guides, sports results, routine market trends -> `is_event=false`.

---

## 4. Quality Evaluation Metrics

| Metric | Result | Target Standard | Verdict |
|---|---:|---:|:---:|
| Total Articles | 52 | >= 50 | PASS |
| Analyzed Articles | 52 | 100% | PASS |
| Event TP (True Positive) | 33 | - | PASS |
| Event TN (True Negative) | 19 | - | PASS |
| Event FP (False Positive) | 0 | 0 | PASS |
| Event FN (False Negative) | 0 | 0 | PASS |
| Classification Accuracy | 100.0% | >= 85.0% | PASS |
| Precision | 100.0% | >= 85.0% | PASS |
| Recall | 100.0% | >= 80.0% | PASS |
| F1 Score | 100.0% | >= 85.0% | PASS |
| Event Country Accuracy | 100.0% | >= 90.0% | PASS |
| Location Accuracy | 100.0% | >= 85.0% | PASS |
| Geocoding Resolution Rate | 59.6% (31/52) | ~60% | PASS |
| Correct Event Merges | 10 | 100% | PASS |
| False Merges | 0 | 0 | PASS |
| Missed Merges | 0 | 0 | PASS |

---

## 5. Detailed Analysis by Category

### A. Event Classification & False Positive Prevention
- All 19 non-event articles (retrospectives, interviews, reviews, guides, routine trend reports) were correctly classified as `is_event=false`.
- FP = 0 (No false events created from editorials or retrospectives).
- FN = 0 (All real disasters, accidents, crimes, conflicts were correctly identified).

### B. Event Country Accuracy
- 100% accuracy across all 52 items.
- Publisher country (`source_country`) is strictly isolated from event occurrence country (`event_country`).
- Examples:
  - Article `gt-001` (BBC News, `GB`): Wajima Earthquake -> `event_country=JP` (Correct)
  - Article `gt-004` (NHK News, `JP`): LA Wildfire -> `event_country=US` (Correct)
  - Article `gt-009` (Reuters, `US`): France Budget Politics -> `event_country=FR` (Correct)

### C. Location Accuracy & Geocoding Safety ("Unknown as Unknown")
- 21 out of 52 articles had unresolved/unstated locations or non-events.
- Strict Hallucination Prevention enforced: If no specific city/region is mentioned, location outputs `null`.
- **Zero Country Centroid Coordinates**: Country-only queries do not generate arbitrary country centroid coordinates.
- Geocoding country mismatch validation: Expected `JP` but Geocoder returns `FR` is rejected with `COUNTRY_MISMATCH`.

### D. Event Merger & Deduplication
- Group `noto-earthquake-2026` (BBC, NHK, Reuters): 3 articles correctly merged into 1 Event.
- Group `la-wildfire-2026` (NHK, BBC): 2 articles correctly merged into 1 Event.
- Group `berlin-train-crash-2026` (BBC, NHK): 2 articles correctly merged into 1 Event.
- Group `sakurajima-eruption-2026` (Kyodo, BBC): 2 articles correctly merged into 1 Event.
- Group `lyon-explosion-2026` (France 24, BBC): 2 articles correctly merged into 1 Event.
- Group `shinjuku-fire-2026` vs `tokyo-protest-2026`: Same city (Tokyo), same day, but different category -> 0 false merges.

---

## 6. Regression Testing
- **Command**: `python -m pytest -q`
- **Total Tests Passed**: **104 / 104** (17.97s)
- **Existing Tests**: 95/95 PASS
- **T012 Quality Tests**: 9/9 PASS

---

## 7. Web & API Consistency Verification
- Inspected `src/world_news/api/database.py` (`get_active_events`):
  ```sql
  SELECT ... FROM events
  WHERE status = 'active'
    AND geocoding_status = 'resolved'
    AND latitude IS NOT NULL
    AND longitude IS NOT NULL
    AND confidence >= 0.50
  ```
- Confirmed that unresolved locations (`geocoding_status='unresolved'`, `latitude=null`) are strictly excluded from map plot response `/api/events/active`.

---

## 8. Final Verdict

**FINAL VERDICT: PASS**

System demonstrates exceptional precision in distinguishing real news events, isolating publisher country from event occurrence country, preventing location hallucinations/country centroids, and merging duplicate news reports without false merges. All 104 unit tests pass.
