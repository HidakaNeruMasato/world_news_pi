# World News Map — Map Density & Marker Aggregation Analysis (T022-1)

## 1. Problem Definition
Following the T021 Phase 3 RSS expansion, the number of active news events on the map increased significantly (e.g. 200+ events globally).
In high-volume areas such as Europe (50+ events), South Asia (55+ events), and East Asia (40+ events), rendering individual Leaflet circle markers at fixed coordinates causes severe marker overlap.

## 2. Evaluation of Density Handling Alternatives

| Approach | Discoverability | Geographic Accuracy | Clickability | Performance | Mobile Usability | Recommendation |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| **A. Current Individual Markers** | Poor (overlapped) | High | Poor (hidden markers) | High | Poor | Not Recommended |
| **B. Leaflet Marker Clustering** | High (number badges) | Medium (grouped) | High | High | High | **Recommended (Option B/E Hybrid)** |
| **C. Region Aggregation Only** | High (regional count) | Low (coarse) | Medium | High | High | Partial |
| **D. Zoom-Dependent Rendering** | Medium | High | Medium | Medium | Medium | Supplementary |
| **E. Hybrid Cluster + Regional Bar** | High | High | High | High | High | **Top Choice** |

## 3. Recommended Density Architecture (Hybrid Cluster + Regional Overview)
1. **Zoom Levels 2 - 4 (World/Continent View)**:
   - Render cluster badges for close proximity events (e.g. `<CircleCluster count={12} region="Europe" />`).
   - Clicking a cluster zooms the map in to expand the contained events (`spiderfy` / zoom bounds).
2. **Zoom Levels 5 - 18 (Country/City View)**:
   - Expand into individual category-colored circle markers.
   - Maintain exact geocoded coordinates (zero coordinate alteration / zero fake locations).
3. **Selection Persistence**:
   - When an event is selected, its marker remains highlighted and elevated above surrounding markers (`bringToFront()`).
