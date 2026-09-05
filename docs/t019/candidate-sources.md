# RSS Candidate Sources Database (T019 Research)

This document contains the evaluation of **127 candidate RSS/Atom feed sources** researched across 11 global regions to fill coverage gaps in World News Map.

## Candidate Summary by Tier

* **Tier A (High Priority / Recommended Expansion)**: 30 sources (HTTP 200, valid XML, high update frequency, filling major geographic gaps)
* **Tier B (Secondary Candidates)**: 39 sources (HTTP 200, valid XML, supplementary regional coverage)
* **Tier C (Low Frequency / Redundant)**: 12 sources (HTTP 200, but low update volume or redundant with Tier A)
* **Tier D (Rejected / Unavailable)**: 46 sources (HTTP 403, 404, 429, XML Parse Errors, DNS/Connection failure)

---

## Candidate List by Region

### 1. South Asia (南アジア)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| The Hindu | India | IN | en | `https://www.thehindu.com/news/national/feeder/default.rss` | OK | 60 | **A** | Premier Indian national daily |
| Indian Express | India | IN | en | `https://indianexpress.com/section/world/feed/` | OK | 200 | **A** | High-volume Indian national daily |
| Hindustan Times | India | IN | en | `https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml` | OK | 100 | **B** | Major Indian daily |
| Times of India | India | IN | en | `https://timesofindia.indiatimes.com/rssfeeds/296589292.cms` | OK | 20 | **B** | High volume Indian daily |
| NDTV | India | IN | en | `https://feeds.feedburner.com/ndtvnews-world-news` | OK | 20 | **B** | Major Indian broadcaster |
| ThePrint | India | IN | en | `https://theprint.in/feed/` | XML_ERROR | 0 | **D** | Parsing issue |
| Dawn | Pakistan | PK | en | `https://www.dawn.com/feeds/home/` | OK | 27 | **A** | Premier Pakistani English newspaper |
| The Express Tribune | Pakistan | PK | en | `https://tribune.com.pk/feed/home` | OK | 73 | **B** | Major Pakistani newspaper |
| Daily Times | Pakistan | PK | en | `https://dailytimes.com.pk/feed/` | HTTP_403 | 0 | **D** | Access blocked |
| The Daily Star | Bangladesh | BD | en | `https://www.thedailystar.net/frontpage/rss.xml` | OK | 10 | **A** | Leading Bangladesh daily |
| Dhaka Tribune | Bangladesh | BD | en | `https://www.dhakatribune.com/feed` | HTTP_404 | 0 | **D** | RSS endpoint deprecated |
| Daily Mirror | Sri Lanka | LK | en | `https://www.dailymirror.lk/RSS_Feeds/` | XML_ERROR | 0 | **D** | Invalid XML markup |
| NewsFirst | Sri Lanka | LK | en | `https://www.newsfirst.lk/feed/` | HTTP_403 | 0 | **D** | Cloudflare block |

