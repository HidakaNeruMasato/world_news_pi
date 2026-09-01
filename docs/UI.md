# UI.md

## 1. Web prototype

The first visual client is a browser-based world map.

The map is the dominant visual element.

## 2. Marker behavior

New events:

- appear immediately after API update
- start at larger visual size
- may animate once

Aging:

- marker size decreases
- opacity decreases

Expiration:

- marker is removed from active map

## 3. Marker content

At minimum:

- event type
- country
- location
- age

On selection:

- title/summary
- event type
- location
- first seen
- last seen
- confidence
- number of sources
- source links

## 4. Filters

Initial:

- event type
- country
- minimum confidence
- time window

## 5. Clustering

When many events are near each other, marker clustering SHOULD be used.

## 6. Client/server separation

The UI MUST consume the API.

It MUST NOT read server files.

## 7. Mobile-ready principle

The API data model SHOULD be sufficient for Flutter without special server-side responses for the web prototype.
