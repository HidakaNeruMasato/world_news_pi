# TESTING.md

## 1. Test layers

- unit
- integration
- LLM evaluation
- end-to-end
- failure/recovery

## 2. Unit tests

Required for:

- RSS parsing
- normalization
- hashing
- deduplication
- schema validation
- confidence thresholds
- expiration
- geocode validation
- event matching
- API serialization

## 3. LLM evaluation dataset

Maintain manually verified examples covering:

- Japan event reported by non-Japanese source
- US event reported by Japanese source
- international event
- ambiguous location
- no location
- multiple locations
- historical article
- opinion article
- non-event article
- multiple reports of one event

## 4. Metrics

Track:

- event classification accuracy
- country accuracy
- location accuracy
- event type accuracy
- invalid JSON rate
- average inference latency

## 5. Integration

Test:

RSS -> Pi3 -> Pi4 -> LLM -> geocoder -> event DB -> API -> client

## 6. Failure cases

Simulate:

- feed timeout
- malformed feed
- Pi4 unavailable
- LLM unavailable
- invalid LLM output
- geocoder unavailable
- database locked
- network interruption
- reboot

## 7. Regression

Every LLM prompt/model change MUST run the fixed evaluation dataset.

Do not compare only aggregate accuracy; inspect false positives and false merges.
