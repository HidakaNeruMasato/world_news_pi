# AGENT_TASKS.md

This file defines the implementation queue for the AI agent.

## T001 — Environment inventory (Status: Completed)

Inspect without modifying:

- Windows Python/Git/SSH
- SSH aliases
- Pi3 OS/kernel/Python/storage/RAM/temperature
- Pi4 OS/kernel/Python/storage/RAM/temperature
- available ports
- systemd capability

Output:
`docs/ENVIRONMENT.md`

Do not change OS configuration in this task.

## T002 — Repository bootstrap (Status: Completed)

Create:

- Python package layout
- tests
- configuration loader
- logging
- common schemas
- PowerShell operation skeleton

## T003 — Pi3 collector (Status: Completed)

Implement feed registry, scheduler, parser, normalization, deduplication and retry queue.

## T004 — Pi4 intake/API/database

Implement SQLite schema, migrations/init, internal article intake and health endpoint.

## T005 — LLM benchmark (Status: Completed)

Benchmark a small set of suitable quantized models on Pi4.

Record:

- model
- RAM
- latency
- JSON reliability
- evaluation metrics

Do not install many large models simultaneously.

## T006 — Analyzer (Status: Completed)

Implement prompt versioning, LLM invocation, schema validation, analyses & events record creation, and retry.

## T007 — Geocoder (Status: Completed)

Implement Geocoder interface abstraction, OpenStreetMap Nominatim provider, location resolver, fallback queries, country validation, geocoding cache, and systemd user service.

## T008 — Event engine (Status: Completed)

Implement matching, merge, expiration and active-event query.

## T009 — Web prototype / map visualization (Status: Completed)

Implement React+TS+Vite map UI with Leaflet, active event polling, event detail panel, category markers, fade effects, error handling and FastAPI static hosting on Pi4.

## T010 — End-to-end test (Status: Completed)

Execute full E2E test from Pi3 RSS fetch to Pi4 LLM, Geocoder, Event Engine, API and React+Leaflet Web Map. Verify metrics, outage recovery, duplicate handling, resource safety, and manual location accuracy. (Verdict: PASS)

## T011 — Operations / Long-Running Test (Status: Completed)

Execute continuous operation & stability tests, monitoring metrics into CSV, verifying service & host restart recoveries, memory safety (OOM = 0), queue drain, SQLite integrity (ok), and data loss zero. (Verdict: PASS)up and rollback scripts.

## T012 — News Quality and Event Accuracy Verification (Status: Completed)

Evaluate and verify news quality, event classification, source vs event country separation, hallucination prevention, duplicate event merging, and geocoding safety with 52-item Ground Truth dataset and Quality Evaluation CLI (`world_news.quality`). (Verdict: PASS)

## T013 — Real-World News Quality Verification (Status: Completed)

Evaluate real-world RSS ingested news articles (204 items) with human review dataset (`docs/t013/review.json`), error taxonomy (`docs/t013/errors.md`), RealWorldEvaluator CLI, zero critical errors, 100% country & location accuracy, and 106/106 unit test pass. (Verdict: CONDITIONAL PASS)

## T014 — Real-World Event Detection Recall Improvement (Status: Completed)

Improve Real-World Event Detection Recall from 5.9% to 73.5% (F1: 76.9%, Precision: 80.6%) using Prompt v2 (`analysis_prompt_v2`), threshold optimization, and Event/Location separation while preserving 100% safety properties (Critical Errors = 0, Country Acc = 100%, Location Acc = 100%, False Merge = 0) and passing 118/118 unit tests on Qwen2.5-1.5B. (Verdict: PASS)

## T015 — Mobile prototype

Create Flutter client after the API contract is stable.

Each task should be completed and verified before moving to the next unless the user explicitly requests parallel work.
