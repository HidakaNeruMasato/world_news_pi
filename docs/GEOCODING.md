# GEOCODING.md

## 1. Principle

The LLM extracts names. A geocoding component resolves names to coordinates.

The LLM MUST NOT be treated as a coordinate authority.

## 2. Resolution order

Preferred query construction:

specific location + city + region + country

then:

city + region + country

then:

region + country

then:

country

## 3. Confidence

The geocoder result MUST be recorded separately from LLM confidence.

A low-precision country centroid MAY be used only if explicitly enabled.

Default behavior SHOULD prefer no marker over a misleading precise-looking marker.

## 4. Cache

Successful geocoding results MUST be cached to reduce repeated requests.

The cache MUST include the provider and query.

## 5. Provider

The provider MUST be configurable.

The implementation MUST respect provider rate limits and terms.

## 6. Offline resilience

If geocoding fails temporarily:

- retain the event
- mark location unresolved
- retry later
- do not block the entire analyzer queue

## 7. Coordinate validation

Reject:

- latitude outside -90..90
- longitude outside -180..180
- malformed numeric values

## 8. Privacy

No personal address geocoding is required by this application.
