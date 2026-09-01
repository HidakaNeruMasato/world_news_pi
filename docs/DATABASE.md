# DATABASE.md

## 1. Database

Initial database: SQLite on Pi4.

SQLite is the canonical runtime data store.

## 2. sources

- id INTEGER PRIMARY KEY
- name TEXT NOT NULL
- country_code TEXT
- language TEXT
- feed_url TEXT UNIQUE NOT NULL
- category TEXT
- enabled INTEGER NOT NULL
- interval_seconds INTEGER
- last_success_at TEXT
- last_failure_at TEXT

## 3. articles

- id INTEGER PRIMARY KEY
- source_id INTEGER NOT NULL
- external_id TEXT
- title TEXT NOT NULL
- description TEXT
- url TEXT
- published_at TEXT
- fetched_at TEXT NOT NULL
- language TEXT
- content_hash TEXT
- processing_status TEXT NOT NULL
- retry_count INTEGER NOT NULL DEFAULT 0
- event_id INTEGER
- created_at TEXT NOT NULL
- updated_at TEXT NOT NULL

## 4. analyses

- id INTEGER PRIMARY KEY
- article_id INTEGER NOT NULL
- model_id TEXT
- model_version TEXT
- prompt_version TEXT
- raw_output TEXT
- parsed_json TEXT
- status TEXT
- error_message TEXT
- analyzed_at TEXT

## 5. events

- id INTEGER PRIMARY KEY
- event_type TEXT NOT NULL
- country_code TEXT
- country_name TEXT
- region TEXT
- city TEXT
- location_name TEXT
- latitude REAL
- longitude REAL
- confidence REAL
- location_confidence REAL
- first_seen_at TEXT NOT NULL
- last_seen_at TEXT NOT NULL
- expires_at TEXT NOT NULL
- status TEXT NOT NULL
- created_at TEXT NOT NULL
- updated_at TEXT NOT NULL

## 6. article_events

Use a join table when multiple articles can describe one event.

- article_id
- event_id
- relation_type
- similarity_score

## 7. geocoding_cache

- id INTEGER PRIMARY KEY
- normalized_query TEXT UNIQUE
- provider TEXT
- result_json TEXT
- latitude REAL
- longitude REAL
- resolved_name TEXT
- created_at TEXT
- expires_at TEXT

## 8. processing_jobs

- id INTEGER PRIMARY KEY
- article_id INTEGER
- job_type TEXT
- status TEXT
- started_at TEXT
- completed_at TEXT
- retry_count INTEGER
- error_message TEXT

## 9. Indexes

At minimum index:

- articles.processing_status
- articles.published_at
- articles.content_hash
- events.status
- events.expires_at
- events.country_code
- events.event_type
- processing_jobs.status

## 10. Retention

Article retention and event retention MUST be configurable.

Do not retain full article text by default.
