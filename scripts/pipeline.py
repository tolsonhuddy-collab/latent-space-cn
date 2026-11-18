#!/usr/bin/env python3
"""Editorial pipeline CLI for Latent Space 中文精读: status, publish, audit-git."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog" / "episodes.json"
HOMEPAGE_PATH = ROOT / "site" / "homepage.json"
SITE_ZH_DIR = ROOT / "site" / "zh"

FORBIDDEN_GIT_PREFIXES = (
    "private/",
    "dist/",
    "grok/",
    "argon-noetik/",
    "inputs/",
    "content/",
    "source/",
    "sources/",
    ".env",
)


def extract_h1(md_text: str) -> str:
    for line in md_text.splitlines():
        s = line.strip()
        if s.startswith("# "):
            return s[2:].strip()
    return ""


def cmd_status() -> None:
    if not CATALOG_PATH.exists():
        print("catalog/episodes.json not found.")
        return
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    episodes = data.get("episodes", [])
    published = sum(1 for ep in episodes if (SITE_ZH_DIR / f"{ep['id']}.md").exists())
    print(f"Catalog: {len(episodes)} episodes | Published in site/zh: {published}")
    for ep in episodes:
        ep_id = ep["id"]
        has_md = (SITE_ZH_DIR / f"{ep_id}.md").exists()
        has_meta = (SITE_ZH_DIR / f"{ep_id}.json").exists()
        state = "published" if (has_md and has_meta) else ep.get("status", "pending")
        title_display = ep.get("title_zh") or ep.get("title_en", "")
        print(f"  [{ep.get('number', '---')}] {ep_id:24s} {state:10s} {title_display[:52]}")


def cmd_publish(ep_id: str, md_file: Path, set_featured: bool = False) -> None:
    if not md_file.exists():
        sys.exit(f"Error: markdown file not found: {md_file}")
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    episodes = catalog.get("episodes", [])
    target_ep = next((e for e in episodes if e["id"] == ep_id or e.get("number") == ep_id), None)
    if not target_ep:
        sys.exit(f"Error: episode '{ep_id}' not found in catalog/episodes.json")

    canonical_id = target_ep["id"]
    md_text = md_file.read_text(encoding="utf-8")
    h1_title = extract_h1(md_text)
    if h1_title:
        target_ep["title_zh"] = h1_title
    target_ep["status"] = "reviewed"

    SITE_ZH_DIR.mkdir(parents=True, exist_ok=True)
    dest_md = SITE_ZH_DIR / f"{canonical_id}.md"
    dest_json = SITE_ZH_DIR / f"{canonical_id}.json"
    shutil.copy2(md_file, dest_md)

    meta = {
        "id": canonical_id,
        "number": target_ep.get("number", ""),
        "title_zh": target_ep.get("title_zh", ""),
        "title_en": target_ep.get("title_en", ""),
        "guests": target_ep.get("guests", []),
        "org": target_ep.get("org", ""),
        "hosts": target_ep.get("hosts", ["swyx", "Alessio"]),
        "published_at": target_ep.get("published_at", ""),
        "duration_minutes": target_ep.get("duration_minutes", 0),
        "source_url": target_ep.get("source_url", "https://www.latent.space/"),
        "source_note": "依据 Latent Space 官方英文逐字稿整理编写，删去广告与寒暄，未逐一核实提及的研究与原始数据，原节目请见 Latent Space 官网。",
    }
    dest_json.write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    CATALOG_PATH.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    if set_featured and HOMEPAGE_PATH.exists():
        hp = json.loads(HOMEPAGE_PATH.read_text(encoding="utf-8"))
        hp["featured_id"] = canonical_id
        HOMEPAGE_PATH.write_text(json.dumps(hp, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    cjk_count = len(re.findall(r"[\u4e00-\u9fff]", md_text))
    print(f"Published {canonical_id} ({cjk_count:,} CJK chars): {target_ep.get('title_zh')}")


def cmd_audit_git() -> None:
    res = subprocess.run(
        ["git", "-C", str(ROOT), "ls-files"],
        capture_output=True,
        text=True,
        check=True,
    )
    tracked = [line.strip() for line in res.stdout.splitlines() if line.strip()]
    leaks = [f for f in tracked if f.startswith(FORBIDDEN_GIT_PREFIXES)]
    if leaks:
        sys.exit(f"Git audit FAILED! Private or build files tracked: {leaks}")
    print(f"Git audit PASSED ({len(tracked)} public files tracked, 0 private leaks).")


def main() -> None:
    parser = argparse.ArgumentParser(description="Latent Space 中文精读 pipeline helper")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show catalog and published status")
    sub.add_parser("audit-git", help="Verify no private or dist files are tracked by git")

    pub_p = sub.add_parser("publish", help="Ingest a finished markdown article into site/zh/")
    pub_p.add_argument("--id", required=True, help="Episode id or 3-digit number (e.g. 002 or 002-kohli-protein)")
    pub_p.add_argument("--md", required=True, help="Path to finished markdown file")
    pub_p.add_argument("--featured", action="store_true", help="Also set this episode as homepage featured")

    args = parser.parse_args()
    if args.command == "status":
        cmd_status()
    elif args.command == "audit-git":
        cmd_audit_git()
    elif args.command == "publish":
        cmd_publish(args.id, Path(args.md), set_featured=args.featured)


if __name__ == "__main__":
    main()
