# SECURITY.md

## 1. Threat model

Initial system is a private home-LAN application.

Public exposure is a future phase with a separate security review.

## 2. SSH

Use key-based authentication.

Disable root SSH login.

Do not commit private keys.

## 3. API

Bind internal services appropriately.

Do not expose internal endpoints to the public network.

## 4. Secrets

Never commit:

- API keys
- SSH keys
- passwords
- tokens
- private certificates

## 5. AI Agent permissions

The AI agent is not granted unrestricted root access.

Use narrowly scoped sudo rules or controlled operation scripts.

## 6. Destructive actions

Require user approval.

## 7. Network

Initial services SHOULD be reachable only on the home LAN.

Before public release, add:

- HTTPS
- authentication
- authorization
- rate limiting
- request validation
- logging
- secret rotation
- dependency patching

## 8. Data

Avoid unnecessary personal data.

Do not store full article text by default.

## 9. Supply chain

Pin important dependencies.

Review downloaded model files and their source.

Do not execute untrusted scripts downloaded from RSS/news content.
