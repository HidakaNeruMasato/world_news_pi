# Current Baseline RSS Sources Inventory

This document lists all RSS/Atom feed sources currently registered and configured in the World News Map baseline system (`config.example.yaml`) and used in production testing (T015–T018).

## Baseline Registered Feeds

| ID | Media | Country | Country Code | Region | Feed URL | Type | Status |
|---|---|---|---|---|---|---|---|
| 1 | NHK News Top | Japan | JP | East Asia | `https://www.nhk.or.jp/rss/news/cat0.xml` | RSS 2.0 | Enabled |
| 2 | BBC News World | United Kingdom | GB | Western Europe | `http://feeds.bbci.co.uk/news/world/rss.xml` | RSS 2.0 | Enabled |

## Production Validation Active Feeds (T015-T018 Reference Sets)

The following 16 media outlets represent the reference active feeds ingested during real-world production tests (T015 through T018):

| # | Media | Country Code | Region | Language | Active in Production |
|---|---|---|---|---|---|
| 1 | NHK World / NHK News | JP | East Asia | ja / en | Yes |
| 2 | Asahi Shimbun | JP | East Asia | ja | Yes |
| 3 | Yomiuri Shimbun | JP | East Asia | ja | Yes |
| 4 | Mainichi Shimbun | JP | East Asia | ja | Yes |
| 5 | Kyodo News | JP | East Asia | ja / en | Yes |
| 6 | Japan Times | JP | East Asia | en | Yes |
| 7 | BBC News | GB | Western Europe | en | Yes |
| 8 | Reuters | US | North America / Global | en | Yes |
| 9 | France 24 | FR | Western Europe | en / fr | Yes |
| 10 | Deutsche Welle | DE | Western Europe | en / de | Yes |
| 11 | ANSA | IT | Southern Europe | en / it | Yes |
| 12 | Al Jazeera | QA | Middle East | en | Yes |
| 13 | CBC News | CA | North America | en | Yes |
| 14 | Yonhap News | KR | East Asia | en / ko | Yes |
| 15 | Manila Bulletin | PH | Southeast Asia | en | Yes |
| 16 | El Comercio | PE | South America | es | Yes |

## Inventory Summary & Geographic Gap Analysis

* **Total Baseline Registered Feeds**: 2
* **Total Ingested Sources (T015-T018)**: 16
* **Current Regional Distribution**:
  * East Asia: 7 (JP: 6, KR: 1)
  * Western/Southern Europe: 4 (GB: 1, FR: 1, DE: 1, IT: 1)
  * North America: 2 (US: 1, CA: 1)
  * Middle East: 1 (QA: 1)
  * Southeast Asia: 1 (PH: 1)
  * South America: 1 (PE: 1)
  * South Asia: **0**
  * Eastern Europe / Balkans: **0**
  * Nordic Europe: **0**
  * North / West / East / Southern / Central Africa: **0**
  * Central America / Caribbean: **0**
  * Oceania / Pacific Islands: **0**
