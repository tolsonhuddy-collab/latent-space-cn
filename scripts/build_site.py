#!/usr/bin/env python3
"""Static site builder for Latent Space 中文精读 (Python 3.9+ stdlib)."""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
from datetime import datetime, timezone
from email.utils import format_datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
CATALOG_PATH = ROOT / "catalog" / "episodes.json"
HOMEPAGE_PATH = ROOT / "site" / "homepage.json"
SITE_ZH_DIR = ROOT / "site" / "zh"
PRIVATE_ARTICLES_DIR = ROOT / "private" / "articles"
PRIVATE_META_DIR = ROOT / "private" / "metadata"


def format_date_zh(iso_date: str) -> str:
    if not iso_date:
        return ""
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", iso_date.strip())
    if not m:
        return html.escape(iso_date)
    return f"{m.group(1)}年{m.group(2)}月{m.group(3)}日"


def render_inline_md(text: str) -> str:
    escaped = html.escape(text, quote=False)
    # Links [label](url)
    escaped = re.sub(
        r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
        lambda m: f'<a href="{html.escape(m.group(2), quote=True)}" target="_blank" rel="noopener noreferrer">{m.group(1)}</a>',
        escaped,
    )
    # Inline code
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    # Bold
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    # Italic
    escaped = re.sub(r"\*([^*]+)\*", r"<em>\1</em>", escaped)
    return escaped


def markdown_to_html(md_text: str) -> Tuple[str, List[Tuple[str, str]], str]:
    """Convert article markdown into HTML, returning (body_html, toc_items, extracted_h1)."""
    lines = md_text.splitlines()
    out: List[str] = []
    toc: List[Tuple[str, str]] = []
    extracted_h1 = ""
    para_buf: List[str] = []
    list_buf: List[str] = []
    quote_buf: List[str] = []
    sec_idx = 0

    def flush_para() -> None:
        if para_buf:
            joined = " ".join(s.strip() for s in para_buf)
            out.append(f"<p>{render_inline_md(joined)}</p>")
            para_buf.clear()

    def flush_list() -> None:
        if list_buf:
            items = "".join(f"<li>{render_inline_md(item)}</li>" for item in list_buf)
            out.append(f"<ul>{items}</ul>")
            list_buf.clear()

    def flush_quote() -> None:
        if quote_buf:
            joined = " ".join(s.strip() for s in quote_buf)
            out.append(f"<blockquote><p>{render_inline_md(joined)}</p></blockquote>")
            quote_buf.clear()

    for raw in lines:
        line = raw.rstrip()
        stripped = line.strip()

        if not stripped:
            flush_para()
            flush_list()
            flush_quote()
            continue

        if stripped.startswith("# ") and not extracted_h1:
            flush_para()
            flush_list()
            flush_quote()
            extracted_h1 = stripped[2:].strip()
            continue

        if stripped.startswith("## "):
            flush_para()
            flush_list()
            flush_quote()
            sec_idx += 1
            heading = stripped[3:].strip()
            sec_id = f"section-{sec_idx}"
            num_str = f"{sec_idx:02d}"
            toc.append((sec_id, f"{num_str} {heading}"))
            out.append(
                f'<h2 id="{sec_id}"><span class="sec-num">{num_str}</span>{render_inline_md(heading)}</h2>'
            )
            continue

        if stripped.startswith("### "):
            flush_para()
            flush_list()
            flush_quote()
            out.append(f"<h3>{render_inline_md(stripped[4:].strip())}</h3>")
            continue

        if stripped.startswith("> "):
            flush_para()
            flush_list()
            quote_buf.append(stripped[2:].strip())
            continue

        if stripped.startswith("- ") or stripped.startswith("* "):
            flush_para()
            flush_quote()
            list_buf.append(stripped[2:].strip())
            continue

        flush_list()
        flush_quote()
        para_buf.append(stripped)

    flush_para()
    flush_list()
    flush_quote()
    return "\n".join(out), toc, extracted_h1


