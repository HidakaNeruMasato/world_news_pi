# World News Map — RSS Source Policy & Governance

This document establishes the governing principles, access guidelines, and lifecycle management rules for news RSS/Atom feeds integrated into the World News Map system.

---

## 1. Access & Polling Guidelines

To ensure ethical, respectful, and stable data collection:

1. **User-Agent Header**: All HTTP requests sent by Pi3 Collector MUST specify the explicit User-Agent string:
   ```text
   WorldNewsCollector/1.0 (+http://worldnews.local)
   ```
2. **Polling Frequency**: The standard polling interval per feed is **300 seconds (5 minutes)**. Rapid polling (< 60s) is strictly prohibited to avoid rate limiting or server strain.
3. **Timeout Limit**: Individual feed HTTP requests MUST time out after **10 seconds**.
4. **Conditional Retrieval**: If HTTP `ETag` or `Last-Modified` headers are provided by the publisher, Pi3 Collector MUST send `If-None-Match` / `If-Modified-Since` headers to receive `304 Not Modified` and reduce bandwidth.
5. **No Full-Page Scraping**: World News Map ingests exclusively RSS/Atom XML payloads (headline, summary, pubDate, GUID). Automated full HTML scraping of publisher websites is strictly out of scope.

---

## 2. Selection & Inclusion Criteria

A news feed candidate is eligible for inclusion in World News Map if it satisfies all of the following criteria:

* **Technical Health**:
  * Returns `HTTP 200 OK`.
  * Passes XML validation for RSS 2.0 or Atom 1.0.
  * Includes `<item>` or `<entry>` tags with non-empty `<title>`, `<link>`, and date information (`<pubDate>`, `<published>`, or `<updated>`).
* **Active Update Rate**: Produces at least 5 news items over a 7-day period.
* **Geographic Relevance**: Reports on real-world events occurring within its target region or country.
* **Editorial Quality**: Represents a legitimate news organization, public broadcaster, state agency, or independent press outlet.

---

## 3. Political Neutrality & Multi-Perspective Principle

1. **Zero Political Exclusion**: World News Map DOES NOT exclude or penalize media outlets based on state ownership, political stance, or editorial perspective.
2. **Multi-Perspective Balance**: Where possible, regions are covered by a combination of:
   * State / Public Broadcasters (e.g., NHK, BBC, SVT, Radio Okapi)
   * Major Private Commercial Press (e.g., The Hindu, Folha de S.Paulo, El País)
   * Independent / Regional Journalism (e.g., Notes from Poland, Balkan Insight, Times of Israel)
3. **Geographic Priority Over Volume**: Adding a news source for an underrepresented geographic region (e.g., Tonga, Zambia, Guatemala) takes precedence over adding another news source for saturated regions (e.g., US, UK, Japan).

---

## 4. Lifecycle & Deprecation Rules

Pi3 Collector and QualityMonitor automatically track feed health and apply the following lifecycle state transitions:

```text
[ Active ] ───(3 consecutive failures)───► [ Warning Alert ]
    │                                              │
    ├─────────(10 consecutive failures)────────────┴───► [ Disabled / Quarantine ]
    │
    └─────────(No new items for > 12 hours)────────────► [ Stale Ingestion Alert ]
```

* **Quarantine / Auto-Disable**: A feed with > 10 consecutive failures or persistent HTTP 403/404 errors is automatically set to `enabled: false` in `collector.db` to prevent wasteful network requests.
* **Quarterly Audit**: Every 3 months, a full inventory run (equivalent to `t019_test_feeds.py`) is conducted to re-verify quarantined feeds and update broken URLs.
