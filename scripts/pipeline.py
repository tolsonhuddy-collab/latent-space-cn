#!/usr/bin/env python3
"""Minimal editorial pipeline status & check CLI for Latent Space 中文精读."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CATALOG_PATH = ROOT / "catalog" / "episodes.json"
SITE_ZH_DIR = ROOT / "site" / "zh"


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
        print(f"  [{ep.get('number', '---')}] {ep_id:24s} {state:10s} {ep.get('title_en', '')[:60]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Latent Space 中文精读 pipeline helper")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("status", help="Show catalog and published status")
    args = parser.parse_args()
    if args.command == "status":
        cmd_status()


if __name__ == "__main__":
    main()
