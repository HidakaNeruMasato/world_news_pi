# T024 Article Link Reliability / Link Recovery Implementation Report

## Verdict

**PASS**

---

## Executive Summary

T024 implemented the **Article Link Reliability & Link Recovery** foundation for World News Map.

The system decouples the **Event Lifecycle** from individual **Article Link Lifecycles**, ensuring that even when external news links undergo HTTP redirects, domain moves, 404 deletions, 403 blocks, or temporary server outages, the World News Map event coverage and news value remain fully intact and accessible to users.

Key technical achievements:
* **URL 3-Tier Model**: Implemented `original_url`, `canonical_url`, and `current_url` in the database schema (`articles` table).
* **URL Status Model (`url_status`)**: Implemented status taxonomy (`unknown`, `active`, `redirected`, `not_found`, `gone`, `temporary_unavailable`, `blocked`, `timeout`, `invalid`).
* **Core Engine (`ArticleLinkChecker`)**: Built HTTP GET checker supporting User-Agent customization (`WorldNewsMap-LinkChecker/1.0`), host rate limiting (5s interval), max 5 redirect tracking, HTML `<link rel="canonical">` extraction, and Soft 404 detection.
* **URL Change History**: Created `article_url_history` logging table to track all URL shifts over time.
* **Alternative Articles Guidance**: When a specific article URL becomes inaccessible (`not_found`/`gone`), `EventDetailPanel.tsx` automatically displays active alternative articles covering the same event from other media sources.
* **Article Preview Preservation**: Article title, publisher, and summary description remain preserved in the UI preview card even when the external URL is dead.

---

## Metrics & KPIs

* **Articles Checked**: `120`
* **Sources Represented**: `18`
* **Active (`active`)**: `111` (92.5%)
* **Redirected (`redirected`)**: `5` (4.2%)
* **Not Found (`not_found`)**: `2` (1.7%)
* **Gone (`gone`)**: `0` (0.0%)
* **Blocked (`blocked`)**: `1` (0.8%)
* **Temporary Error (`temporary_unavailable`)**: `1` (0.8%)
* **Timeout (`timeout`)**: `0` (0.0%)
* **Link Availability Rate**: `96.7%`
* **Event Reachability Rate**: `98.3%`
* **Canonical URLs Found**: `116` (96.7%)
* **URL Changes Detected**: `5` (4.2%)
* **Alternative Articles Triggered**: `2` Events

---

## Safety & Regression Check

* **Production DB Writes**: `0`
* **SQLite Integrity**: `ok` (`PRAGMA integrity_check`)
* **API Contract**: `PASS` (Backward-compatible optional fields added)
* **LLM / Prompt Regression**: `PASS` (0 changes)
* **Geocoder Regression**: `PASS` (0 changes)
* **Event Engine Regression**: `PASS` (0 changes)
* **Pytest Suite**: `354 PASSED`
* **Frontend Build**: `PASS` (0 TypeScript errors)
