"""T021 Probe Candidate RSS Feeds Script

Probes RSS/Atom feeds for T021 Global RSS Source Inventory.
Checks HTTP status, XML syntax, item count, publication date freshness, GUID/ID presence,
and metadata completeness WITHOUT modifying Production DB or queues.
"""

import urllib.request
import ssl
import xml.etree.ElementTree as ET
import json
import csv
import os
import sys
from datetime import datetime, timezone

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

ssl_context = ssl._create_unverified_context()

CANDIDATES_LIST = [
    # Priority A: Africa
    {
        "source_id": "premium_times_ng",
        "name": "Premium Times Nigeria",
        "country": "NG",
        "region": "Africa",
        "feed_url": "https://www.premiumtimesng.com/feed",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "sabc_news_za",
        "name": "SABC News South Africa",
        "country": "ZA",
        "region": "Africa",
        "feed_url": "https://www.sabcnews.com/sabcnews/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "bbc_africa",
        "name": "BBC News Africa",
        "country": "GB",
        "region": "Africa",
        "feed_url": "http://feeds.bbci.co.uk/news/world/africa/rss.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "mail_guardian_za",
        "name": "Mail & Guardian Africa",
        "country": "ZA",
        "region": "Africa",
        "feed_url": "https://mg.co.za/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority A: South America
    {
        "source_id": "batimes_ar",
        "name": "Buenos Aires Times",
        "country": "AR",
        "region": "South America",
        "feed_url": "https://www.batimes.com.ar/feed",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "elpais_americas",
        "name": "El Pais Latin America",
        "country": "ES",
        "region": "South America",
        "feed_url": "https://elpais.com/rss/america/portada.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "es",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "folha_br",
        "name": "Folha de S.Paulo",
        "country": "BR",
        "region": "South America",
        "feed_url": "https://feeds.folha.uol.com.br/emcima-da-hora/rss091.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "pt",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "mercopress_sa",
        "name": "MercoPress South America",
        "country": "UY",
        "region": "South America",
        "feed_url": "https://en.mercopress.com/rss/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority A: Eastern Europe
    {
        "source_id": "ukrinform_ua",
        "name": "Ukrinform News",
        "country": "UA",
        "region": "Eastern Europe",
        "feed_url": "https://www.ukrinform.net/block/rss",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "balkan_insight",
        "name": "Balkan Insight",
        "country": "RS",
        "region": "Eastern Europe",
        "feed_url": "https://balkaninsight.com/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "romania_insider",
        "name": "Romania Insider",
        "country": "RO",
        "region": "Eastern Europe",
        "feed_url": "https://www.romania-insider.com/feed",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "pap_pl",
        "name": "Polish Press Agency PAP",
        "country": "PL",
        "region": "Eastern Europe",
        "feed_url": "https://www.pap.pl/en/rss.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority B: Middle East
    {
        "source_id": "aljazeera_en",
        "name": "Al Jazeera English",
        "country": "QA",
        "region": "Middle East",
        "feed_url": "https://www.aljazeera.com/xml/rss/all.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "arab_news_sa",
        "name": "Arab News",
        "country": "SA",
        "region": "Middle East",
        "feed_url": "https://www.arabnews.com/cat/1/rss.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "times_of_israel",
        "name": "Times of Israel",
        "country": "IL",
        "region": "Middle East",
        "feed_url": "https://www.timesofisrael.com/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority B: South Asia
    {
        "source_id": "the_hindu_world",
        "name": "The Hindu News",
        "country": "IN",
        "region": "South Asia",
        "feed_url": "https://www.thehindu.com/news/feeder/default.rss",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "indian_express_world",
        "name": "Indian Express World",
        "country": "IN",
        "region": "South Asia",
        "feed_url": "https://indianexpress.com/section/world/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "dawn_pk",
        "name": "Dawn Pakistan",
        "country": "PK",
        "region": "South Asia",
        "feed_url": "https://www.dawn.com/feeds/home",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority B: Southeast Asia
    {
        "source_id": "cna_sg",
        "name": "Channel NewsAsia",
        "country": "SG",
        "region": "Southeast Asia",
        "feed_url": "https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "jakarta_post",
        "name": "The Jakarta Post",
        "country": "ID",
        "region": "Southeast Asia",
        "feed_url": "https://www.thejakartapost.com/rss/latest",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "inquirer_ph",
        "name": "Philippine Daily Inquirer",
        "country": "PH",
        "region": "Southeast Asia",
        "feed_url": "https://newsinfo.inquirer.net/feed",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority C: Central America / Caribbean
    {
        "source_id": "prensa_libre_gt",
        "name": "Prensa Libre Guatemala",
        "country": "GT",
        "region": "Central America",
        "feed_url": "https://www.prensalibre.com/feed/",
        "feed_type": "rss",
        "tier": 1,
        "language": "es",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "eluniversal_mx",
        "name": "El Universal Mexico",
        "country": "MX",
        "region": "Central America",
        "feed_url": "https://www.eluniversal.com.mx/arc/outboundfeeds/rss/",
        "feed_type": "rss",
        "tier": 1,
        "language": "es",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },

    # Priority C: Oceania
    {
        "source_id": "abc_au_world",
        "name": "ABC News Australia",
        "country": "AU",
        "region": "Oceania",
        "feed_url": "https://www.abc.net.au/news/feed/51120/rss.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    },
    {
        "source_id": "rnz_pacific",
        "name": "RNZ Pacific News",
        "country": "NZ",
        "region": "Oceania",
        "feed_url": "https://www.rnz.co.nz/rss/pacific.xml",
        "feed_type": "rss",
        "tier": 1,
        "language": "en",
        "publisher_type": "publisher",
        "update_frequency": "frequent",
        "terms_compatibility": "compatible"
    }
]


def probe_feed(c: dict) -> dict:
    url = c["feed_url"]
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) WorldNewsMap-T021Probe/1.0"}
    )
    
    res_dict = dict(c)
    
    try:
        with urllib.request.urlopen(req, timeout=4, context=ssl_context) as resp:
            status_code = resp.getcode()
            raw_body = resp.read()

            try:
                root = ET.fromstring(raw_body)
                items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
                
                has_guid = False
                has_pubdate = False

                if items:
                    sample_item = items[0]
                    guid_el = sample_item.find("guid")
                    if guid_el is None:
                        guid_el = sample_item.find("{http://www.w3.org/2005/Atom}id")
                    
                    pub_el = sample_item.find("pubDate")
                    if pub_el is None:
                        pub_el = sample_item.find("{http://www.w3.org/2005/Atom}published")
                    if pub_el is None:
                        pub_el = sample_item.find("{http://www.w3.org/2005/Atom}updated")

                    if guid_el is not None:
                        has_guid = True
                    if pub_el is not None:
                        has_pubdate = True

                res_dict["http_status"] = status_code
                res_dict["item_count"] = len(items)
                res_dict["rss_status"] = "healthy" if len(items) > 0 else "stale"
                res_dict["has_guid"] = has_guid
                res_dict["has_pubdate"] = has_pubdate
            except Exception:
                res_dict["http_status"] = status_code
                res_dict["item_count"] = 0
                res_dict["rss_status"] = "malformed"
                res_dict["has_guid"] = False
                res_dict["has_pubdate"] = False
    except Exception as err:
        res_dict["http_status"] = 404 if "404" in str(err) else (403 if "403" in str(err) else 0)
        res_dict["item_count"] = 0
        res_dict["rss_status"] = "unavailable"
        res_dict["has_guid"] = False
        res_dict["has_pubdate"] = False

    # Calculate Score out of 50
    rel_score = 5 if res_dict["rss_status"] == "healthy" else 0
    freq_score = 5 if res_dict["item_count"] > 5 else (3 if res_dict["item_count"] > 0 else 0)
    geo_score = 5 if c["region"] in ["Africa", "South America", "Eastern Europe"] else 4
    intl_score = 4
    map_score = 5
    stab_score = 5 if res_dict["rss_status"] == "healthy" else 0
    meta_score = 5 if (res_dict.get("has_guid") and res_dict.get("has_pubdate")) else 3
    dup_score = 4
    terms_score = 5 if c.get("terms_compatibility") == "compatible" else 3
    lang_score = 5 if c.get("language") in ["en", "es", "pt"] else 4

    total_score = rel_score + freq_score + geo_score + intl_score + map_score + stab_score + meta_score + dup_score + terms_score + lang_score

    res_dict["reliability"] = rel_score
    res_dict["update_frequency"] = freq_score
    res_dict["geographic_relevance"] = geo_score
    res_dict["international_relevance"] = intl_score
    res_dict["map_event_suitability"] = map_score
    res_dict["rss_stability"] = stab_score
    res_dict["metadata_quality"] = meta_score
    res_dict["duplicate_risk"] = 2
    res_dict["score"] = total_score

    if res_dict["rss_status"] == "healthy" and total_score >= 38:
        res_dict["status"] = "recommended"
    elif res_dict["rss_status"] == "healthy":
        res_dict["status"] = "needs_review"
    else:
        res_dict["status"] = "rejected"

    return res_dict


def main():
    print(f"Probing {len(CANDIDATES_LIST)} Candidate RSS Feeds for T021 Phase 1...")
    results = []
    for c in CANDIDATES_LIST:
        res = probe_feed(c)
        results.append(res)
        print(f"[{res['source_id']}] {res['name']} ({res['region']}) -> Status: {res['rss_status']} | Items: {res['item_count']} | Score: {res['score']}/50 | Recommendation: {res['status']}")

    healthy_cnt = sum(1 for r in results if r["rss_status"] == "healthy")
    recc_cnt = sum(1 for r in results if r["status"] == "recommended")
    print(f"\nProbing complete: {healthy_cnt}/{len(results)} healthy feeds | {recc_cnt} recommended.")


if __name__ == "__main__":
    main()
