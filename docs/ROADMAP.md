# ROADMAP.md

## Phase 0 — Inventory

- inspect Windows environment
- inspect Pi3
- inspect Pi4
- verify SSH aliases
- verify Python
- verify available storage/RAM/temperature
- create repository

## Phase 1 — RSS

- feed registry
- scheduler
- parser
- normalization
- deduplication
- queue
- Pi4 intake

## Phase 2 — Backend

- SQLite
- migrations/schema initialization
- API
- health checks

## Phase 3 — LLM

- benchmark candidate models
- install llama.cpp-compatible runtime
- implement schema-constrained analysis
- evaluation dataset
- model selection

## Phase 4 — Event engine

- event normalization
- location resolution
- geocoding cache
- event matching
- expiration

## Phase 5 — Web prototype

- world map
- markers
- aging
- detail panel
- filters

## Phase 6 — Reliability

- retries
- backup
- monitoring
- recovery tests
- deployment automation

## Phase 7 — Mobile

- Flutter prototype
- API integration
- map
- filters
- details

## Phase 8 — Public release architecture

- public API gateway
- HTTPS
- authentication
- rate limiting
- map/tile licensing review
- app store requirements
- privacy policy
- operational monitoring

No phase may silently bypass the security or approval rules in AGENTS.md.
