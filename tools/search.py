"""Live Web Search and Content Scraper (100% Free & Unlimited)."""
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

def search_web(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search the live web using DuckDuckGo HTML without any API keys.
    Returns a list of dictionaries with title, snippet, and link.
    """
    url = "https://html.duckduckgo.com/html/"
    data = {"q": query}

    try:
        resp = requests.post(url, data=data, headers=HEADERS, timeout=12)
        if resp.status_code != 200:
            return []

        soup = BeautifulSoup(resp.text, "html.parser")
        results = []

        # Find search result links
        result_elements = soup.find_all("div", class_=re.compile(r"result\s+results_links"))
        if not result_elements:
            result_elements = soup.find_all("div", class_="result")

        for el in result_elements:
            title_tag = el.find("a", class_="result__a")
            snippet_tag = el.find("a", class_="result__snippet")

            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
            raw_url = title_tag.get("href", "")

            # Decode DuckDuckGo redirect url
            if "/l/?uddg=" in raw_url:
                parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_url).query)
                clean_url = parsed.get("uddg", [raw_url])[0]
            else:
                clean_url = raw_url

            if title and clean_url.startswith("http"):
                results.append({
                    "title": title,
                    "snippet": snippet,
                    "url": clean_url
                })

            if len(results) >= max_results:
                break

        if results:
            return results

        # Fallback to DuckDuckGo Lite if HTML endpoint returned 0
        resp_lite = requests.post("https://lite.duckduckgo.com/lite/", data=data, headers=HEADERS, timeout=10)
        if resp_lite.status_code == 200:
            soup_lite = BeautifulSoup(resp_lite.text, "html.parser")
            for link in soup_lite.find_all("a", class_="result-link"):
                title = link.get_text(strip=True)
                href = link.get("href", "")
                # Find preceding or adjacent snippet in table
                tr = link.find_parent("tr")
                snippet = ""
                if tr:
                    next_tr = tr.find_next_sibling("tr")
                    if next_tr:
                        snippet_td = next_tr.find("td", class_="result-snippet")
                        if snippet_td:
                            snippet = snippet_td.get_text(strip=True)

                if title and href.startswith("http"):
                    results.append({
                        "title": title,
                        "snippet": snippet,
                        "url": href
                    })
                if len(results) >= max_results:
                    break

        return results
    except Exception as e:
        print(f"Web search error: {e}")
        return []

def fetch_page_text(url: str, max_chars: int = 2500) -> str:
    """Fetch and clean article text from a webpage URL."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code != 200:
            return ""

        soup = BeautifulSoup(resp.text, "html.parser")

        # Remove scripts, styles, navigations
        for tag in soup(["script", "style", "nav", "footer", "header", "noscript", "aside"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)
        # Collapse extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:max_chars]
    except Exception as e:
        print(f"Error fetching page {url}: {e}")
        return ""

def deep_research(query: str, max_sources: int = 3) -> Dict[str, Any]:
    """
    Execute deep research across multiple authoritative web sources and scrape full contents.
    """
    clean_q = query.strip()
    primary_results = search_web(clean_q, max_results=max_sources + 3)
    sources = []
    seen_domains = set()

    for r in primary_results:
        domain = urllib.parse.urlparse(r["url"]).netloc
        if domain in seen_domains:
            continue
        seen_domains.add(domain)

        page_body = fetch_page_text(r["url"], max_chars=1800)
        sources.append({
            "title": r["title"],
            "url": r["url"],
            "snippet": r["snippet"],
            "content": page_body if page_body else r["snippet"]
        })
        if len(sources) >= max_sources:
            break

    return {
        "query": clean_q,
        "sources": sources
    }
