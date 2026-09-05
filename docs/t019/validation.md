# T019 Validation & Regression Test Report

This document records the automated and manual verification results for T019.

---

## 1. Test Suite Results

```text
============================ 214 passed in 20.65s =============================
```

* **Baseline T018 Test Count**: 190 tests (100% PASS)
* **New Dashboard Unit/Integration Tests Added**: 24 tests (100% PASS)
* **Total Suite**: **214 tests passed in 20.65s**.

---

## 2. Verified Non-Negotiable Rules

1. **Core Pipeline Non-Destruction**:
   * Qwen2.5-1.5B model, Prompt v2, threshold 0.35, Geocoder, Event Engine merge/expiration rules untouched.
2. **`source_country` vs `event_country` Separation**:
   * Verified with regression test `test_source_vs_event_country_separation`: BBC article (source `GB`) reporting Tokyo event (`JP`) correctly attributes source metrics to `GB` and event activity to `East Asia` / `JP`.
3. **Map Event Exclusion Verification**:
   * Verified with `test_exclusion_low_confidence_and_unresolved`: Events with `confidence < 0.50` or `latitude/longitude = NULL` are strictly excluded from `map_events`.
4. **Web UI Compilation**:
   * Production build (`tsc && vite build`) passed in 5.38s.