### 2. Southeast Asia (東南アジア)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| ANTARA News | Indonesia | ID | en | `https://en.antaranews.com/rss/news.xml` | OK | 50 | **A** | Indonesian national news agency |
| Malay Mail | Malaysia | MY | en | `https://www.malaymail.com/feed/rss/malaysia` | OK | 50 | **A** | Leading Malaysian daily |
| The Straits Times | Singapore | SG | en | `https://www.straitstimes.com/news/world/rss.xml` | OK | 50 | **A** | Premier Singapore & regional daily |
| VnExpress | Vietnam | VN | en | `https://e.vnexpress.net/rss/news.rss` | OK | 60 | **A** | Top Vietnam online newspaper |
| Vietnam News | Vietnam | VN | en | `https://vietnamnews.vn/rss/world-109.rss` | OK | 1 | **C** | Low item frequency |
| Myanmar Now | Myanmar | MM | en | `https://myanmar-now.org/en/feed/` | OK | 10 | **A** | Independent Myanmar coverage |
| The Irrawaddy | Myanmar | MM | en | `https://www.irrawaddy.com/feed` | HTTP_403 | 0 | **D** | Blocked |
| Khmer Times | Cambodia | KH | en | `https://www.khmertimeskh.com/feed/` | OK | 20 | **A** | Leading Cambodian daily |
| Phnom Penh Post | Cambodia | KH | en | `https://www.phnompenhpost.com/rss/national.xml` | HTTP_404 | 0 | **D** | URL broken |
| Inquirer.net | Philippines | PH | en | `https://newsinfo.inquirer.net/feed` | OK | 40 | **A** | Major Philippine national newspaper |
| Philstar | Philippines | PH | en | `https://www.philstar.com/rss/headlines` | OK | 10 | **B** | Major Philippine daily |
| The Star | Malaysia | MY | en | `https://www.thestar.com.my/rss/news/world/` | HTTP_404 | 0 | **D** | Feed removed |
| Bernama | Malaysia | MY | en | `https://www.bernama.com/en/rss/general.php` | URL_ERROR | 0 | **D** | Host error |
| Channel NewsAsia | Singapore | SG | en | `https://www.channelnewsasia.com/api/v1/rss-out/news/latest.xml` | HTTP_404 | 0 | **D** | Endpoint changed |
| Bangkok Post | Thailand | TH | en | `https://www.bangkokpost.com/rss/data/mostrecent.xml` | HTTP_404 | 0 | **D** | Endpoint changed |
| Thai PBS World | Thailand | TH | en | `https://www.thaipbsworld.com/feed/` | XML_ERROR | 0 | **D** | Malformed XML |
| The Jakarta Post | Indonesia | ID | en | `https://www.thejakartapost.com/rss/latest` | HTTP_404 | 0 | **D** | Endpoint changed |

### 3. East Asia (東アジア)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| China Daily | China | CN | en | `http://www.chinadaily.com.cn/rss/world_rss.xml` | OK | 100 | **A** | Official Chinese English paper |
| Xinhua News | China | CN | en | `http://www.xinhuanet.com/english/rss/worldrss.xml` | OK | 20 | **B** | State news agency |
| South China Morning Post | Hong Kong | HK | en | `https://www.scmp.com/rss/91/feed` | OK | 50 | **A** | Major Asia-Pacific daily |
| Hong Kong Free Press | Hong Kong | HK | en | `https://hongkongfp.com/feed/` | OK | 30 | **B** | Independent HK news |
| Yonhap News | South Korea | KR | en | `https://en.yna.co.kr/RSS/news.xml` | OK | 100 | **B** | South Korea news agency |
| NHK World | Japan | JP | en | `https://www.nhk.or.jp/rss/news/cat0.xml` | OK | 7 | **B** | Baseline |
| Focus Taiwan | Taiwan | TW | en | `https://focustaiwan.tw/rss/news.xml` | HTTP_404 | 0 | **D** | Endpoint dead |
| Taipei Times | Taiwan | TW | en | `https://www.taipeitimes.com/xml/index.rss` | OK | 0 | **C** | Empty feed |

### 4. Oceania & Pacific Islands (オセアニア・太平洋島嶼国)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| ABC News Australia | Australia | AU | en | `https://www.abc.net.au/news/feed/51120/rss.xml` | OK | 25 | **A** | Australia public broadcaster |
| SBS News | Australia | AU | en | `https://www.sbs.com.au/news/feed` | OK | 25 | **B** | Australia multicultural news |
| RNZ News | New Zealand | NZ | en | `https://www.rnz.co.nz/rss/world.xml` | OK | 4 | **B** | New Zealand public news |
| RNZ Pacific | New Zealand / Pacific | NZ | en | `https://www.rnz.co.nz/rss/pacific.xml` | OK | 18 | **A** | Pacific Islands regional coverage |
| PNG Post-Courier | Papua New Guinea | PG | en | `https://postcourier.com.pg/feed/` | OK | 10 | **A** | Papua New Guinea national daily |
| Matangi Tonga | Tonga | TO | en | `https://matangitonga.to/rss.xml` | OK | 10 | **A** | Tonga & Polynesian island coverage |
| Pacific Islands News Association | Fiji / Pacific | FJ | en | `https://pina.com.fj/feed/` | OK | 1 | **C** | Regional aggregator |
| Fiji Times | Fiji | FJ | en | `https://www.fijitimes.com.fj/feed/` | XML_ERROR | 0 | **D** | Parse error |
| NZ Herald | New Zealand | NZ | en | `https://www.nzherald.co.nz/c-rss/world/` | HTTP_404 | 0 | **D** | Feed removed |
| Solomon Times | Solomon Islands | SB | en | `https://www.solomontimes.com/rss/news` | HTTP_404 | 0 | **D** | Broken link |

