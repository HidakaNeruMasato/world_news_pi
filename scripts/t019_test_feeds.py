"""T019 Feed Tester & Validator

This script tests HTTP connection, XML validity, and item update metrics for global RSS/Atom feed candidates.
Output is written to docs/t019/rss-test-results.csv and docs/t019/candidate-sources.json.
"""

import sys
import os
import csv
import json
import time
import urllib.request
import urllib.error
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')


CANDIDATES = [
    # --- South Asia (IN, PK, BD, LK) ---
    {"media": "The Hindu", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://www.thehindu.com/news/national/feeder/default.rss"},
    {"media": "Indian Express", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://indianexpress.com/section/world/feed/"},
    {"media": "NDTV", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://feeds.feedburner.com/ndtvnews-world-news"},
    {"media": "Hindustan Times", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://www.hindustantimes.com/feeds/rss/world-news/rssfeed.xml"},
    {"media": "Times of India", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://timesofindia.indiatimes.com/rssfeeds/296589292.cms"},
    {"media": "ThePrint", "country": "India", "code": "IN", "region": "South Asia", "lang": "en", "url": "https://theprint.in/feed/"},
    {"media": "Dawn", "country": "Pakistan", "code": "PK", "region": "South Asia", "lang": "en", "url": "https://www.dawn.com/feeds/home/"},
    {"media": "The Express Tribune", "country": "Pakistan", "code": "PK", "region": "South Asia", "lang": "en", "url": "https://tribune.com.pk/feed/home"},
    {"media": "Daily Times", "country": "Pakistan", "code": "PK", "region": "South Asia", "lang": "en", "url": "https://dailytimes.com.pk/feed/"},
    {"media": "The Daily Star", "country": "Bangladesh", "code": "BD", "region": "South Asia", "lang": "en", "url": "https://www.thedailystar.net/frontpage/rss.xml"},
    {"media": "Dhaka Tribune", "country": "Bangladesh", "code": "BD", "region": "South Asia", "lang": "en", "url": "https://www.dhakatribune.com/feed"},
    {"media": "Daily Mirror", "country": "Sri Lanka", "code": "LK", "region": "South Asia", "lang": "en", "url": "https://www.dailymirror.lk/RSS_Feeds/"},
    {"media": "NewsFirst", "country": "Sri Lanka", "code": "LK", "region": "South Asia", "lang": "en", "url": "https://www.newsfirst.lk/feed/"},

    # --- Southeast Asia (ID, MY, SG, TH, VN, MM, KH, PH) ---
    {"media": "The Jakarta Post", "country": "Indonesia", "code": "ID", "region": "Southeast Asia", "lang": "en", "url": "https://www.thejakartapost.com/rss/latest"},
    {"media": "ANTARA News", "country": "Indonesia", "code": "ID", "region": "Southeast Asia", "lang": "en", "url": "https://en.antaranews.com/rss/news.xml"},
    {"media": "The Star", "country": "Malaysia", "code": "MY", "region": "Southeast Asia", "lang": "en", "url": "https://www.thestar.com.my/rss/news/world/"},
    {"media": "Malay Mail", "country": "Malaysia", "code": "MY", "region": "Southeast Asia", "lang": "en", "url": "https://www.malaymail.com/feed/rss/malaysia"},
    {"media": "Bernama", "country": "Malaysia", "code": "MY", "region": "Southeast Asia", "lang": "en", "url": "https://www.bernama.com/en/rss/general.php"},
    {"media": "Channel NewsAsia", "country": "Singapore", "code": "SG", "region": "Southeast Asia", "lang": "en", "url": "https://www.channelnewsasia.com/api/v1/rss-out/news/latest.xml"},
    {"media": "The Straits Times", "country": "Singapore", "code": "SG", "region": "Southeast Asia", "lang": "en", "url": "https://www.straitstimes.com/news/world/rss.xml"},
    {"media": "Bangkok Post", "country": "Thailand", "code": "TH", "region": "Southeast Asia", "lang": "en", "url": "https://www.bangkokpost.com/rss/data/mostrecent.xml"},
    {"media": "Thai PBS World", "country": "Thailand", "code": "TH", "region": "Southeast Asia", "lang": "en", "url": "https://www.thaipbsworld.com/feed/"},
    {"media": "VnExpress", "country": "Vietnam", "code": "VN", "region": "Southeast Asia", "lang": "en", "url": "https://e.vnexpress.net/rss/news.rss"},
    {"media": "Vietnam News", "country": "Vietnam", "code": "VN", "region": "Southeast Asia", "lang": "en", "url": "https://vietnamnews.vn/rss/world-109.rss"},
    {"media": "The Irrawaddy", "country": "Myanmar", "code": "MM", "region": "Southeast Asia", "lang": "en", "url": "https://www.irrawaddy.com/feed"},
    {"media": "Myanmar Now", "country": "Myanmar", "code": "MM", "region": "Southeast Asia", "lang": "en", "url": "https://myanmar-now.org/en/feed/"},
    {"media": "Khmer Times", "country": "Cambodia", "code": "KH", "region": "Southeast Asia", "lang": "en", "url": "https://www.khmertimeskh.com/feed/"},
    {"media": "Phnom Penh Post", "country": "Cambodia", "code": "KH", "region": "Southeast Asia", "lang": "en", "url": "https://www.phnompenhpost.com/rss/national.xml"},
    {"media": "Inquirer.net", "country": "Philippines", "code": "PH", "region": "Southeast Asia", "lang": "en", "url": "https://newsinfo.inquirer.net/feed"},
    {"media": "Philstar", "country": "Philippines", "code": "PH", "region": "Southeast Asia", "lang": "en", "url": "https://www.philstar.com/rss/headlines"},

    # --- East Asia (CN, TW, HK, JP, KR) ---
    {"media": "China Daily", "country": "China", "code": "CN", "region": "East Asia", "lang": "en", "url": "http://www.chinadaily.com.cn/rss/world_rss.xml"},
    {"media": "Xinhua News", "country": "China", "code": "CN", "region": "East Asia", "lang": "en", "url": "http://www.xinhuanet.com/english/rss/worldrss.xml"},
    {"media": "Focus Taiwan", "country": "Taiwan", "code": "TW", "region": "East Asia", "lang": "en", "url": "https://focustaiwan.tw/rss/news.xml"},
    {"media": "Taipei Times", "country": "Taiwan", "code": "TW", "region": "East Asia", "lang": "en", "url": "https://www.taipeitimes.com/xml/index.rss"},
    {"media": "South China Morning Post", "country": "Hong Kong", "code": "HK", "region": "East Asia", "lang": "en", "url": "https://www.scmp.com/rss/91/feed"},
    {"media": "Hong Kong Free Press", "country": "Hong Kong", "code": "HK", "region": "East Asia", "lang": "en", "url": "https://hongkongfp.com/feed/"},
    {"media": "NHK World", "country": "Japan", "code": "JP", "region": "East Asia", "lang": "en", "url": "https://www.nhk.or.jp/rss/news/cat0.xml"},
    {"media": "Yonhap News", "country": "South Korea", "code": "KR", "region": "East Asia", "lang": "en", "url": "https://en.yna.co.kr/RSS/news.xml"},

    # --- Oceania & Pacific Islands (AU, NZ, FJ, SB, PG, TO) ---
    {"media": "ABC News Australia", "country": "Australia", "code": "AU", "region": "Oceania", "lang": "en", "url": "https://www.abc.net.au/news/feed/51120/rss.xml"},
    {"media": "SBS News", "country": "Australia", "code": "AU", "region": "Oceania", "lang": "en", "url": "https://www.sbs.com.au/news/feed"},
    {"media": "RNZ News", "country": "New Zealand", "code": "NZ", "region": "Oceania", "lang": "en", "url": "https://www.rnz.co.nz/rss/world.xml"},
    {"media": "NZ Herald", "country": "New Zealand", "code": "NZ", "region": "Oceania", "lang": "en", "url": "https://www.nzherald.co.nz/c-rss/world/"},
    {"media": "RNZ Pacific", "country": "New Zealand / Pacific", "code": "NZ", "region": "Pacific Islands", "lang": "en", "url": "https://www.rnz.co.nz/rss/pacific.xml"},
    {"media": "Pacific Islands News Association", "country": "Fiji / Pacific", "code": "FJ", "region": "Pacific Islands", "lang": "en", "url": "https://pina.com.fj/feed/"},
    {"media": "Fiji Times", "country": "Fiji", "code": "FJ", "region": "Pacific Islands", "lang": "en", "url": "https://www.fijitimes.com.fj/feed/"},
    {"media": "Solomon Times", "country": "Solomon Islands", "code": "SB", "region": "Pacific Islands", "lang": "en", "url": "https://www.solomontimes.com/rss/news"},
    {"media": "PNG Post-Courier", "country": "Papua New Guinea", "code": "PG", "region": "Pacific Islands", "lang": "en", "url": "https://postcourier.com.pg/feed/"},
    {"media": "Matangi Tonga", "country": "Tonga", "code": "TO", "region": "Pacific Islands", "lang": "en", "url": "https://matangitonga.to/rss.xml"},

    # --- Europe (ES, PT, NL, SE, NO, FI, IE, PL, CZ, HU, RO, UA, RS, HR, BG, GR, Regional) ---
    {"media": "El País", "country": "Spain", "code": "ES", "region": "Western Europe", "lang": "es", "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/section/internacional/portada"},
    {"media": "El Mundo", "country": "Spain", "code": "ES", "region": "Western Europe", "lang": "es", "url": "https://e00-elmundo.uecdn.es/elmundo/rss/internacional.xml"},
    {"media": "Público", "country": "Portugal", "code": "PT", "region": "Western Europe", "lang": "pt", "url": "https://www.publico.pt/api/generic/rss/mundo"},
    {"media": "NOS Nieuws", "country": "Netherlands", "code": "NL", "region": "Western Europe", "lang": "nl", "url": "https://feeds.nos.nl/nosnieuws-buitenland"},
    {"media": "NL Times", "country": "Netherlands", "code": "NL", "region": "Western Europe", "lang": "en", "url": "https://nltimes.nl/rss"},
    {"media": "SVT Nyheter", "country": "Sweden", "code": "SE", "region": "Nordic Europe", "lang": "sv", "url": "https://www.svt.se/nyheter/utrikes/rss.xml"},
    {"media": "The Local Sweden", "country": "Sweden", "code": "SE", "region": "Nordic Europe", "lang": "en", "url": "https://www.thelocal.se/feeds/rss.php"},
    {"media": "NRK Urix", "country": "Norway", "code": "NO", "region": "Nordic Europe", "lang": "no", "url": "https://www.nrk.no/urix/toppsaker.rss"},
    {"media": "Yle News", "country": "Finland", "code": "FI", "region": "Nordic Europe", "lang": "en", "url": "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss"},
    {"media": "RTÉ News", "country": "Ireland", "code": "IE", "region": "Western Europe", "lang": "en", "url": "https://www.rte.ie/rss/news.xml"},
    {"media": "Notes from Poland", "country": "Poland", "code": "PL", "region": "Eastern Europe", "lang": "en", "url": "https://notesfrompoland.com/feed/"},
    {"media": "TVP World", "country": "Poland", "code": "PL", "region": "Eastern Europe", "lang": "en", "url": "https://tvpworld.com/rss"},
    {"media": "Radio Prague", "country": "Czechia", "code": "CZ", "region": "Eastern Europe", "lang": "en", "url": "https://english.radio.cz/rss/news.xml"},
    {"media": "Daily News Hungary", "country": "Hungary", "code": "HU", "region": "Eastern Europe", "lang": "en", "url": "https://dailynewshungary.com/feed/"},
    {"media": "Romania Insider", "country": "Romania", "code": "RO", "region": "Eastern Europe", "lang": "en", "url": "https://www.romania-insider.com/feed"},
    {"media": "Ukrinform", "country": "Ukraine", "code": "UA", "region": "Eastern Europe", "lang": "en", "url": "https://www.ukrinform.net/rss/block/block_lastnews.xml"},
    {"media": "Kyiv Independent", "country": "Ukraine", "code": "UA", "region": "Eastern Europe", "lang": "en", "url": "https://kyivindependent.com/feed/"},
    {"media": "B92", "country": "Serbia", "code": "RS", "region": "Balkans", "lang": "en", "url": "https://www.b92.net/info/rss/english.xml"},
    {"media": "Total Croatia News", "country": "Croatia", "code": "HR", "region": "Balkans", "lang": "en", "url": "https://total-croatia-news.com/feed/"},
    {"media": "Bulgarian National Radio", "country": "Bulgaria", "code": "BG", "region": "Balkans", "lang": "en", "url": "https://bnr.bg/en/post/rss"},
    {"media": "Ekathimerini", "country": "Greece", "code": "GR", "region": "Southern Europe", "lang": "en", "url": "https://www.ekathimerini.com/feed/"},
    {"media": "Balkan Insight", "country": "Balkans Region", "code": "RS", "region": "Balkans", "lang": "en", "url": "https://balkaninsight.com/feed/"},

    # --- Middle East (SA, AE, QA, JO, IL, PS, LB, Regional) ---
    {"media": "Arab News", "country": "Saudi Arabia", "code": "SA", "region": "Middle East", "lang": "en", "url": "https://www.arabnews.com/cat/1/rss.xml"},
    {"media": "The National", "country": "UAE", "code": "AE", "region": "Middle East", "lang": "en", "url": "https://www.thenationalnews.com/arc/outboundfeeds/rss/"},
    {"media": "Khaleej Times", "country": "UAE", "code": "AE", "region": "Middle East", "lang": "en", "url": "https://www.khaleejtimes.com/rss.xml"},
    {"media": "Al Jazeera English", "country": "Qatar", "code": "QA", "region": "Middle East", "lang": "en", "url": "https://www.aljazeera.com/xml/rss/all.xml"},
    {"media": "Jordan Times", "country": "Jordan", "code": "JO", "region": "Middle East", "lang": "en", "url": "https://www.jordantimes.com/rss.xml"},
    {"media": "Times of Israel", "country": "Israel", "code": "IL", "region": "Middle East", "lang": "en", "url": "https://www.timesofisrael.com/feed/"},
    {"media": "Haaretz", "country": "Israel", "code": "IL", "region": "Middle East", "lang": "en", "url": "https://www.haaretz.com/cmlink/1.4604445"},
    {"media": "WAFA News", "country": "Palestine", "code": "PS", "region": "Middle East", "lang": "en", "url": "https://english.wafa.ps/rss.aspx"},
    {"media": "Palestinian Chronicle", "country": "Palestine", "code": "PS", "region": "Middle East", "lang": "en", "url": "https://www.palestinechronicle.com/feed/"},
    {"media": "L'Orient Today", "country": "Lebanon", "code": "LB", "region": "Middle East", "lang": "en", "url": "https://today.lorientlejour.com/rss"},
    {"media": "Al-Monitor", "country": "Middle East Region", "code": "US", "region": "Middle East", "lang": "en", "url": "https://www.al-monitor.com/rss"},
    {"media": "Middle East Eye", "country": "Middle East Region", "code": "GB", "region": "Middle East", "lang": "en", "url": "https://www.middleeasteye.net/rss"},

    # --- Africa (EG, MA, TN, DZ, NG, GH, SN, KE, ET, UG, RW, SO, ZA, ZW, ZM, CD, CM) ---
    {"media": "Ahram Online", "country": "Egypt", "code": "EG", "region": "North Africa", "lang": "en", "url": "https://english.ahram.org.eg/rss/World.xml"},
    {"media": "Morocco World News", "country": "Morocco", "code": "MA", "region": "North Africa", "lang": "en", "url": "https://www.moroccoworldnews.com/feed"},
    {"media": "TAP News", "country": "Tunisia", "code": "TN", "region": "North Africa", "lang": "en", "url": "https://www.tap.info.tn/en/rss"},
    {"media": "Algeria Press Service", "country": "Algeria", "code": "DZ", "region": "North Africa", "lang": "en", "url": "https://www.aps.dz/en/?option=com_k2&view=itemlist&task=feed"},
    {"media": "Premium Times", "country": "Nigeria", "code": "NG", "region": "West Africa", "lang": "en", "url": "https://www.premiumtimesng.com/feed"},
    {"media": "Vanguard News", "country": "Nigeria", "code": "NG", "region": "West Africa", "lang": "en", "url": "https://www.vanguardngr.com/feed/"},
    {"media": "The Punch", "country": "Nigeria", "code": "NG", "region": "West Africa", "lang": "en", "url": "https://punchng.com/feed/"},
    {"media": "GhanaWeb", "country": "Ghana", "code": "GH", "region": "West Africa", "lang": "en", "url": "https://www.ghanaweb.com/GhanaHomePage/rss/news.xml"},
    {"media": "JoyOnline", "country": "Ghana", "code": "GH", "region": "West Africa", "lang": "en", "url": "https://www.myjoyonline.com/feed/"},
    {"media": "Seneweb", "country": "Senegal", "code": "SN", "region": "West Africa", "lang": "fr", "url": "https://www.seneweb.com/rss/news.xml"},
    {"media": "Daily Nation", "country": "Kenya", "code": "KE", "region": "East Africa", "lang": "en", "url": "https://nation.africa/kenya/rss/1148"},
    {"media": "The Standard Kenya", "country": "Kenya", "code": "KE", "region": "East Africa", "lang": "en", "url": "https://www.standardmedia.co.ke/rss/world.php"},
    {"media": "Addis Standard", "country": "Ethiopia", "code": "ET", "region": "East Africa", "lang": "en", "url": "https://addisstandard.com/feed/"},
    {"media": "Daily Monitor", "country": "Uganda", "code": "UG", "region": "East Africa", "lang": "en", "url": "https://www.monitor.co.ug/uganda/rss/688324"},
    {"media": "The New Times", "country": "Rwanda", "code": "RW", "region": "East Africa", "lang": "en", "url": "https://www.newtimes.co.rw/rss.xml"},
    {"media": "Hiiraan Online", "country": "Somalia", "code": "SO", "region": "East Africa", "lang": "en", "url": "https://www.hiiraan.com/rss/news.xml"},
    {"media": "Daily Maverick", "country": "South Africa", "code": "ZA", "region": "Southern Africa", "lang": "en", "url": "https://www.dailymaverick.co.za/feed/"},
    {"media": "Mail & Guardian", "country": "South Africa", "code": "ZA", "region": "Southern Africa", "lang": "en", "url": "https://mg.co.za/feed/"},
    {"media": "News24", "country": "South Africa", "code": "ZA", "region": "Southern Africa", "lang": "en", "url": "https://feeds.news24.com/articles/news24/World/rss"},
    {"media": "The Herald Zimbabwe", "country": "Zimbabwe", "code": "ZW", "region": "Southern Africa", "lang": "en", "url": "https://www.herald.co.zw/feed/"},
    {"media": "Times of Zambia", "country": "Zambia", "code": "ZM", "region": "Southern Africa", "lang": "en", "url": "https://www.times.co.zm/?feed=rss2"},
    {"media": "Radio Okapi", "country": "DR Congo", "code": "CD", "region": "Central Africa", "lang": "fr", "url": "https://www.radiookapi.net/rss.xml"},
    {"media": "Cameroon Tribune", "country": "Cameroon", "code": "CM", "region": "Central Africa", "lang": "en", "url": "https://www.cameroon-tribune.cm/rss.xml"},

    # --- North America (US, CA) ---
    {"media": "AP News", "country": "United States", "code": "US", "region": "North America", "lang": "en", "url": "https://apnews.com/index.rss"},
    {"media": "NPR World", "country": "United States", "code": "US", "region": "North America", "lang": "en", "url": "https://feeds.npr.org/1001/rss.xml"},
    {"media": "PBS NewsHour", "country": "United States", "code": "US", "region": "North America", "lang": "en", "url": "https://www.pbs.org/newshour/feeds/rss/world"},
    {"media": "CBC News", "country": "Canada", "code": "CA", "region": "North America", "lang": "en", "url": "https://www.cbc.ca/cxml/rss/rss-world.xml"},
    {"media": "CTV News", "country": "Canada", "code": "CA", "region": "North America", "lang": "en", "url": "https://www.ctvnews.ca/rss/ctvnews-ca-world-public-rss-1.822289"},

    # --- Central America & Caribbean (MX, GT, CR, PA, CU, JM, DO) ---
    {"media": "El Universal", "country": "Mexico", "code": "MX", "region": "Central America", "lang": "es", "url": "https://www.eluniversal.com.mx/arc/outboundfeeds/rss/"},
    {"media": "Mexico News Daily", "country": "Mexico", "code": "MX", "region": "Central America", "lang": "en", "url": "https://mexiconewsdaily.com/feed/"},
    {"media": "Prensa Libre", "country": "Guatemala", "code": "GT", "region": "Central America", "lang": "es", "url": "https://www.prensalibre.com/feed/"},
    {"media": "The Tico Times", "country": "Costa Rica", "code": "CR", "region": "Central America", "lang": "en", "url": "https://ticotimes.net/feed"},
    {"media": "Newsroom Panama", "country": "Panama", "code": "PA", "region": "Central America", "lang": "en", "url": "https://newsroompanama.com/feed/"},
    {"media": "Granma", "country": "Cuba", "code": "CU", "region": "Caribbean", "lang": "es", "url": "https://www.granma.cu/feed"},
    {"media": "Jamaica Gleaner", "country": "Jamaica", "code": "JM", "region": "Caribbean", "lang": "en", "url": "https://jamaica-gleaner.com/feed/rss.xml"},
    {"media": "Dominican Today", "country": "Dominican Republic", "code": "DO", "region": "Caribbean", "lang": "en", "url": "https://dominicantoday.com/feed/"},

    # --- South America (BR, AR, CL, CO, PE, VE) ---
    {"media": "Folha de S.Paulo", "country": "Brazil", "code": "BR", "region": "South America", "lang": "pt", "url": "https://feeds.folha.uol.com.br/mundo/rss091.xml"},
    {"media": "Agência Brasil", "country": "Brazil", "code": "BR", "region": "South America", "lang": "pt", "url": "https://agenciabrasil.ebc.com.br/rss/ultimasnoticias/feed.xml"},
    {"media": "Buenos Aires Times", "country": "Argentina", "code": "AR", "region": "South America", "lang": "en", "url": "https://www.batimes.com.ar/feed"},
    {"media": "Clarín", "country": "Argentina", "code": "AR", "region": "South America", "lang": "es", "url": "https://www.clarin.com/rss/mundo/"},
    {"media": "BioBioChile", "country": "Chile", "code": "CL", "region": "South America", "lang": "es", "url": "https://www.biobiochile.cl/lista/tag/mundo/feed"},
    {"media": "El Tiempo", "country": "Colombia", "code": "CO", "region": "South America", "lang": "es", "url": "https://www.eltiempo.com/rss/mundo.xml"},
    {"media": "El Espectador", "country": "Colombia", "code": "CO", "region": "South America", "lang": "es", "url": "https://www.elespectador.com/rss/mundo.xml"},
    {"media": "El Comercio Peru", "country": "Peru", "code": "PE", "region": "South America", "lang": "es", "url": "https://elcomercio.pe/arc/outboundfeeds/rss/category/mundo/"},
    {"media": "El Nacional", "country": "Venezuela", "code": "VE", "region": "South America", "lang": "es", "url": "https://www.elnacional.com/feed/"}
]

def test_single_feed(candidate):
    url = candidate["url"]
    headers = {
        "User-Agent": "WorldNewsMap/1.0 (+https://worldnews.local)",
        "Accept": "application/rss+xml, application/atom+xml, application/xml, text/xml, */*"
    }
    req = urllib.request.Request(url, headers=headers)
    
    start_t = time.time()
    res = {
        "media": candidate["media"],
        "country": candidate["country"],
        "country_code": candidate["code"],
        "region": candidate["region"],
        "language": candidate["lang"],
        "feed_url": url,
        "http_status": 0,
        "xml_valid": False,
        "item_count": 0,
        "latency_sec": 0.0,
        "last_pub_date": "",
        "status": "FAIL",
        "reason": ""
    }

    try:
        with urllib.request.urlopen(req, timeout=8) as response:
            res["http_status"] = response.status
            content = response.read()
            res["latency_sec"] = round(time.time() - start_t, 3)

            try:
                root = ET.fromstring(content)
                res["xml_valid"] = True
                
                # Check RSS <item> or Atom <entry>
                items = root.findall(".//item")
                if not items:
                    items = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                if not items:
                    items = root.findall(".//entry")
                
                res["item_count"] = len(items)
                
                if items:
                    # Get last published date if available
                    pub = items[0].find("pubDate")
                    if pub is None:
                        pub = items[0].find("{http://www.w3.org/2005/Atom}published")
                    if pub is None:
                        pub = items[0].find("dc:date")
                    if pub is not None and pub.text:
                        res["last_pub_date"] = pub.text.strip()[:30]

                if res["http_status"] == 200 and res["xml_valid"] and res["item_count"] > 0:
                    res["status"] = "OK"
                elif res["item_count"] == 0:
                    res["status"] = "NO_ITEMS"
                    res["reason"] = "No <item> or <entry> elements found"
            except Exception as e:
                res["status"] = "XML_ERROR"
                res["reason"] = f"XML Parse Error: {str(e)[:50]}"
    except urllib.error.HTTPError as e:
        res["http_status"] = e.code
        res["status"] = f"HTTP_{e.code}"
        res["reason"] = str(e)
    except urllib.error.URLError as e:
        res["status"] = "URL_ERROR"
        res["reason"] = str(e.reason)[:50]
    except Exception as e:
        res["status"] = "ERROR"
        res["reason"] = str(e)[:50]

    return res

def main():
    print(f"Testing {len(CANDIDATES)} RSS feed candidates concurrently...")
    results = []
    
    with ThreadPoolExecutor(max_workers=15) as executor:
        futures = {executor.submit(test_single_feed, c): c for c in CANDIDATES}
        for future in as_completed(futures):
            res = future.result()
            results.append(res)
            print(f"[{res['status']}] {res['media']} ({res['country_code']}) - HTTP {res['http_status']}, Items: {res['item_count']}, Latency: {res['latency_sec']}s")

    # Ensure docs/t019 exists
    os.makedirs("docs/t019", exist_ok=True)

    # Write CSV results
    csv_path = "docs/t019/rss-test-results.csv"
    fieldnames = ["media", "country", "country_code", "region", "language", "feed_url", "http_status", "xml_valid", "item_count", "latency_sec", "last_pub_date", "status", "reason"]
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(sorted(results, key=lambda x: (x["region"], x["country_code"], x["media"])))

    ok_count = sum(1 for r in results if r["status"] == "OK")
    print(f"\nCompleted testing. {ok_count} / {len(CANDIDATES)} feeds returned OK. Results saved to {csv_path}")

if __name__ == "__main__":
    main()
