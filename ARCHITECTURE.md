# ARCHITECTURE.md

## 1. Physical architecture

Internet
  -> RSS providers
  -> Pi 3 collector
  -> Pi 4 analyzer/database/API
  -> clients

Windows PC
  -> Git
  -> SSH
  -> deployment/operations

## 2. Node responsibilities

### worldnews-pi3

MUST provide:

- feed scheduler
- RSS/Atom fetcher
- feed parser
- normalization
- URL/GUID/hash deduplication
- outbound submission to Pi 4
- retry queue

SHOULD avoid:

- LLM inference
- public API serving
- long-term canonical event storage

### worldnews-pi4

MUST provide:

- article intake
- processing queue
- local LLM inference
- JSON schema validation
- event normalization
- geocoding orchestration
- event merge/expiration
- SQLite database
- REST API
- health endpoints

### Windows PC

MUST provide:

- source repository
- AI-agent workspace
- deployment scripts
- test execution
- SSH access
- backup destination

The runtime MUST continue if the PC is powered off.

## 3. Data flow

RSS
 -> collector
 -> normalized article
 -> Pi4 intake
 -> pending job
 -> pre-filter
 -> LLM
 -> schema validation
 -> location resolver
 -> event matching
 -> event upsert
 -> API
 -> client

## 4. Failure isolation

Pi3 offline:
Pi4 continues serving existing events.

Pi4 offline:
Pi3 queues articles for later submission.

PC offline:
runtime continues.

Geocoder unavailable:
article remains stored with unresolved location status.

LLM unavailable:
articles remain pending/retryable.

## 5. Technology baseline

Pi 3 / Pi 4:
Raspberry Pi OS 64-bit.

Backend:
Python 3.x.

Database:
SQLite for initial deployment.

LLM runtime:
llama.cpp-compatible runtime.

API:
FastAPI candidate.

Web prototype:
HTML/CSS/JavaScript + Leaflet candidate.

Mobile:
Flutter candidate.

Deployment:
systemd + SSH + PowerShell scripts.

The exact versions MUST be pinned during implementation after environment inspection.