def load_json(path: Path, default: dict) -> dict:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def build_demo_data() -> Tuple[dict, List[dict], Dict[str, Tuple[dict, str]]]:
    homepage = {
        "site_title": "Latent Space 中文精读",
        "site_subtitle": "来自硅谷，AI for Science 最前沿的讨论",
        "featured_id": "002-demo",
        "featured_label": "最新精读",
        "footer_lines": [
            "非官方中文精读项目，主要整理 Latent Space Science 子频道的科学长谈。",
            "所有内容基于公开逐字稿整理、翻译与校订，旨在降低中文读者的长文阅读门槛。",
            "原节目版权归原播客所有，本站不替代原音频或原文，欢迎支持原节目。",
        ],
    }
    episodes = [
        {
            "id": "001-demo",
            "number": "001",
            "title_en": "Lab in the Loop — Demo Episode One",
            "title_zh": "示例精读一：实验闭环与科学模型",
            "guests": ["Guest A"],
            "org": "Demo Lab",
            "published_at": "2026-01-15",
            "duration_minutes": 80,
            "source_url": "https://www.latent.space/",
            "status": "reviewed",
        },
        {
            "id": "002-demo",
            "number": "002",
            "title_en": "BioAI Phase Shift — Demo Episode Two",
            "title_zh": "示例精读二：蛋白质设计正在进入软件迭代循环",
            "guests": ["Guest B", "Guest C"],
            "org": "Demo Bio",
            "published_at": "2026-02-26",
            "duration_minutes": 95,
            "source_url": "https://www.latent.space/",
            "status": "reviewed",
        },
        {
            "id": "003-demo",
            "number": "003",
            "title_en": "Foundation Models for Physics — Demo Episode Three",
            "title_zh": "",
            "guests": ["Guest D"],
            "org": "Demo Institute",
            "published_at": "2026-03-05",
            "duration_minutes": 75,
            "source_url": "https://www.latent.space/",
            "status": "pending",
        },
    ]
    articles = {
        "001-demo": (
            episodes[0],
            "# 示例精读一：实验闭环与科学模型\n\n## 实验数据决定了模型的上限\n\n这是一个用于验证静态站点构建与排版效果的示例正文。",
        ),
        "002-demo": (
            episodes[1],
            "# 示例精读二：蛋白质设计正在进入软件迭代循环\n\n## 从结构预测走向可控设计\n\n这是一个用于验证首页推荐位与文章页渲染的示例正文。",
        ),
    }
    return homepage, episodes, articles


def collect_published_data(private_mode: bool = False) -> Tuple[dict, List[dict], Dict[str, Tuple[dict, str]]]:
    homepage = load_json(
        HOMEPAGE_PATH,
        {
            "site_title": "Latent Space 中文精读",
            "site_subtitle": "来自硅谷，AI for Science 最前沿的讨论",
            "featured_id": "",
            "featured_label": "最新精读",
            "footer_lines": [],
        },
    )
    catalog = load_json(CATALOG_PATH, {"episodes": []})
    episodes: List[dict] = catalog.get("episodes", [])

    articles: Dict[str, Tuple[dict, str]] = {}
    md_dir = PRIVATE_ARTICLES_DIR if private_mode else SITE_ZH_DIR
    meta_dir = PRIVATE_META_DIR if private_mode else SITE_ZH_DIR

    for ep in episodes:
        ep_id = ep["id"]
        md_path = md_dir / f"{ep_id}.md"
        meta_path = meta_dir / f"{ep_id}.json"
        if md_path.exists():
            md_text = md_path.read_text(encoding="utf-8")
            meta = load_json(meta_path, ep)
            merged = {**ep, **meta}
            articles[ep_id] = (merged, md_text)
            if not ep.get("title_zh") and merged.get("title_zh"):
                ep["title_zh"] = merged["title_zh"]
            ep["status"] = "reviewed"

    return homepage, episodes, articles


