# API.md

## 1. API

Version prefix:

`/api/v1`

Initial API implementation candidate: FastAPI.

## 2. GET /api/v1/health

Returns service health.

Example:

{
  "status": "ok",
  "database": "ok",
  "llm": "ok",
  "queue": "ok"
}

## 3. GET /api/v1/events

Returns active events.

Query parameters:

- country
- event_type
- min_confidence
- since
- limit

Default behavior returns active events only.

## 4. GET /api/v1/events/{id}

Returns event details and associated source metadata.

## 5. GET /api/v1/stats

Returns:

- active_events
- pending_articles
- processed_articles
- failed_articles
- feed_count
- healthy_feed_count

## 6. Internal endpoints

POST /api/v1/internal/articles

Used by Pi3 to submit normalized articles.

POST /api/v1/internal/reprocess/{article_id}

Requests re-analysis.

GET /api/v1/internal/queue

Returns queue state.

Internal endpoints MUST NOT be publicly exposed.

## 7. Authentication

Initial LAN prototype may use network restriction.

Before public exposure, proper authentication, authorization and HTTPS are mandatory.

## 8. Compatibility

API response schemas MUST be versioned and documented.

Mobile clients MUST NOT access SQLite directly.
