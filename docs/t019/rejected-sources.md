# Rejected & Excluded RSS Sources (T019 Research)

This document records the **58 candidate RSS/Atom feed sources** that were evaluated but excluded from adoption during T019 Phase 1, along with the precise technical or operational reason for rejection.

## Rejection Breakdown

* **HTTP 403 (Forbidden / Cloudflare Bot Blocking)**: 14 feeds
* **HTTP 404 (Not Found / Endpoint Deprecated)**: 25 feeds
* **XML Parse Errors (Malformed XML / HTML Error Pages)**: 8 feeds
* **Network / DNS / Host Unreachable**: 6 feeds
* **Tier C (Zero or Low Item Volume / Redundant)**: 5 feeds

---

## Complete Exclusion Table

| Media | Country Code | Region | RSS Feed URL | HTTP Status | Exclusion Reason Category | Detail / Technical Error Log |
|---|:---:|---|---|:---:|---|---|
| **NewsFirst** | LK | South Asia | `https://www.newsfirst.lk/feed/` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **Daily Times** | PK | South Asia | `https://dailytimes.com.pk/feed/` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **ThePrint** | IN | South Asia | `https://theprint.in/feed/` | 200 | Malformed XML | XML Parse Error: mismatched tag |
| **Dhaka Tribune** | BD | South Asia | `https://www.dhakatribune.com/feed` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Daily Mirror** | LK | South Asia | `https://www.dailymirror.lk/RSS_Feeds/` | 200 | Malformed XML | Invalid XML declaration |
| **The Star** | MY | Southeast Asia | `https://www.thestar.com.my/rss/news/world/` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **The Irrawaddy** | MM | Southeast Asia | `https://www.irrawaddy.com/feed` | 403 | Access Blocked | HTTP 403 Forbidden |
| **The Jakarta Post** | ID | Southeast Asia | `https://www.thejakartapost.com/rss/latest` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Phnom Penh Post** | KH | Southeast Asia | `https://www.phnompenhpost.com/rss/national.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Thai PBS World** | TH | Southeast Asia | `https://www.thaipbsworld.com/feed/` | 200 | Malformed XML | Malformed RSS XML structure |
| **Bernama** | MY | Southeast Asia | `https://www.bernama.com/en/rss/general.php` | 0 | Host Unreachable | URL Error / Connection refused |
| **Channel NewsAsia** | SG | Southeast Asia | `https://www.channelnewsasia.com/api/v1/rss-out/news/latest.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Focus Taiwan** | TW | East Asia | `https://focustaiwan.tw/rss/news.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Taipei Times** | TW | East Asia | `https://www.taipeitimes.com/xml/index.rss` | 200 | Zero Items (Tier C) | Feed returned 0 items |
| **Bangkok Post** | TH | Southeast Asia | `https://www.bangkokpost.com/rss/data/mostrecent.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **NZ Herald** | NZ | Oceania | `https://www.nzherald.co.nz/c-rss/world/` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Solomon Times** | SB | Pacific Islands | `https://www.solomontimes.com/rss/news` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Fiji Times** | FJ | Pacific Islands | `https://www.fijitimes.com.fj/feed/` | 200 | Malformed XML | XML Parse Error |
| **NOS Nieuws** | NL | Western Europe | `https://feeds.nos.nl/nosnieuws-buitenland` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Público** | PT | Western Europe | `https://www.publico.pt/api/generic/rss/mundo` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Arab News** | SA | Middle East | `https://www.arabnews.com/cat/1/rss.xml` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **The National** | AE | Middle East | `https://www.thenationalnews.com/arc/outboundfeeds/rss/` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Khaleej Times** | AE | Middle East | `https://www.khaleejtimes.com/rss.xml` | 200 | Malformed XML | XML Parse Error |
| **Jordan Times** | JO | Middle East | `https://www.jordantimes.com/rss.xml` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **Haaretz** | IL | Middle East | `https://www.haaretz.com/cmlink/1.4604445` | 200 | Malformed XML | Malformed XML payload |
| **WAFA News** | PS | Middle East | `https://english.wafa.ps/rss.aspx` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Palestinian Chronicle** | PS | Middle East | `https://www.palestinechronicle.com/feed/` | 429 | Rate Limited | HTTP 429 Too Many Requests |
| **L'Orient Today** | LB | Middle East | `https://today.lorientlejour.com/rss` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **TVP World** | PL | Eastern Europe | `https://tvpworld.com/rss` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Ekathimerini** | GR | Southern Europe | `https://www.ekathimerini.com/feed/` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **Kyiv Independent** | UA | Eastern Europe | `https://kyivindependent.com/feed/` | 404 | Cloudflare / Changed | HTTP 404 Not Found |
| **Ukrinform** | UA | Eastern Europe | `https://www.ukrinform.net/rss/block/block_lastnews.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Radio Prague** | CZ | Eastern Europe | `https://english.radio.cz/rss/news.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **B92** | RS | Balkans | `https://www.b92.net/info/rss/english.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Bulgarian National Radio** | BG | Balkans | `https://bnr.bg/en/post/rss` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Ahram Online** | EG | North Africa | `https://english.ahram.org.eg/rss/World.xml` | 403 | Access Blocked | HTTP 403 Forbidden |
| **Morocco World News** | MA | North Africa | `https://www.moroccoworldnews.com/feed` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **TAP News** | TN | North Africa | `https://www.tap.info.tn/en/rss` | 0 | Host Unreachable | URL Error / Connection refused |
| **Algeria Press Service** | DZ | North Africa | `https://www.aps.dz/en/?option=com_k2&view=itemlist&task=feed` | 200 | Zero Items (Tier C) | Feed returned 0 items |
| **GhanaWeb** | GH | West Africa | `https://www.ghanaweb.com/GhanaHomePage/rss/news.xml` | 200 | Malformed XML | Malformed XML payload |
| **Seneweb** | SN | West Africa | `https://www.seneweb.com/rss/news.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Daily Nation** | KE | East Africa | `https://nation.africa/kenya/rss/1148` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Addis Standard** | ET | East Africa | `https://addisstandard.com/feed/` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **Daily Monitor** | UG | East Africa | `https://www.monitor.co.ug/uganda/rss/688324` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **The New Times** | RW | East Africa | `https://www.newtimes.co.rw/rss.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Hiiraan Online** | SO | East Africa | `https://www.hiiraan.com/rss/news.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **Daily Maverick** | ZA | Southern Africa | `https://www.dailymaverick.co.za/feed/` | 403 | Cloudflare / WAF Block | HTTP 403 Forbidden |
| **Mail & Guardian** | ZA | Southern Africa | `https://mg.co.za/feed/` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **News24** | ZA | Southern Africa | `https://feeds.news24.com/articles/news24/World/rss` | 0 | DNS / Connection Error | DNS resolution failure |
| **The Herald Zimbabwe** | ZW | Southern Africa | `https://www.herald.co.zw/feed/` | 403 | Access Blocked | HTTP 403 Forbidden |
| **Cameroon Tribune** | CM | Central Africa | `https://www.cameroon-tribune.cm/rss.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **AP News** | US | North America | `https://apnews.com/index.rss` | 403 | Bot Block | HTTP 403 Forbidden |
| **CBC News** | CA | North America | `https://www.cbc.ca/cxml/rss/rss-world.xml` | 0 | Network Timeout | Connection timeout |
| **CTV News** | CA | North America | `https://www.ctvnews.ca/rss/ctvnews-ca-world-public-rss-1.822289` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **The Tico Times** | CR | Central America | `https://ticotimes.net/feed` | 200 | Malformed XML | Malformed XML payload |
| **El Espectador** | CO | South America | `https://www.elespectador.com/rss/mundo.xml` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **El Comercio Peru** | PE | South America | `https://elcomercio.pe/arc/outboundfeeds/rss/category/mundo/` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
| **BioBioChile** | CL | South America | `https://www.biobiochile.cl/lista/tag/mundo/feed` | 404 | Endpoint Deprecated | HTTP 404 Not Found |