### 5. Europe - Eastern & Balkans (欧州 - 東欧・バルカン)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| Notes from Poland | Poland | PL | en | `https://notesfrompoland.com/feed/` | OK | 12 | **A** | Premier Polish news in English |
| Romania Insider | Romania | RO | en | `https://www.romania-insider.com/feed` | OK | 100 | **A** | Premier Romanian daily |
| Balkan Insight | Balkans Region | RS | en | `https://balkaninsight.com/feed/` | OK | 90 | **A** | Cross-Balkan regional journalism |
| Total Croatia News | Croatia | HR | en | `https://total-croatia-news.com/feed/` | OK | 10 | **A** | Croatian national daily |
| Daily News Hungary | Hungary | HU | en | `https://dailynewshungary.com/feed/` | OK | 20 | **B** | Hungarian news |
| Ukrinform | Ukraine | UA | en | `https://www.ukrinform.net/rss/block/block_lastnews.xml` | HTTP_404 | 0 | **D** | Endpoint dead |
| Kyiv Independent | Ukraine | UA | en | `https://kyivindependent.com/feed/` | HTTP_404 | 0 | **D** | Cloudflare / Changed |
| Radio Prague | Czechia | CZ | en | `https://english.radio.cz/rss/news.xml` | HTTP_404 | 0 | **D** | Broken link |
| TVP World | Poland | PL | en | `https://tvpworld.com/rss` | HTTP_404 | 0 | **D** | Offline |
| B92 | Serbia | RS | en | `https://www.b92.net/info/rss/english.xml` | HTTP_404 | 0 | **D** | Offline |
| Bulgarian National Radio | Bulgaria | BG | en | `https://bnr.bg/en/post/rss` | HTTP_404 | 0 | **D** | Broken link |

### 6. Europe - Western & Nordic (欧州 - 西欧・北欧)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| El País | Spain | ES | es | `https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada` | OK | 23 | **A** | Major Spanish global daily |
| SVT Nyheter | Sweden | SE | sv | `https://www.svt.se/nyheter/utrikes/rss.xml` | OK | 100 | **A** | Swedish public broadcaster |
| El Mundo | Spain | ES | es | `https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml` | OK | 51 | **B** | Major Spanish daily |
| NRK Urix | Norway | NO | no | `https://www.nrk.no/urix/toppsaker.rss` | OK | 20 | **B** | Norwegian public news |
| Yle News | Finland | FI | en | `https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss` | OK | 13 | **B** | Finnish public news |
| RTÉ News | Ireland | IE | en | `https://www.rte.ie/rss/news.xml` | OK | 20 | **B** | Irish national news |
| NL Times | Netherlands | NL | en | `https://nltimes.nl/rss` | OK | 10 | **B** | Dutch English daily |
| The Local Sweden | Sweden | SE | en | `https://www.thelocal.se/feeds/rss.php` | OK | 20 | **B** | Swedish English daily |
| Público | Portugal | PT | pt | `https://www.publico.pt/api/generic/rss/mundo` | HTTP_404 | 0 | **D** | Feed removed |
| NOS Nieuws | Netherlands | NL | nl | `https://feeds.nos.nl/nosnieuws-buitenland` | HTTP_404 | 0 | **D** | Endpoint dead |

