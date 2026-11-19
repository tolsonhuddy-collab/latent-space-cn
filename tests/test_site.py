import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

import build_site  # noqa: E402


class TestSiteBuild(unittest.TestCase):
    def test_catalog_valid(self) -> None:
        catalog = json.loads((ROOT / "catalog" / "episodes.json").read_text(encoding="utf-8"))
        episodes = catalog["episodes"]
        self.assertGreaterEqual(len(episodes), 20)
        ids = [ep["id"] for ep in episodes]
        self.assertEqual(len(ids), len(set(ids)))
        for ep in episodes:
            self.assertIn(ep.get("category"), build_site.CATEGORY_ORDER, ep["id"])

    def test_demo_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            build_site.build_site(mode="demo", out_dir=out)
            self.assertTrue((out / "index.html").exists())
            self.assertTrue((out / "style.css").exists())
            self.assertTrue((out / "app.js").exists())
            self.assertTrue((out / "feed.xml").exists())
            self.assertTrue((out / "rss.xml").exists())
            self.assertTrue((out / "latent-space-rss.opml").exists())
            self.assertTrue((out / "episodes" / "001-demo.html").exists())
            self.assertTrue((out / "episodes" / "002-demo.html").exists())
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("Latent Space 中文精读", html)
            self.assertIn("3 期节目 · 1 期待精读", html)
            self.assertNotIn("已定稿", html)

    def test_published_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            build_site.build_site(mode="published", out_dir=out)
            index_html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("20 期节目", index_html)
            self.assertNotIn("已定稿", index_html)
            for ep_id in (
                "001-leash-bio",
                "002-kohli-protein",
                "003-anima-physics",
                "004-chai-discovery",
                "005-lila-lab",
                "006-genesis-diffusion",
                "007-radical-ai",
                "008-materials-ai",
                "009-caspai-materials",
                "010-automating-science",
                "011-boltz",
                "012-noetik",
                "013-vibephysics",
                "014-fourth-law-drones",
                "015-esm",
                "016-axiom-math",
                "017-xaira",
                "018-john-platt",
                "019-radical-numerics",
                "020-periodic-labs",
            ):
                self.assertTrue((out / "episodes" / f"{ep_id}.html").exists())
            article_html = (out / "episodes" / "004-chai-discovery.html").read_text(encoding="utf-8")
            self.assertIn("通用蛋白质设计模型撑起了中立的新药研发软件层", article_html)
            self.assertIn('class="article-cover"', article_html)
            self.assertIn('property="og:image"', article_html)
            self.assertIn('src="covers/001-leash-bio.jpg"', index_html)
            self.assertIn('id="rss-open"', index_html)
            self.assertIn("RSS 订阅", index_html)
            self.assertIn('id="rss-modal"', index_html)
            self.assertIn("application/rss+xml", index_html)
            self.assertIn('id="rss-open"', article_html)
            self.assertIn('id="rss-modal"', article_html)
            self.assertIn("application/rss+xml", article_html)
            self.assertIn("合成超级智能需要把大模型放进真实实验室", index_html)
            for cat in build_site.CATEGORY_ORDER:
                self.assertIn(cat, index_html)
            self.assertIn('data-sort="latest"', index_html)
            self.assertIn('data-sort="number"', index_html)
            self.assertIn("万字", index_html)
            self.assertIn("阅读约", index_html)
            self.assertNotIn('<a class="card-thumb has-cover" href="episodes/001-leash-bio.html"><img src="covers/001-leash-bio.jpg" alt="Lab-in-the-Loop at Compute Speed — Ian Quigley, Leash Bio" loading="lazy" /><span class="card-num">', index_html)
            for ep_id in ("001-leash-bio", "010-automating-science", "011-boltz", "020-periodic-labs"):
                self.assertTrue((out / "covers" / f"{ep_id}.jpg").exists())

    def test_feeds_contain_all_published_episodes(self) -> None:
        import xml.etree.ElementTree as ET

        catalog = json.loads((ROOT / "catalog" / "episodes.json").read_text(encoding="utf-8"))
        expected_ids = [ep["id"] for ep in catalog["episodes"]]
        base_url = "https://tolsonhuddy-collab.github.io/latent-space-cn/"

        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            build_site.build_site(mode="published", out_dir=out, base_url=base_url)

            ns = {"a": "http://www.w3.org/2005/Atom"}
            for feed_rel in ("feed.xml", "podcasts/latent-space/feed.xml"):
                root = ET.fromstring((out / feed_rel).read_text(encoding="utf-8"))
                entries = root.findall("a:entry", ns)
                self.assertEqual(len(entries), len(expected_ids))
                seen_ids = set()
                for entry in entries:
                    link_el = entry.find("a:link", ns)
                    self.assertIsNotNone(link_el)
                    href = link_el.attrib.get("href", "")
                    ep_id = href.rsplit("/", 1)[-1].removesuffix(".html")
                    seen_ids.add(ep_id)
                    content_el = entry.find("a:content", ns)
                    self.assertIsNotNone(content_el)
                    self.assertGreater(len(content_el.text or ""), 5000, ep_id)
                self.assertEqual(seen_ids, set(expected_ids))

            rss_root = ET.fromstring((out / "rss.xml").read_text(encoding="utf-8"))
            items = rss_root.findall("./channel/item")
            self.assertEqual(len(items), len(expected_ids))
            content_ns = "{http://purl.org/rss/1.0/modules/content/}encoded"
            seen_rss_ids = set()
            for item in items:
                link = item.findtext("link", "")
                ep_id = link.rsplit("/", 1)[-1].removesuffix(".html")
                seen_rss_ids.add(ep_id)
                body = item.findtext(content_ns, "")
                self.assertGreater(len(body), 5000, ep_id)
            self.assertEqual(seen_rss_ids, set(expected_ids))

            opml_root = ET.fromstring((out / "latent-space-rss.opml").read_text(encoding="utf-8"))
            outline = opml_root.find("./body/outline")
            self.assertIsNotNone(outline)
            self.assertEqual(outline.attrib.get("xmlUrl"), f"{base_url}feed.xml")

    def test_cover_integrity(self) -> None:
        import hashlib
        catalog = json.loads((ROOT / "catalog" / "episodes.json").read_text(encoding="utf-8"))
        for ep in catalog["episodes"]:
            self.assertTrue(ep["source_url"].startswith("https://latent.space/p/"), ep["id"])
            cover = ROOT / "site" / ep["cover"]
            self.assertTrue(cover.exists(), ep["id"])
            self.assertEqual(hashlib.sha256(cover.read_bytes()).hexdigest(), ep["cover_sha256"], ep["id"])


if __name__ == "__main__":
    unittest.main()
