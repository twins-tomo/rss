#!/usr/bin/env python3
"""GUNDAM Official Website (gundam-official.com) のニュースページから
RSS 2.0 フィードを生成するスクリプト。

公式サイトには RSS が無いため、ニュース一覧ページ
(https://gundam-official.com/news) の HTML に埋め込まれている
構造化データ (newsResponse.data) を取り出してフィード化する。

使い方:
    python3 generate_rss.py [--pages 3] [--output gundam_news.xml] [--feed-url URL]

標準ライブラリのみで動作する (Python 3.9+)。ネットワークへのアクセス先は
gundam-official.com のみ。取得間隔は控えめに (ページ間に 1 秒)。
"""

import argparse
import json
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape

BASE = "https://gundam-official.com"
NEWS_URL = BASE + "/news"
USER_AGENT = (
    "Mozilla/5.0 (compatible; gundam-rss-generator/1.0; personal RSS generator)"
)


def fetch(url: str) -> str:
    req = urllib.request.Request(
        url,
        headers={"User-Agent": USER_AGENT, "Accept-Language": "ja"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read().decode("utf-8", errors="replace")


def extract_news_items(html: str) -> list:
    """Next.js の RSC ペイロード内 "newsResponse":{"data":[...]} を取り出す。"""
    # RSC ペイロードでは引用符が \" とエスケープされている
    text = html.replace('\\"', '"')
    marker = '"newsResponse":{"data":'
    start = text.find(marker)
    if start < 0:
        raise ValueError("newsResponse がページ内に見つかりませんでした")
    arr_start = text.find("[", start)
    depth = 0
    in_str = False
    esc = False
    end = None
    for i in range(arr_start, len(text)):
        c = text[i]
        if in_str:
            if esc:
                esc = False
            elif c == "\\":
                esc = True
            elif c == '"':
                in_str = False
        else:
            if c == '"':
                in_str = True
            elif c == "[":
                depth += 1
            elif c == "]":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
    if end is None:
        raise ValueError("newsResponse の配列の終端が見つかりませんでした")
    return json.loads(text[arr_start:end])


def collect(pages: int) -> list:
    items = {}
    for page in range(1, pages + 1):
        url = NEWS_URL if page == 1 else f"{NEWS_URL}?page={page}"
        found = extract_news_items(fetch(url))
        for it in found:
            link = it.get("url")
            if link:
                items[link] = it
        if page < pages:
            time.sleep(1)
    result = sorted(
        items.values(),
        key=lambda x: x.get("displayDatetime", ""),
        reverse=True,
    )
    return result


def rfc822(iso: str) -> str:
    dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return format_datetime(dt.astimezone(timezone.utc), usegmt=True)


def build_rss(items: list, feed_url: str = "") -> str:
    now = format_datetime(datetime.now(timezone.utc), usegmt=True)
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">',
        "<channel>",
        "<title>GUNDAM Official Website - NEWS</title>",
        f"<link>{NEWS_URL}</link>",
        "<description>アニメ・映画・商品・イベントなど、ガンダムに関する最新情報"
        "（GUNDAM Official Website ニュースの非公式 RSS フィード）</description>",
        "<language>ja</language>",
        f"<lastBuildDate>{now}</lastBuildDate>",
    ]
    if feed_url:
        lines.append(
            f'<atom:link href="{escape(feed_url)}" rel="self" '
            'type="application/rss+xml"/>'
        )
    for it in items:
        title = (it.get("title") or "").strip()
        link = it.get("url") or ""
        if not title or not link:
            continue
        lines.append("<item>")
        lines.append(f"<title>{escape(title)}</title>")
        lines.append(f"<link>{escape(link)}</link>")
        lines.append(f'<guid isPermaLink="true">{escape(link)}</guid>')
        dt = it.get("displayDatetime")
        if dt:
            try:
                lines.append(f"<pubDate>{rfc822(dt)}</pubDate>")
            except ValueError:
                pass
        cats = []
        for group in ("categories", "seriesTags"):
            for c in it.get(group) or []:
                name = (c.get("name") or "").strip()
                if name and name not in cats:
                    cats.append(name)
        for name in cats:
            lines.append(f"<category>{escape(name)}</category>")
        thumb = ((it.get("thumbnail") or {}).get("url") or "").strip()
        desc_parts = []
        if cats:
            desc_parts.append(" / ".join(cats))
        if thumb:
            desc_parts.append(thumb)
        if desc_parts:
            lines.append(
                f"<description>{escape(' - '.join(desc_parts))}</description>"
            )
        lines.append("</item>")
    lines.append("</channel>")
    lines.append("</rss>")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description="gundam-official.com ニュースの RSS を生成")
    ap.add_argument("--pages", type=int, default=3,
                    help="取得する一覧ページ数 (1ページ18件, 既定: 3)")
    ap.add_argument("--output", default="gundam_news.xml",
                    help="出力先ファイル (既定: gundam_news.xml)")
    ap.add_argument("--feed-url", default="",
                    help="公開先のフィード URL (atom:link self に記載)")
    args = ap.parse_args()

    items = collect(max(1, args.pages))
    if not items:
        print("記事が取得できませんでした", file=sys.stderr)
        return 1
    xml = build_rss(items, feed_url=args.feed_url)
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"{len(items)} 件の記事で {args.output} を生成しました")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
