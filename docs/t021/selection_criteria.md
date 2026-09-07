# T021 RSS Source Selection Criteria & Evaluation Rubric

Each candidate RSS feed is evaluated across 10 dimensions (0-5 points each, total 50 points max):

1. **Reliability**: Live HTTP status and feed parsing stability.
2. **Update Frequency**: Freshness and frequent item publishing.
3. **Geographic Relevance**: Direct coverage of target priority regions.
4. **International Relevance**: Global significance of published items.
5. **Map/Event Suitability**: Compatibility with location extraction and map visualization.
6. **RSS Stability**: XML validity and endpoint permanence.
7. **Metadata Quality**: Presence of title, pubDate, GUID/ID, link, and summary.
8. **Duplicate Risk**: Uniqueness of content vs existing syndicated wire feeds.
9. **Terms/Usage Compatibility**: Open RSS distribution rights.
10. **Language Accessibility**: Readability (English, Spanish, Portuguese, etc.).

### Recommendation Threshold
- **Score >= 38 & Status Healthy**: `recommended`
- **Score < 38 & Status Healthy**: `needs_review`
- **Status Unavailable / Malformed**: `rejected`