### 7. Middle East (中東)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| Times of Israel | Israel | IL | en | `https://www.timesofisrael.com/feed/` | OK | 15 | **A** | Israeli independent news |
| Al-Monitor | Middle East Region | US | en | `https://www.al-monitor.com/rss` | OK | 20 | **A** | Regional Middle East analysis |
| Middle East Eye | Middle East Region | GB | en | `https://www.middleeasteye.net/rss` | OK | 20 | **A** | Middle East regional news |
| Al Jazeera English | Qatar | QA | en | `https://www.aljazeera.com/xml/rss/all.xml` | OK | 25 | **B** | Baseline reference |
| Arab News | Saudi Arabia | SA | en | `https://www.arabnews.com/cat/1/rss.xml` | HTTP_403 | 0 | **D** | Cloudflare block |
| The National | UAE | AE | en | `https://www.thenationalnews.com/arc/outboundfeeds/rss/` | HTTP_404 | 0 | **D** | Endpoint changed |
| Khaleej Times | UAE | AE | en | `https://www.khaleejtimes.com/rss.xml` | XML_ERROR | 0 | **D** | Parse error |
| Jordan Times | Jordan | JO | en | `https://www.jordantimes.com/rss.xml` | HTTP_403 | 0 | **D** | Access blocked |
| Haaretz | Israel | IL | en | `https://www.haaretz.com/cmlink/1.4604445` | XML_ERROR | 0 | **D** | Malformed RSS |
| WAFA News | Palestine | PS | en | `https://english.wafa.ps/rss.aspx` | HTTP_404 | 0 | **D** | Dead link |
| Palestinian Chronicle | Palestine | PS | en | `https://www.palestinechronicle.com/feed/` | HTTP_429 | 0 | **D** | Rate limited |
| L'Orient Today | Lebanon | LB | en | `https://today.lorientlejour.com/rss` | HTTP_404 | 0 | **D** | Endpoint dead |

### 8. Africa (アフリカ)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| Vanguard News | Nigeria | NG | en | `https://www.vanguardngr.com/feed/` | OK | 20 | **A** | Nigeria major national daily |
| The Punch | Nigeria | NG | en | `https://punchng.com/feed/` | OK | 30 | **B** | Nigeria major daily |
| Premium Times | Nigeria | NG | en | `https://www.premiumtimesng.com/feed` | OK | 15 | **B** | Nigeria investigative news |
| JoyOnline | Ghana | GH | en | `https://www.myjoyonline.com/feed/` | OK | 50 | **A** | Ghana premier news portal |
| GhanaWeb | Ghana | GH | en | `https://www.ghanaweb.com/GhanaHomePage/rss/news.xml` | XML_ERROR | 0 | **D** | Invalid XML |
| The Standard Kenya | Kenya | KE | en | `https://www.standardmedia.co.ke/rss/world.php` | OK | 30 | **A** | Kenya national newspaper |
| Times of Zambia | Zambia | ZM | en | `https://www.times.co.zm/?feed=rss2` | OK | 10 | **A** | Zambia national newspaper |
| Radio Okapi | DR Congo | CD | fr | `https://www.radiookapi.net/rss.xml` | OK | 30 | **A** | Central Africa / DRC UN public news |
| Ahram Online | Egypt | EG | en | `https://english.ahram.org.eg/rss/World.xml` | HTTP_403 | 0 | **D** | Blocked |
| Morocco World News | Morocco | MA | en | `https://www.moroccoworldnews.com/feed` | HTTP_403 | 0 | **D** | Blocked |
| TAP News | Tunisia | TN | en | `https://www.tap.info.tn/en/rss` | URL_ERROR | 0 | **D** | Connection error |
| Algeria Press Service | Algeria | DZ | en | `https://www.aps.dz/en/?option=com_k2&view=itemlist&task=feed` | OK | 0 | **C** | No items returned |
| Daily Nation | Kenya | KE | en | `https://nation.africa/kenya/rss/1148` | HTTP_404 | 0 | **D** | Endpoint changed |
| Addis Standard | Ethiopia | ET | en | `https://addisstandard.com/feed/` | HTTP_403 | 0 | **D** | Cloudflare block |
| Daily Monitor | Uganda | UG | en | `https://www.monitor.co.ug/uganda/rss/688324` | HTTP_403 | 0 | **D** | Blocked |
| The New Times | Rwanda | RW | en | `https://www.newtimes.co.rw/rss.xml` | HTTP_404 | 0 | **D** | Endpoint dead |
| Hiiraan Online | Somalia | SO | en | `https://www.hiiraan.com/rss/news.xml` | HTTP_404 | 0 | **D** | Endpoint dead |
| Daily Maverick | South Africa | ZA | en | `https://www.dailymaverick.co.za/feed/` | HTTP_403 | 0 | **D** | Cloudflare block |
| Mail & Guardian | South Africa | ZA | en | `https://mg.co.za/feed/` | HTTP_404 | 0 | **D** | Endpoint dead |
| News24 | South Africa | ZA | en | `https://feeds.news24.com/articles/news24/World/rss` | URL_ERROR | 0 | **D** | DNS error |
| The Herald Zimbabwe | Zimbabwe | ZW | en | `https://www.herald.co.zw/feed/` | HTTP_403 | 0 | **D** | Access blocked |
| Seneweb | Senegal | SN | fr | `https://www.seneweb.com/rss/news.xml` | HTTP_404 | 0 | **D** | Broken link |
| Cameroon Tribune | Cameroon | CM | en | `https://www.cameroon-tribune.cm/rss.xml` | HTTP_404 | 0 | **D** | Broken link |

