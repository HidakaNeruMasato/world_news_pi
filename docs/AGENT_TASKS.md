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

## T003 — Pi3 collector

Implement feed registry, scheduler, parser, normalization, deduplication and retry queue.

## T004 — Pi4 intake/API/database

Implement SQLite schema, migrations/init, internal article intake and health endpoint.

## T005 — LLM benchmark

Benchmark a small set of suitable quantized models on Pi4.

Record:

- model
- RAM
- latency
- JSON reliability
- evaluation metrics

Do not install many large models simultaneously.

## T006 — Analyzer

Implement prompt versioning, LLM invocation, schema validation and retry.

## T007 — Geocoder

Implement provider abstraction and cache.

## T008 — Event engine

Implement matching, merge, expiration and active-event query.

## T009 — Web prototype

Implement map, markers, aging, filters and event details.

## T010 — End-to-end test

Run the complete pipeline with controlled test feeds/articles.

## T011 — Operations

Implement real deployment, health, backup and rollback scripts.

## T012 — Mobile prototype

Create Flutter client after the API contract is stable.

Each task should be completed and verified before moving to the next unless the user explicitly requests parallel work.