def render_featured_html(homepage: dict, episodes: List[dict], articles: Dict[str, Tuple[dict, str]]) -> str:
    feat_id = homepage.get("featured_id") or ""
    feat_ep: Optional[dict] = None
    if feat_id and feat_id in articles:
        feat_ep = articles[feat_id][0]
    else:
        for ep in episodes:
            if ep["id"] in articles:
                feat_ep = articles[ep["id"]][0]
                break

    if not feat_ep:
        return ""

    ep_id = feat_ep["id"]
    title_zh = html.escape(feat_ep.get("title_zh") or feat_ep.get("title_en") or "")
    title_en = html.escape(feat_ep.get("title_en") or "")
    guests = ", ".join(feat_ep.get("guests") or [])
    org = feat_ep.get("org") or ""
    date_zh = format_date_zh(feat_ep.get("published_at") or "")
    dur = feat_ep.get("duration_minutes")
    source_url = feat_ep.get("source_url") or "https://www.latent.space/"

    meta_parts = [p for p in [guests, org, date_zh, f"约 {dur} 分钟" if dur else ""] if p]
    meta_html = " · ".join(html.escape(p) for p in meta_parts)
    if source_url:
        meta_html += f' · <a href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">原节目页</a>'

    kicker = html.escape(homepage.get("featured_label") or "最新精读")
    article_href = f"episodes/{html.escape(ep_id, quote=True)}.html"
    cover = feat_ep.get("cover") or ""
    if cover:
        cover_inner = f'<img src="{html.escape(cover, quote=True)}" alt="{title_en}" loading="eager" />'
        cover_class = "featured-cover has-cover"
    else:
        cover_inner = f'<span class="cover-badge">封面占位</span><span class="cover-en-caption">{title_en}</span>'
        cover_class = "featured-cover"

    return f"""
    <section class="featured-section">
      <div class="container">
        <div class="featured-grid">
          <a class="{cover_class}" href="{article_href}">
            {cover_inner}
          </a>
          <div class="featured-body">
            <div class="featured-kicker">{kicker}</div>
            <h2 class="featured-title"><a href="{article_href}">{title_zh}</a></h2>
            <p class="featured-en">{title_en}</p>
            <p class="featured-meta">{meta_html}</p>
            <a class="btn-outline" href="{article_href}">阅读全文</a>
          </div>
        </div>
      </div>
    </section>
    """.strip()


def render_episode_cards(episodes: List[dict], articles: Dict[str, Tuple[dict, str]]) -> str:
    cards: List[str] = []
    for ep in episodes:
        ep_id = ep["id"]
        num = html.escape(ep.get("number") or "")
        is_pub = ep_id in articles
        merged = articles[ep_id][0] if is_pub else ep
        title_en = merged.get("title_en") or ""
        title_zh = merged.get("title_zh") or ""
        guests = ", ".join(merged.get("guests") or [])
        org = merged.get("org") or ""
        date_zh = format_date_zh(merged.get("published_at") or "")
        dur = merged.get("duration_minutes")
        source_url = merged.get("source_url") or ""

        status_label = "" if is_pub else "待精读"
        article_href = f"episodes/{html.escape(ep_id, quote=True)}.html"

        search_blob = " ".join(p for p in [num, title_zh, title_en, guests, org, status_label] if p)
        guests_line = " · ".join(p for p in [guests, org] if p)

        meta_parts = [p for p in [date_zh, f"约 {dur} 分钟" if dur else ""] if p]
        meta_html = " · ".join(html.escape(p) for p in meta_parts)
        if source_url:
            sep = " · " if meta_html else ""
            meta_html += f'{sep}<a href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">原节目页</a>'

        cover = merged.get("cover") or ""
        img_html = (
            f'<img src="{html.escape(cover, quote=True)}" alt="{html.escape(title_en, quote=True)}" loading="lazy" />'
            if cover
            else ""
        )
        thumb_cls = "card-thumb has-cover" if cover else "card-thumb"
        if is_pub:
            thumb_html = (
                f'<a class="{thumb_cls}" href="{article_href}">'
                f"{img_html}"
                f'<span class="card-num">{num}</span>'
                f"</a>"
            )
            title_html = f'<h3 class="card-title"><a href="{article_href}">{html.escape(title_zh or title_en)} ↗</a></h3>'
        else:
            thumb_html = (
                f'<div class="{thumb_cls}">'
                f"{img_html}"
                f'<span class="card-num">{num}</span>'
                f'<span class="card-badge">{status_label}</span>'
                f"</div>"
            )
            title_html = f'<h3 class="card-title">{html.escape(title_en)}</h3>'

        card_class = "episode-card is-published" if is_pub else "episode-card"
        cards.append(
            f'<article class="{card_class}" data-search="{html.escape(search_blob, quote=True)}">'
            f"{thumb_html}"
            f'<div class="card-status-line">{num}{" · " + status_label if status_label else ""}</div>'
            f"{title_html}"
            f'<p class="card-en">{html.escape(title_en)}</p>'
            f'<p class="card-guests">{html.escape(guests_line)}</p>'
            f'<div class="card-meta">{meta_html}</div>'
            f"</article>"
        )
    return "\n".join(cards)


def _parse_iso_date_utc(iso_date: str) -> datetime:
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})", (iso_date or "").strip())
    if m:
        return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)), tzinfo=timezone.utc)
    return datetime(2026, 1, 1, tzinfo=timezone.utc)


