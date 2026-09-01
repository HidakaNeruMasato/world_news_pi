# RSS.md

## 1. Feed registry

Each feed has:

- id
- name
- publisher_country
- language
- feed_url
- category
- enabled
- interval_seconds
- timeout_seconds
- last_success_at
- last_failure_at

## 2. Source selection

Use reputable, identifiable news organizations.

The initial source list is configuration data, not application code.

The agent SHOULD validate that each feed is accessible and actually provides RSS/Atom.

## 3. Collection

The collector SHOULD use conditional requests when supported.

It MUST respect reasonable request intervals.

It MUST handle:

- HTTP errors
- timeouts
- malformed XML
- redirects
- duplicate items
- missing publication dates
- missing GUIDs

## 4. Article normalization

Normalized fields:

- source_id
- external_id
- title
- description
- url
- published_at
- fetched_at
- language
- content_hash

Full article retrieval is optional and must respect site terms and copyright constraints.

## 5. Deduplication

Priority:

1. external GUID
2. canonical URL
3. exact content hash
4. normalized title + source + close publication time

Near-duplicate detection MAY be added later.

## 6. Queue semantics

Submission to Pi4 is at-least-once.

Pi4 MUST make article intake idempotent.

## 7. Feed health

A feed is degraded after repeated failures according to configurable thresholds.

One failed feed MUST NOT stop the collector.
