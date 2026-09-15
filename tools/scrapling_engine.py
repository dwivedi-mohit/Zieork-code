"""
Scrapling Adaptive Stealth Scraper for Zieork.
Employs Scrapling's adaptive parser, regex lead mining (emails, phones, social profiles),
HTML table extraction, and automatic export to Excel.
"""
import os
import sys
import re
import urllib.request
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath("libs"))
from scrapling.parser import Adaptor
from tools.generator import create_excel_file

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}')

class ScraplingEngine:
    def __init__(self):
        self.user_agent = (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
        )

    def scrape_url(self, url: str, auto_excel: bool = False, excel_title: Optional[str] = None) -> Dict[str, Any]:
        """Fetch, adaptively parse, and extract leads and structured data from a URL."""
        import requests
        if not url.startswith("http://") and not url.startswith("https://"):
            url = f"https://{url}"

        headers = {
            "User-Agent": self.user_agent,
        }

        try:
            resp = requests.get(url, headers=headers, timeout=12, allow_redirects=True)
            if resp.status_code != 200:
                # Fallback to standard request
                resp = requests.get(url, timeout=12, allow_redirects=True)
            if resp.status_code != 200:
                return {"error": f"HTTP {resp.status_code} returned from {url}"}
            html = resp.text
            response_headers = dict(resp.headers)
            status_code = resp.status_code
        except Exception as e:
            return {"error": f"Failed to fetch {url}: {str(e)}"}

        res = self.parse_html(html, source_url=url, auto_excel=auto_excel, excel_title=excel_title)
        if isinstance(res, dict) and "error" not in res:
            res["status_code"] = status_code
            res["response_headers"] = response_headers
            res["server"] = response_headers.get("Server") or response_headers.get("server") or "Unknown"
            res["powered_by"] = response_headers.get("X-Powered-By") or response_headers.get("x-powered-by") or ""
        return res

    def parse_html(self, html: str, source_url: str = "raw_html", auto_excel: bool = False, excel_title: Optional[str] = None) -> Dict[str, Any]:
        """Parse HTML string with Scrapling Adaptor and mine leads/tables."""
        try:
            page = Adaptor(html)

            # Extract Title
            title_nodes = page.css("title::text")
            title = str(title_nodes[0]).strip() if title_nodes else "Web Page"

            # Extract Meta Tags
            meta_tags = {}
            for m in page.css("meta"):
                key = m.attrib.get("name") or m.attrib.get("property") or ""
                val = m.attrib.get("content") or ""
                if key and val:
                    meta_tags[key.lower().strip()] = val.strip()

            meta_desc = meta_tags.get("description") or meta_tags.get("og:description") or meta_tags.get("twitter:description") or ""
            keywords = meta_tags.get("keywords") or ""
            author = meta_tags.get("author") or meta_tags.get("creator") or meta_tags.get("publisher") or ""
            og_site_name = meta_tags.get("og:site_name") or ""
            og_title = meta_tags.get("og:title") or ""

            # Extract Headings
            h1_nodes = page.css("h1::text")
            headings = [str(h).strip() for h in h1_nodes if str(h).strip()]

            # Extract Links & Social Handles
            social_links = {
                "linkedin": [],
                "twitter": [],
                "instagram": [],
                "facebook": [],
                "github": [],
                "youtube": []
            }
            all_links = []
            for a in page.css("a"):
                href = a.attrib.get("href", "")
                if href:
                    all_links.append(href)
                    h_low = href.lower()
                    for platform in social_links.keys():
                        if platform in h_low:
                            social_links[platform].append(href)

            # Deduplicate social links
            for k in social_links:
                social_links[k] = list(set(social_links[k]))

            # Regex Lead Mining from entire HTML text
            emails = list(set(EMAIL_REGEX.findall(html)))
            # Filter out obvious static assets from emails
            emails = [e for e in emails if not any(e.endswith(ext) for ext in [".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".css", ".js"])]

            phones = list(set([p.strip() for p in PHONE_REGEX.findall(html) if len(p.strip()) >= 10]))

            # Table Extraction
            tables_data = []
            for t_idx, table in enumerate(page.css("table")):
                headers = [str(th.text).strip() for th in table.css("th") if str(th.text).strip()]
                rows = []
                for tr in table.css("tr"):
                    cells = [str(td.text).strip() for td in tr.css("td")]
                    if cells:
                        rows.append(cells)
                if rows:
                    if not headers and rows:
                        headers = [f"Col_{i+1}" for i in range(len(rows[0]))]
                    tables_data.append({
                        "table_id": t_idx + 1,
                        "headers": headers,
                        "rows": rows[:100]
                    })

            # Text content excerpt
            text_blocks = [str(p.text).strip() for p in page.css("p") if str(p.text).strip()]
            main_text = "\n\n".join(text_blocks[:15])

            result = {
                "success": True,
                "url": source_url,
                "title": title,
                "meta_description": meta_desc,
                "keywords": keywords,
                "author": author,
                "og_site_name": og_site_name,
                "og_title": og_title,
                "meta_tags": meta_tags,
                "headings": headings[:5],
                "leads": {
                    "emails": emails[:20],
                    "phone_numbers": phones[:10],
                    "social_links": {k: v for k, v in social_links.items() if v}
                },
                "tables_count": len(tables_data),
                "tables": tables_data[:3],
                "content_preview": main_text[:1500]
            }

            # Optional Auto-Export to Excel if tables or leads exist
            if auto_excel and (tables_data or emails or any(social_links.values())):
                sheet_title = excel_title or title or "Scraped_Data"
                sheets_dict = {}

                # Sheet 1: Leads
                lead_rows = []
                max_items = max(len(emails), 1)
                for i in range(max_items):
                    em = emails[i] if i < len(emails) else ""
                    ph = phones[i] if i < len(phones) else ""
                    li = social_links["linkedin"][i] if i < len(social_links["linkedin"]) else ""
                    tw = social_links["twitter"][i] if i < len(social_links["twitter"]) else ""
                    lead_rows.append([title, source_url, em, ph, li, tw])

                sheets_dict["Extracted_Leads"] = {
                    "headers": ["Entity / Company", "Source URL", "Email", "Phone", "LinkedIn", "Twitter/X"],
                    "rows": lead_rows
                }

                # Sheet 2+: Any Tables
                for t in tables_data:
                    sheets_dict[f"Table_{t['table_id']}"] = {
                        "headers": t["headers"],
                        "rows": t["rows"]
                    }

                excel_res = create_excel_file(sheet_title, sheets_dict)
                result["excel_export"] = excel_res

            return result

        except Exception as e:
            return {"error": f"Scrapling Parsing Error: {str(e)}"}

# Global singleton
scrapling_engine = ScraplingEngine()