def _sort_feed_items_desc(published_items: List[Tuple[dict, str, str]]) -> List[Tuple[dict, str, str]]:
    return sorted(
        published_items,
        key=lambda item: (item[0].get("published_at") or "", item[0].get("number") or ""),
        reverse=True,
    )


def build_atom_feed(
    site_title: str,
    site_subtitle: str,
    base_url: str,
    published_items: List[Tuple[dict, str, str]],
) -> str:
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    site_link = base_url.rstrip("/") + "/" if base_url else "index.html"
    feed_url = base_url.rstrip("/") + "/feed.xml" if base_url else "feed.xml"
    feed_id = base_url.rstrip("/") + "/feed.xml" if base_url else "urn:latent-space-cn:feed"

    entries: List[str] = []
    for meta, body_html, _ in _sort_feed_items_desc(published_items):
        ep_id = meta["id"]
        title = html.escape(meta.get("title_zh") or meta.get("title_en") or ep_id)
        link = f"{base_url.rstrip('/')}/episodes/{ep_id}.html" if base_url else f"episodes/{ep_id}.html"
        pub_date = meta.get("published_at") or "2026-01-01"
        updated = f"{pub_date}T00:00:00Z"
        author_name = html.escape(", ".join(meta.get("guests") or []) or site_title)
        entries.append(
            f"  <entry>\n"
            f"    <title>{title}</title>\n"
            f'    <link href="{html.escape(link, quote=True)}" rel="alternate" type="text/html" />\n'
            f"    <id>{html.escape(link)}</id>\n"
            f"    <published>{updated}</published>\n"
            f"    <updated>{updated}</updated>\n"
            f"    <author><name>{author_name}</name></author>\n"
            f'    <content type="html">{html.escape(body_html)}</content>\n'
            f"  </entry>"
        )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<feed xmlns="http://www.w3.org/2005/Atom">\n'
        f"  <title>{html.escape(site_title)}</title>\n"
        f"  <subtitle>{html.escape(site_subtitle)}</subtitle>\n"
        f'  <link href="{html.escape(site_link, quote=True)}" rel="alternate" type="text/html" />\n'
        f'  <link href="{html.escape(feed_url, quote=True)}" rel="self" type="application/atom+xml" />\n'
        f"  <id>{html.escape(feed_id)}</id>\n"
        f"  <updated>{now_iso}</updated>\n"
        f"  <author><name>{html.escape(site_title)}</name></author>\n"
        + "\n".join(entries)
        + "\n</feed>\n"
    )


def build_rss_feed(
    site_title: str,
    site_subtitle: str,
    base_url: str,
    published_items: List[Tuple[dict, str, str]],
) -> str:
    now_rfc822 = format_datetime(datetime.now(timezone.utc), usegmt=True)
    site_link = base_url.rstrip("/") + "/" if base_url else "index.html"
    rss_url = base_url.rstrip("/") + "/rss.xml" if base_url else "rss.xml"
    is_abs = "true" if base_url else "false"

    items_xml: List[str] = []
    for meta, body_html, _ in _sort_feed_items_desc(published_items):
        ep_id = meta["id"]
        title_raw = meta.get("title_zh") or meta.get("title_en") or ep_id
        title = html.escape(title_raw)
        link = f"{base_url.rstrip('/')}/episodes/{ep_id}.html" if base_url else f"episodes/{ep_id}.html"
        pub_dt = _parse_iso_date_utc(meta.get("published_at") or "")
        pub_rfc822 = format_datetime(pub_dt, usegmt=True)
        summary_parts = [
            p for p in [meta.get("title_en") or "", ", ".join(meta.get("guests") or []), meta.get("org") or ""] if p
        ]
        summary_text = " · ".join(summary_parts) if summary_parts else title_raw
        safe_cdata_body = body_html.replace("]]>", "]]]]><![CDATA[>")
        items_xml.append(
            f"    <item>\n"
            f"      <title>{title}</title>\n"
            f"      <link>{html.escape(link)}</link>\n"
            f'      <guid isPermaLink="{is_abs}">{html.escape(link)}</guid>\n'
            f"      <pubDate>{pub_rfc822}</pubDate>\n"
            f"      <description>{html.escape(summary_text)}</description>\n"
            f"      <content:encoded><![CDATA[{safe_cdata_body}]]></content:encoded>\n"
            f"    </item>"
        )
    return (
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<rss version="2.0" xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:atom="http://www.w3.org/2005/Atom">\n'
        "  <channel>\n"
        f"    <title>{html.escape(site_title)}</title>\n"
        f"    <link>{html.escape(site_link)}</link>\n"
        f"    <description>{html.escape(site_subtitle)}</description>\n"
        "    <language>zh-CN</language>\n"
        f"    <lastBuildDate>{now_rfc822}</lastBuildDate>\n"
        f'    <atom:link href="{html.escape(rss_url, quote=True)}" rel="self" type="application/rss+xml" />\n'
        + "\n".join(items_xml)
        + "\n  </channel>\n"
        "</rss>\n"
    )


