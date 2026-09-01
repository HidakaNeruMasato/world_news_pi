# DECISIONS.md

## ADR-001: Pi3 collects, Pi4 analyzes

Decision:
Pi3 B+ performs RSS collection/preprocessing; Pi4 4GB performs LLM analysis and backend services.

Reason:
Pi3 has insufficient RAM for a comfortable local LLM workload, while Pi4 4GB is better suited to small quantized models.

## ADR-002: SQLite on Pi4

Decision:
SQLite is the initial canonical database.

Reason:
The system is single-home, moderate scale, and benefits from operational simplicity.

Migration to PostgreSQL is possible later if scale requires it.

## ADR-003: API-first

Decision:
Clients communicate through a versioned API.

Reason:
The first web map and future Android/iOS applications must share the same backend contract.

## ADR-004: LLM does not produce coordinates

Decision:
LLM returns semantic place names; geocoder returns coordinates.

Reason:
This avoids fabricated coordinates and separates semantic interpretation from geographic resolution.

## ADR-005: Local LLM

Decision:
News semantic analysis is performed locally on Pi4.

Reason:
The project's explicit requirement is to avoid depending on external LLM APIs for this processing.

## ADR-006: LAN-first

Decision:
The initial product is private-LAN only.

Reason:
Public exposure introduces authentication, HTTPS, abuse prevention and operational complexity that is not required to validate the core idea.

## ADR-007: Mobile later

Decision:
Flutter is the initial mobile candidate, but mobile implementation begins only after API and event processing are stable.

Reason:
Backend data quality is the core product value; client technology should not slow validation.
