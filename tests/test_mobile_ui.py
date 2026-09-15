"""Automated verification for Modern Mobile ChatGPT Web App (Dark Mode & 1-Tap Copy Code)."""
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath("."))
from app import app

class TestMobileChatGPTUI(unittest.TestCase):
    """Test suite verifying mobile web app responsiveness, PWA assets, and 1-tap copy code."""

    def setUp(self):
        self.client = app.test_client()

    def test_mobile_index_html_served(self):
        """Verify GET / returns mobile ChatGPT interface with dark theme and meta tags."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Mobile ChatGPT Title & Brand
        self.assertIn("Zieork Prime — Mobile AI", html)
        self.assertIn("viewport-fit=cover", html)
        self.assertIn("manifest.json", html)
        self.assertIn("mobile.css", html)
        self.assertIn("mobile.js", html)

        # Creator Attribution in Mobile UI
        self.assertIn("Mohit Dwivedi", html)
        self.assertIn("https://mohitdwivedi.in", html)
        self.assertIn("https://hackortech.in", html)
        self.assertIn("https://github.com/dwivedi-mohit", html)

        # Core Mobile UI Elements
        self.assertIn('id="chat-container"', html)
        self.assertIn('id="chat-textarea"', html)
        self.assertIn('id="send-btn"', html)
        self.assertIn('id="mic-btn"', html)
        self.assertIn('id="mobile-drawer"', html)

    def test_mobile_css_served(self):
        """Verify static/mobile.css exists and includes dark theme & 1-tap copy code styles."""
        res = self.client.get("/static/mobile.css")
        self.assertEqual(res.status_code, 200)
        css = res.data.decode("utf-8")
        self.assertIn("--bg-primary: #212121", css)
        self.assertIn(".copy-code-btn", css)
        self.assertIn(".code-block-container", css)
        self.assertIn("--accent-emerald: #10a37f", css)

    def test_mobile_js_served(self):
        """Verify static/mobile.js exists and implements 1-tap copy code and SSE streaming."""
        res = self.client.get("/static/mobile.js")
        self.assertEqual(res.status_code, 200)
        js = res.data.decode("utf-8")
        self.assertIn("window.copyCodeBlock", js)
        self.assertIn("navigator.clipboard.writeText", js)
        self.assertIn("/v1/chat/completions", js)
        self.assertIn("parseMarkdown", js)

    def test_pwa_manifest_served(self):
        """Verify static/manifest.json is valid and installable."""
        res = self.client.get("/static/manifest.json")
        self.assertEqual(res.status_code, 200)
        data = res.json
        self.assertEqual(data.get("name"), "Zieork Prime")
        self.assertEqual(data.get("display"), "standalone")
        self.assertEqual(data.get("theme_color"), "#212121")

if __name__ == "__main__":
    unittest.main()
