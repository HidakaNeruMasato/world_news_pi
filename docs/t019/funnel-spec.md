# T019 Pipeline Reduction Funnel Specification

This document describes the pipeline reduction funnel model and conversion percentage formulas.

---

## 1. Funnel Stages

```text
┌────────────────────────────────────────────────────────┐
│ Stage 1: RSS Items Seen                                │
└──────────────────────────┬─────────────────────────────┘
                           │ Deduplication Rate
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 2: New Articles Ingested                         │
└──────────────────────────┬─────────────────────────────┘
                           │ LLM Event Rate
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 3: LLM Event Candidates                          │
└──────────────────────────┬─────────────────────────────┘
                           │ Geocoding Resolution Rate
                           ▼
┌────────────────────────────────────────────────────────┐
│ Stage 4: Active Map Events Displayable                 │
└────────────────────────────────────────────────────────┘
```

---

## 2. Stage Reduction Formulas

* **Deduplication Rate**: `(new_articles / rss_items_seen) * 100`
* **Analysis Rate**: `(llm_analyzed / new_articles) * 100`
* **Event Candidate Rate**: `(event_candidates / llm_analyzed) * 100`
* **Geocoding Rate**: `(geocoding_resolved / event_candidates) * 100`
* **Map Display Rate**: `(active_map_events / geocoding_resolved) * 100`
* **Overall Map Conversion Rate**: `(active_map_events / new_articles) * 100`
