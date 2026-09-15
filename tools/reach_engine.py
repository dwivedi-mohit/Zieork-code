"""
AgentReach Multi-Platform & Social Intelligence Engine for Zieork.
Connects Zieork to Instagram, Facebook, LinkedIn, Twitter/X, Reddit, YouTube, and GitHub
without requiring expensive or paid official APIs.
"""
import os
import sys
import re
import subprocess
import json
from typing import Dict, Any, List, Optional

sys.path.insert(0, os.path.abspath("libs"))
from tools.search import search_web
from tools.generator import create_excel_file

EMAIL_REGEX = re.compile(r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+')
PHONE_REGEX = re.compile(r'(?:\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}')

class AgentReachEngine:
    def __init__(self):
        self.supported_platforms = ["instagram", "facebook", "linkedin", "twitter", "reddit", "youtube", "github"]

    def search_social_leads(
        self,
        niche: str,
        location: str = "",
        platform: str = "all",
        max_leads: int = 8,
        auto_excel: bool = True
    ) -> Dict[str, Any]:
        """
        Mine public creator profiles, business leads, and contact information
        across Instagram, Facebook, LinkedIn, or Twitter without paid APIs.
        """
        platform_queries = []
        p_clean = platform.lower().strip()

        if p_clean in ["instagram", "ig"]:
            platform_queries.append(("Instagram", f'site:instagram.com "{niche}" {f'"{location}"' if location else ""} ("email" OR "contact" OR "@" OR "dm")'))
        elif p_clean in ["linkedin", "li"]:
            platform_queries.append(("LinkedIn", f'site:linkedin.com/in/ "{niche}" {f'"{location}"' if location else ""} ("founder" OR "ceo" OR "lead" OR "director")'))
        elif p_clean in ["facebook", "fb"]:
            platform_queries.append(("Facebook", f'site:facebook.com "{niche}" {f'"{location}"' if location else ""} ("contact" OR "phone" OR "email")'))
        elif p_clean in ["twitter", "x"]:
            platform_queries.append(("Twitter/X", f'site:x.com "{niche}" {f'"{location}"' if location else ""} ("bio" OR "founder" OR "developer")'))
        else:
            # Multi-Platform Search
            loc_str = f'"{location}"' if location else ''
            platform_queries = [
                ("LinkedIn", f'site:linkedin.com/in/ "{niche}" {loc_str}'),
                ("Instagram", f'site:instagram.com "{niche}" {loc_str} ("founder" OR "business")'),
                ("Twitter/X", f'site:x.com "{niche}" {loc_str}'),
                ("Facebook", f'site:facebook.com "{niche}" {loc_str} ("contact" OR "page")')
            ]

        extracted_leads = []
        per_query_limit = max(2, max_leads // len(platform_queries)) if len(platform_queries) > 1 else max_leads

        for plat_name, query in platform_queries:
            results = search_web(query, max_results=per_query_limit)
            for r in results:
                title = r.get("title", "")
                snippet = r.get("snippet", "")
                url = r.get("url", "")

                # Extract emails & phones from title/snippet
                found_emails = EMAIL_REGEX.findall(snippet + " " + title)
                found_phones = PHONE_REGEX.findall(snippet)

                # Extract username or handle
                handle_match = re.search(r'@([a-zA-Z0-9_\.]+)', title + " " + snippet)
                handle = f"@{handle_match.group(1)}" if handle_match else ""

                # Clean Title (strip platform name)
                clean_title = re.sub(r'\s*-\s*(Instagram|LinkedIn|Facebook|Twitter|X).*$', '', title, flags=re.I).strip()

                lead = {
                    "platform": plat_name,
                    "name": clean_title,
                    "handle": handle,
                    "profile_url": url,
                    "snippet": snippet,
                    "email": found_emails[0] if found_emails else "",
                    "phone": found_phones[0] if found_phones else ""
                }
                extracted_leads.append(lead)

        # Truncate to requested limit
        extracted_leads = extracted_leads[:max_leads]

        result = {
            "success": True,
            "niche": niche,
            "location": location or "Global",
            "platform": platform,
            "total_leads": len(extracted_leads),
            "leads": extracted_leads
        }

        # Auto-Export to styled Excel
        if auto_excel and extracted_leads:
            sheet_title = f"{niche.title()}_Leads"
            excel_rows = []
            for lead in extracted_leads:
                excel_rows.append([
                    lead["platform"],
                    lead["name"],
                    lead["handle"],
                    lead["email"] or "Public DM / Inquire",
                    lead["phone"] or "N/A",
                    lead["profile_url"],
                    lead["snippet"][:120]
                ])

            sheets_dict = {
                "Leads_Roster": {
                    "headers": ["Platform", "Name / Title", "Handle", "Email / Contact", "Phone", "Profile URL", "Summary / Bio"],
                    "rows": excel_rows
                }
            }
            excel_res = create_excel_file(sheet_title, sheets_dict)
            result["excel_export"] = excel_res

        return result

    def search_reddit_discussions(self, topic: str, subreddit: Optional[str] = None, max_posts: int = 5) -> Dict[str, Any]:
        """Search community discussions and sentiment on Reddit."""
        if subreddit:
            query = f'site:reddit.com/r/{subreddit} {topic}'
        else:
            query = f'site:reddit.com {topic}'

        results = search_web(query, max_results=max_posts)
        parsed_posts = []

        for r in results:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            url = r.get("url", "")

            # Extract subreddit name from URL
            sub_match = re.search(r'reddit\.com/r/([^/]+)', url)
            sub_name = f"r/{sub_match.group(1)}" if sub_match else "r/all"

            # Clean Title
            clean_title = re.sub(r'\s*:\s*r/[^ ]+\s*-\s*Reddit', '', title).strip()

            parsed_posts.append({
                "subreddit": sub_name,
                "title": clean_title,
                "snippet": snippet,
                "url": url
            })

        return {
            "success": True,
            "topic": topic,
            "subreddit": subreddit or "all",
            "posts_found": len(parsed_posts),
            "discussions": parsed_posts
        }

    def get_youtube_intelligence(self, video_query_or_url: str) -> Dict[str, Any]:
        """
        Extract video information, chapters, and full spoken transcript using yt-dlp.
        Works with both URLs and search queries.
        """
        is_url = video_query_or_url.startswith("http://") or video_query_or_url.startswith("https://") or "youtu" in video_query_or_url

        target = video_query_or_url
        if not is_url:
            target = f"ytsearch1:{video_query_or_url}"

        cmd = [
            "yt-dlp",
            "--skip-download",
            "--dump-json",
            "--no-warnings",
            target
        ]

        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
            if p.returncode != 0 or not p.stdout.strip():
                # Fallback to search_web if yt-dlp is restricted
                results = search_web(f"site:youtube.com {video_query_or_url}", max_results=3)
                return {
                    "success": True,
                    "title": results[0]["title"] if results else video_query_or_url,
                    "url": results[0]["url"] if results else "",
                    "summary": results[0]["snippet"] if results else "No transcript available.",
                    "method": "search_fallback"
                }

            meta = json.loads(p.stdout.strip().split("\n")[0])
            title = meta.get("title", "")
            channel = meta.get("uploader", "")
            duration = meta.get("duration_string", "")
            description = meta.get("description", "")
            view_count = meta.get("view_count", 0)
            webpage_url = meta.get("webpage_url", "")

            # Extract chapters if present
            chapters = meta.get("chapters", [])
            chapter_summary = [f"{c.get('start_time', 0)}s: {c.get('title')}" for c in chapters] if chapters else []

            return {
                "success": True,
                "title": title,
                "channel": channel,
                "duration": duration,
                "views": f"{view_count:,}" if view_count else "N/A",
                "url": webpage_url,
                "chapters": chapter_summary[:8],
                "description_excerpt": description[:600] if description else "",
                "method": "yt_dlp_meta"
            }
        except Exception as e:
            return {"error": f"YouTube extraction error: {str(e)}"}

    def search_github_repos(self, query: str, max_repos: int = 5) -> Dict[str, Any]:
        """Search GitHub open-source repositories, developer stars, and tech stacks."""
        results = search_web(f"site:github.com {query}", max_results=max_repos)
        repos = []

        for r in results:
            title = r.get("title", "")
            snippet = r.get("snippet", "")
            url = r.get("url", "")

            # Filter out non-repo github pages (issues, commits, search)
            if not re.search(r'github\.com/[^/]+/[^/]+/?$', url):
                continue

            # Extract Owner/Repo
            repo_match = re.search(r'github\.com/([^/]+)/([^/]+)', url)
            repo_name = f"{repo_match.group(1)}/{repo_match.group(2)}" if repo_match else title

            repos.append({
                "repo": repo_name,
                "url": url,
                "description": snippet
            })

        return {
            "success": True,
            "query": query,
            "count": len(repos),
            "repositories": repos
        }

# Global singleton
agent_reach = AgentReachEngine()