def build_opml(site_title: str, base_url: str) -> str:
    feed_url = (base_url.rstrip("/") + "/feed.xml") if base_url else "feed.xml"
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<opml version="2.0">\n'
        "  <head>\n"
        f"    <title>{html.escape(site_title)}</title>\n"
        "  </head>\n"
        "  <body>\n"
        f'    <outline text="{html.escape(site_title, quote=True)}" title="{html.escape(site_title, quote=True)}" type="rss" xmlUrl="{html.escape(feed_url, quote=True)}" />\n'
        "  </body>\n"
        "</opml>\n"
    )


def build_site(mode: str, out_dir: Path, base_url: str = "") -> None:
    if mode == "demo":
        homepage, episodes, articles = build_demo_data()
    elif mode == "private":
        homepage, episodes, articles = collect_published_data(private_mode=True)
    else:
        homepage, episodes, articles = collect_published_data(private_mode=False)

    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "episodes").mkdir(parents=True, exist_ok=True)
    (out_dir / "podcasts" / "latent-space").mkdir(parents=True, exist_ok=True)

    # Copy static assets
    for asset in ("style.css", "app.js"):
        shutil.copy2(WEB_DIR / asset, out_dir / asset)
    covers_src = ROOT / "site" / "covers"
    if mode != "demo" and covers_src.is_dir():
        shutil.copytree(covers_src, out_dir / "covers")

    site_title = homepage.get("site_title") or "Latent Space 中文精读"
    site_subtitle = homepage.get("site_subtitle") or "来自硅谷，AI for Science 最前沿的讨论"
    total_count = len(episodes)
    pub_count = sum(1 for ep in episodes if ep["id"] in articles)
    stats_text = f"{total_count} 期节目" if pub_count == total_count else f"{total_count} 期节目 · {total_count - pub_count} 期待精读"

    footer_lines = homepage.get("footer_lines") or []
    footer_lines_html = "\n".join(f"<p>{html.escape(line)}</p>" for line in footer_lines)

    featured_html = render_featured_html(homepage, episodes, articles)
    cards_html = render_episode_cards(episodes, articles)

    index_tpl = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    index_html = (
        index_tpl.replace("{{SITE_TITLE}}", html.escape(site_title))
        .replace("{{SITE_SUBTITLE}}", html.escape(site_subtitle))
        .replace("{{BASE_PATH}}", "")
        .replace("{{STATS_TEXT}}", html.escape(stats_text))
        .replace("{{FEATURED_HTML}}", featured_html)
        .replace("{{TOTAL_COUNT}}", str(total_count))
        .replace("{{PUBLISHED_COUNT}}", str(pub_count))
        .replace("{{EPISODE_CARDS_HTML}}", cards_html)
        .replace("{{FOOTER_LINES_HTML}}", footer_lines_html)
    )
    (out_dir / "index.html").write_text(index_html, encoding="utf-8")

    # Build article pages in catalog order
    published_ordered: List[Tuple[dict, str, str]] = []
    for ep in episodes:
        ep_id = ep["id"]
        if ep_id in articles:
            meta, md_text = articles[ep_id]
            body_html, toc_items, extracted_h1 = markdown_to_html(md_text)
            if not meta.get("title_zh") and extracted_h1:
                meta["title_zh"] = extracted_h1
            toc_html = "\n".join(
                f'<li><a href="#{html.escape(sec_id)}">{html.escape(label)}</a></li>'
                for sec_id, label in toc_items
            )
            published_ordered.append((meta, body_html, toc_html))

    article_tpl = (WEB_DIR / "article.html").read_text(encoding="utf-8")
    for idx, (meta, body_html, toc_html) in enumerate(published_ordered):
        ep_id = meta["id"]
        num = meta.get("number") or ""
        title_zh = meta.get("title_zh") or meta.get("title_en") or ep_id
        title_en = meta.get("title_en") or ""
        guests = ", ".join(meta.get("guests") or [])
        org = meta.get("org") or ""
        date_zh = format_date_zh(meta.get("published_at") or "")
        dur = meta.get("duration_minutes")
        source_url = meta.get("source_url") or ""
        source_note = meta.get("source_note") or "依据公开英文逐字稿整理编写，删去广告与寒暄。"

        meta_parts = [p for p in [guests, org, date_zh, f"原节目约 {dur} 分钟" if dur else ""] if p]
        cjk_chars = len(re.findall(r"[\u4e00-\u9fff]", body_html))
        if cjk_chars > 0:
            read_mins = max(1, round(cjk_chars / 450))
            meta_parts.append(f"约 {cjk_chars:,} 字 · 阅读 {read_mins} 分钟")
        meta_text = " · ".join(html.escape(p) for p in meta_parts)
        if source_url:
            meta_text += f' · <a href="{html.escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">原节目 ↗</a>'

        prev_html = ""
        if idx > 0:
            pm = published_ordered[idx - 1][0]
            prev_html = f'<a href="{html.escape(pm["id"], quote=True)}.html">← 上一篇：{html.escape(pm.get("number", ""))} {html.escape(pm.get("title_zh") or pm.get("title_en") or "")}</a>'

        next_html = ""
        if idx + 1 < len(published_ordered):
            nm = published_ordered[idx + 1][0]
            next_html = f'<a href="{html.escape(nm["id"], quote=True)}.html">下一篇：{html.escape(nm.get("number", ""))} {html.escape(nm.get("title_zh") or nm.get("title_en") or "")} →</a>'

        cover = meta.get("cover") or ""
        og_meta = ""
        cover_html = ""
        if cover:
            og_url = f"{base_url.rstrip('/')}/{cover}" if base_url else f"../{cover}"
            og_meta = (
                f'<meta property="og:image" content="{html.escape(og_url, quote=True)}" />\n'
                f'  <meta name="twitter:card" content="summary_large_image" />'
            )
            cover_html = (
                f'<figure class="article-cover"><img src="../{html.escape(cover, quote=True)}" '
                f'alt="{html.escape(title_en, quote=True)}" /></figure>'
            )

        page_html = (
            article_tpl.replace("{{SITE_TITLE}}", html.escape(site_title))
            .replace("{{BASE_PATH}}", "../")
            .replace("{{NUMBER}}", html.escape(num))
            .replace("{{TITLE_ZH}}", html.escape(title_zh))
            .replace("{{TITLE_EN}}", html.escape(title_en))
            .replace("{{META_TEXT}}", meta_text)
            .replace("{{SOURCE_NOTE}}", html.escape(source_note))
            .replace("{{TOC_HTML}}", toc_html)
            .replace("{{ARTICLE_BODY_HTML}}", body_html)
            .replace("{{PREV_LINK_HTML}}", prev_html)
            .replace("{{NEXT_LINK_HTML}}", next_html)
            .replace("{{OG_IMAGE_META}}", og_meta)
            .replace("{{COVER_HTML}}", cover_html)
            .replace("{{PUBLISHED_COUNT}}", str(pub_count))
        )
        (out_dir / "episodes" / f"{ep_id}.html").write_text(page_html, encoding="utf-8")

    # Feeds & OPML
    atom_xml = build_atom_feed(site_title, site_subtitle, base_url, published_ordered)
    rss_xml = build_rss_feed(site_title, site_subtitle, base_url, published_ordered)
    (out_dir / "feed.xml").write_text(atom_xml, encoding="utf-8")
    (out_dir / "rss.xml").write_text(rss_xml, encoding="utf-8")
    (out_dir / "podcasts" / "latent-space" / "feed.xml").write_text(atom_xml, encoding="utf-8")
    (out_dir / "latent-space-rss.opml").write_text(build_opml(site_title, base_url), encoding="utf-8")

    print(f"Built {mode} site into {out_dir} ({total_count} episodes, {pub_count} published).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build Latent Space 中文精读 static site.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--demo", action="store_true", help="Build synthetic demo site")
    group.add_argument("--private", action="store_true", help="Build from private/articles")
    group.add_argument("--published", action="store_true", help="Build from catalog/episodes.json + site/zh")
    parser.add_argument("--out", default="dist", help="Output directory (default: dist)")
    parser.add_argument("--base-url", default="", help="Optional canonical base URL for feeds")
    args = parser.parse_args()

    mode = "demo" if args.demo else ("private" if args.private else "published")
    out_path = Path(args.out)
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    build_site(mode=mode, out_dir=out_path, base_url=args.base_url)


if __name__ == "__main__":
    main()
