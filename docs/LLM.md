# LLM.md

## 1. Purpose

The local LLM performs semantic extraction only.

It MUST NOT:

- browse the web
- fetch RSS
- geocode
- write directly to the database
- decide whether a generated coordinate is correct

## 2. Model constraints

Pi 4 has 4GB RAM.

Initial model selection SHOULD favor a small instruction-following model with 4-bit quantization and reliable structured output.

The exact model is a benchmark decision.

The agent MUST benchmark:

- latency/article
- peak RAM
- invalid JSON rate
- country accuracy
- event-type accuracy
- location accuracy

## 3. Recommended inference behavior

- temperature: 0 or near 0
- deterministic decoding where practical
- bounded context
- bounded output tokens
- one article per analysis request initially

## 4. Input

The prompt SHOULD include:

- source name
- source country
- title
- description/content excerpt
- publication time

The prompt MUST clearly state that source country is not event country.

## 5. Output contract

Conceptual schema:

{
  "is_event": true,
  "event_type": "earthquake",
  "event_country_code": "JP",
  "event_country_name": "Japan",
  "region": "Hokkaido",
  "city": null,
  "location_name": null,
  "confidence": 0.94,
  "location_confidence": 0.88
}

All fields MUST be schema-validated.

## 6. Ambiguity

Null is preferred over guessing.

For multiple locations, the analyzer MAY return a primary location plus a structured list in a future schema.

## 7. Prompt versioning

Every stored analysis result MUST record:

- model_id
- model_version
- prompt_version
- analyzed_at

## 8. Evaluation

Maintain a manually verified dataset.

Any model/prompt change MUST be evaluated before being promoted to production.

## 9. LLM service boundary

Analyzer calls an LLM service over localhost or a local socket/API.

The application code SHOULD not depend on a specific model file name.
