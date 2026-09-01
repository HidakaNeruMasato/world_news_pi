# EVENT.md

## 1. Event identity

An event is a real-world occurrence, not an article.

Multiple articles MAY map to one event.

## 2. Matching signals

Use, in order of reliability:

- normalized location
- event type
- temporal proximity
- named entities
- title similarity
- source agreement

The initial implementation may use deterministic rules plus text similarity.

An LLM MAY assist only where deterministic matching is insufficient.

## 3. Merge policy

Automatic merging MUST require a configurable confidence threshold.

If uncertain, create separate events rather than incorrectly merging unrelated events.

## 4. Event timestamps

`first_seen_at` = earliest observed report.

`last_seen_at` = latest credible report associated with the event.

`expires_at` = calculated display expiration.

## 5. Expiration

Expired events are not deleted immediately.

Set:

status = expired

This preserves auditability.

A periodic cleanup MAY remove old records according to retention policy.

## 6. Multiple events in one article

Initial implementation MAY select one primary event.

The schema SHOULD remain extensible for multiple event extraction later.

## 7. Cross-border events

Events occurring near borders MUST be assigned based on the actual reported location, not the publisher country.

If the location cannot be confidently assigned to a country, country_code may be null.
