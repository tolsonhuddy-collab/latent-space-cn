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
        self.assertGreaterEqual(len(episodes), 10)
        ids = [ep["id"] for ep in episodes]
        self.assertEqual(len(ids), len(set(ids)))

    def test_demo_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            build_site.build_site(mode="demo", out_dir=out)
            self.assertTrue((out / "index.html").exists())
            self.assertTrue((out / "style.css").exists())
            self.assertTrue((out / "app.js").exists())
            self.assertTrue((out / "feed.xml").exists())
            self.assertTrue((out / "latent-space-rss.opml").exists())
            self.assertTrue((out / "episodes" / "001-demo.html").exists())
            self.assertTrue((out / "episodes" / "002-demo.html").exists())
            html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("Latent Space 中文精读", html)
            self.assertIn("3 期节目 · 2 期已定稿", html)

    def test_published_build(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "dist"
            build_site.build_site(mode="published", out_dir=out)
            index_html = (out / "index.html").read_text(encoding="utf-8")
            self.assertIn("10 期节目 · 10 期已定稿", index_html)
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
            ):
                self.assertTrue((out / "episodes" / f"{ep_id}.html").exists())
            article_html = (out / "episodes" / "004-chai-discovery.html").read_text(encoding="utf-8")
            self.assertIn("通用蛋白质设计模型撑起了中立的新药研发软件层", article_html)


if __name__ == "__main__":
    unittest.main()
