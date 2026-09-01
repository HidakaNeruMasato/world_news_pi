# MOBILE.md

## 1. Target

Android and iOS.

## 2. Framework

Flutter is the initial candidate.

The framework decision may be revisited after the API prototype is stable.

## 3. Responsibilities

Mobile app:

- map rendering
- event filtering
- event detail
- API connection
- optional notifications in a later phase

Backend:

- news collection
- LLM analysis
- event management
- geocoding
- persistence

## 4. No direct LAN assumption

The first mobile prototype may run on the home LAN.

The production app MUST NOT assume that users can directly reach a private-home IP address.

## 5. Future public architecture

Before App Store / Google Play release, add a secure public access layer.

Candidate:

mobile app
 -> HTTPS public API
 -> authentication/rate limiting/cache
 -> secure tunnel/VPN or controlled home/cloud backend
 -> Pi4

The exact production hosting design is a later architecture decision.

## 6. Real-time updates

Initial mobile version may poll.

Later version may use WebSocket or Server-Sent Events if the public architecture supports it.

## 7. Map provider

The map implementation MUST use a provider and tile usage model compatible with redistribution and mobile application usage.

Do not assume that a free public tile endpoint is suitable for production-scale app distribution.
