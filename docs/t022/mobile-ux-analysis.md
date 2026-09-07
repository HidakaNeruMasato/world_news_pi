# World News Map — Mobile UX & Responsiveness Analysis (T022-1)

## 1. Viewport Audit Targets
- Mobile Small: 390 x 844 (iPhone 12/13/14/15)
- Mobile Medium/Tablet: 768 x 1024 (iPad / Tablet)
- Desktop: 1440 x 900 (Standard Desktop)

## 2. Current Mobile UX Flaws
1. **Vertical Stacking Conflict**: On viewports `< 768px`, `EventList` stacks vertically above `MapView`, forcing users to scroll past the entire list before seeing the map canvas.
2. **Detail Panel Obscuration**: `EventDetailPanel` uses `absolute top-4 right-4 w-96 max-w-[calc(100vw-2rem)]`, completely covering the map on mobile screens when open.
3. **Filter Bar Overflow**: Dropdowns overflow horizontally without clear mobile touch targets.

## 3. Recommended Mobile Information Architecture (Bottom-Sheet Pattern)

```text
+------------------------------------+
|  [Header & Region Pills]           |
+------------------------------------+
|                                    |
|          WORLD MAP CANVAS          |
|            (Full Screen)           |
|                                    |
+------------------------------------+
|  [=== Drag Handle / Event Pill ===]|
|  Active Events (135) - Tap to expand|
|------------------------------------|
|  - Event Card 1                    |
|  - Event Card 2                    |
+------------------------------------+
```

### Key Responsive Design Rules:
- **Mobile Mode (`< 768px`)**:
  - Fullscreen Map view by default.
  - Collapsible **Bottom Sheet** for Event List & Event Detail.
  - Tapping a map marker slides up the Bottom Sheet showing Event Detail.
  - Tapping drag handle expands Event List overlay.
- **Desktop Mode (`>= 768px`)**:
  - Side-by-side layout: Sidebar Event List (Left 320px) + Map Canvas (Flex-1) + Right Overlay Detail Panel (380px).
