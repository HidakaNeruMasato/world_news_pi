# T019 Metrics Specification

This document details the definition, formulas, and data sources for all metrics aggregated by `DashboardMetricsCollector` in `src/world_news/dashboard/metrics.py`.

---

## 1. Primary Metrics Definitions

### 1.1 `rss_sources`
* **Definition**: Number of distinct active RSS feed publishers contributing articles in the period.
* **Source Table**: `articles` (`COUNT(DISTINCT source_id)`) or `sources` (`COUNT(*)`).

### 1.2 `rss_items_seen`
* **Definition**: Estimated total raw RSS/Atom items received in XML feed responses prior to deduplication.
* **Formula**: `int(new_articles * 1.25)`

### 1.3 `new_articles`
* **Definition**: Total unique articles ingested and stored in `articles` table within the time window.
* **Source Table**: `articles` (`created_at >= threshold`).

### 1.4 `analyzed_articles`
* **Definition**: Total articles that successfully completed LLM analysis.
* **Source Table**: `analyses` (`created_at >= threshold`).

### 1.5 `event_articles`
* **Definition**: Total articles classified by LLM as actual news events (`is_event = 1`).
* **Source Table**: `analyses` (`is_event = 1 AND created_at >= threshold`).

### 1.6 `geocoding_resolved`
* **Definition**: Total event candidate articles with successfully resolved non-empty location names.
* **Source Table**: `analyses` (`is_event = 1 AND location_name IS NOT NULL AND location_name != ''`).

### 1.7 `map_events`
* **Definition**: Active event clusters meeting strict display criteria:
  ```sql
  status = 'active'
  AND geocoding_status = 'resolved'
  AND confidence >= 0.50
  AND latitude IS NOT NULL
  AND longitude IS NOT NULL
  ```
* **Source Table**: `events`.

---

## 2. Separation of `source_country` vs `event_country`

* **`source_country`**: Country of the news publisher (e.g., `GB` for BBC, `JP` for NHK). Used exclusively in **Source Metrics**.
* **`event_country`**: Country where the news event occurred (e.g., `JP` for a Tokyo earthquake reported by BBC). Used exclusively in **Regional Activity** and **Country News Activity**.
