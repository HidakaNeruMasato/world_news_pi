"""RSS 2.0 / Atom 1.0 パーサーモジュール"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from email.utils import parsedate_to_datetime


@dataclass
class ParsedItem:
    """パースされたフィード記事の生データ"""
    guid: Optional[str]
    title: str
    description: Optional[str]
    link: Optional[str]
    published_raw: Optional[str]


class FeedParseError(Exception):
    """パースエラー時の例外"""
    pass


class FeedParser:
    """RSS 2.0 および Atom 1.0 フィードをパースするクラス"""

    def parse(self, xml_bytes: bytes) -> List[ParsedItem]:
        """XMLバイトデータをパースして ParsedItem のリストを返します"""
        if not xml_bytes or not xml_bytes.strip():
            return []

        try:
            root = ET.fromstring(xml_bytes)
        except ET.ParseError as e:
            raise FeedParseError(f"Malformed XML feed: {e}")

        tag = root.tag.lower()
        if "rss" in tag or root.find("channel") is not None:
            return self._parse_rss2(root)
        elif "feed" in tag:
            return self._parse_atom(root)
        else:
            # タグから直接判定できない場合、配下要素でフォールバック
            if root.find("channel") is not None:
                return self._parse_rss2(root)
            elif root.tag.endswith("feed"):
                return self._parse_atom(root)
            else:
                raise FeedParseError(f"Unknown feed format: root tag '{root.tag}'")

    def _parse_rss2(self, root: ET.Element) -> List[ParsedItem]:
        items: List[ParsedItem] = []
        channel = root.find("channel")
        if channel is None:
            channel = root

        for item in channel.findall("item"):
            title_elem = item.find("title")
            title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else ""

            desc_elem = item.find("description")
            desc = desc_elem.text.strip() if (desc_elem is not None and desc_elem.text) else None

            link_elem = item.find("link")
            link = link_elem.text.strip() if (link_elem is not None and link_elem.text) else None

            guid_elem = item.find("guid")
            guid = guid_elem.text.strip() if (guid_elem is not None and guid_elem.text) else None

            pub_elem = item.find("pubDate")
            if pub_elem is None:
                pub_elem = item.find("{http://purl.org/dc/elements/1.1/}date")
            pub_raw = pub_elem.text.strip() if (pub_elem is not None and pub_elem.text) else None

            items.append(
                ParsedItem(
                    guid=guid,
                    title=title,
                    description=desc,
                    link=link,
                    published_raw=pub_raw,
                )
            )

        return items

    def _parse_atom(self, root: ET.Element) -> List[ParsedItem]:
        items: List[ParsedItem] = []
        # Atom の名前空間処理
        ns = ""
        if root.tag.startswith("{"):
            ns = root.tag.split("}")[0] + "}"

        for entry in root.findall(f"{ns}entry"):
            title_elem = entry.find(f"{ns}title")
            title = title_elem.text.strip() if (title_elem is not None and title_elem.text) else ""

            desc_elem = entry.find(f"{ns}summary")
            if desc_elem is None or not desc_elem.text:
                desc_elem = entry.find(f"{ns}content")
            desc = desc_elem.text.strip() if (desc_elem is not None and desc_elem.text) else None

            # Atom link (rel="alternate" またはデフォルト)
            link = None
            for l_elem in entry.findall(f"{ns}link"):
                rel = l_elem.attrib.get("rel", "alternate")
                if rel in ("alternate", ""):
                    link = l_elem.attrib.get("href")
                    if link:
                        break
            if not link:
                l_elem = entry.find(f"{ns}link")
                if l_elem is not None:
                    link = l_elem.attrib.get("href") or (l_elem.text.strip() if l_elem.text else None)

            id_elem = entry.find(f"{ns}id")
            guid = id_elem.text.strip() if (id_elem is not None and id_elem.text) else None

            pub_elem = entry.find(f"{ns}published")
            if pub_elem is None:
                pub_elem = entry.find(f"{ns}updated")
            pub_raw = pub_elem.text.strip() if (pub_elem is not None and pub_elem.text) else None

            items.append(
                ParsedItem(
                    guid=guid,
                    title=title,
                    description=desc,
                    link=link,
                    published_raw=pub_raw,
                )
            )

        return items
