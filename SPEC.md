# SPEC.md — System Specification

## 1. Product

World News Event Map is a self-hosted event intelligence and visualization system.

It continuously ingests RSS news, semantically identifies real-world events, resolves event locations, merges related reports, and presents active events on a world map.

## 2. Primary goals

- Continuous RSS collection.
- Reliable source management.
- Event-vs-non-event classification.
- Event-country identification.
- Region/city/location extraction.
- Geocoding.
- Duplicate/related-event merging.
- Time-based event expiration.
- Local LLM processing.
- API-first architecture.
- AI-agent-operated infrastructure.
- Future Android/iOS clients.

## 3. Initial non-goals

- Public Internet exposure.
- User accounts.
- Personalized news feeds.
- Automated political persuasion or sentiment ranking.
- Automatic article republication.
- Full-text archival.
- Fully autonomous destructive server administration.

## 4. Terminology

`source_country`: country associated with the publisher.

`event_country`: country where the reported event occurred.

`article`: one RSS/news report.

`event`: normalized real-world occurrence represented on the map.

`event_group`: optional internal grouping of articles believed to describe the same occurrence.

## 5. Event categories

Initial categories:

- earthquake
- volcanic
- tsunami
- flood
- storm
- wildfire
- fire
- explosion
- traffic_accident
- rail_accident
- aviation_accident
- maritime_accident
- industrial_accident
- crime
- shooting
- terrorism
- protest
- war
- military
- other
- none

The taxonomy MUST remain extensible.

## 6. Event lifetime

Default display lifetime: 6 hours after the latest confirmed event observation.

The value MUST be configurable.

An event may be extended when new credible reports indicate the occurrence is still active.

## 7. Confidence

Confidence is a value from 0.0 to 1.0.

It represents system confidence in the extracted event/location, not source credibility alone.

Recommended interpretation:

- 0.90–1.00: high
- 0.75–0.89: good
- 0.50–0.74: uncertain
- below 0.50: normally not displayed unless configured

## 8. Reliability requirements

- Reboot recovery is required.
- Temporary RSS failure must not stop other feeds.
- Pi 4 failure must not corrupt Pi 3 collection state.
- Invalid LLM output must be recoverable.
- Geocoder failure must not lose the article.
- Expired events must not remain active indefinitely.

## 9. Runtime

Pi 3:
RSS collector and preprocessing.

Pi 4:
analysis, geocoding orchestration, database, API and web prototype.

Windows PC:
development and AI-agent control only; it is not required for runtime.

## 10. Client architecture

The backend MUST expose a stable versioned REST API.

The first client may be a browser-based prototype.

The intended long-term client is a cross-platform mobile application, with Flutter as the initial candidate.

The mobile application MUST NOT depend on internal Pi filesystem/database access.