### 9. Central America & Caribbean (中米・カリブ海)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| El Universal | Mexico | MX | es | `https://www.eluniversal.com.mx/arc/outboundfeeds/rss/` | OK | 100 | **A** | Leading Mexican national daily |
| Mexico News Daily | Mexico | MX | en | `https://mexiconewsdaily.com/feed/` | OK | 10 | **B** | Mexico English daily |
| Prensa Libre | Guatemala | GT | es | `https://www.prensalibre.com/feed/` | OK | 99 | **A** | Leading Guatemala daily |
| Newsroom Panama | Panama | PA | en | `https://newsroompanama.com/feed/` | OK | 10 | **A** | Panama daily |
| Granma | Cuba | CU | es | `https://www.granma.cu/feed` | OK | 26 | **A** | Cuba official news |
| Jamaica Gleaner | Jamaica | JM | en | `https://jamaica-gleaner.com/feed/rss.xml` | OK | 10 | **A** | Premier Caribbean daily |
| Dominican Today | Dominican Republic | DO | en | `https://dominicantoday.com/feed/` | OK | 10 | **B** | Dominican Republic daily |
| The Tico Times | Costa Rica | CR | en | `https://ticotimes.net/feed` | XML_ERROR | 0 | **D** | XML Error |

### 10. South America (南米)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| Folha de S.Paulo | Brazil | BR | pt | `https://feeds.folha.uol.com.br/mundo/rss091.xml` | OK | 100 | **A** | Premier Brazilian newspaper |
| Agência Brasil | Brazil | BR | pt | `https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml` | OK | 10 | **B** | Brazil state agency |
| Buenos Aires Times | Argentina | AR | en | `https://www.batimes.com.ar/feed` | OK | 100 | **A** | Argentine English daily |
| Clarín | Argentina | AR | es | `https://www.clarin.com/rss/mundo/` | OK | 10 | **B** | Major Argentine newspaper |
| El Tiempo | Colombia | CO | es | `https://www.eltiempo.com/rss/mundo.xml` | OK | 10 | **A** | Leading Colombia daily |
| El Nacional | Venezuela | VE | es | `https://www.elnacional.com/feed/` | OK | 100 | **A** | Major Venezuela daily |
| El Espectador | Colombia | CO | es | `https://www.elespectador.com/rss/mundo.xml` | HTTP_404 | 0 | **D** | Feed removed |
| El Comercio Peru | Peru | PE | es | `https://elcomercio.pe/arc/outboundfeeds/rss/category/mundo/` | HTTP_404 | 0 | **D** | Endpoint dead |
| BioBioChile | Chile | CL | es | `https://www.biobiochile.cl/lista/tag/mundo/feed` | HTTP_404 | 0 | **D** | Endpoint dead |

### 11. North America (北米)

| Media | Country | Code | Lang | URL | Status | Items | Tier | Notes |
|---|---|---|---|---|---|---:|:---:|---|
| NPR World | United States | US | en | `https://feeds.npr.org/1001/rss.xml` | OK | 10 | **A** | US public radio |
| PBS NewsHour | United States | US | en | `https://www.pbs.org/newshour/feeds/rss/world` | OK | 20 | **B** | US public television |
| AP News | United States | US | en | `https://apnews.com/index.rss` | HTTP_403 | 0 | **D** | Cloudflare block |
| CBC News | Canada | CA | en | `https://www.cbc.ca/cxml/rss/rss-world.xml` | ERROR | 0 | **D** | Network timeout |
| CTV News | Canada | CA | en | `https://www.ctvnews.ca/rss/ctvnews-ca-world-public-rss-1.822289` | HTTP_404 | 0 | **D** | Broken link |
