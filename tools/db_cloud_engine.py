"""
Zieork Bidirectional Database & Cloud CRM Engine.
Provides two-way synchronization for SQLite, PostgreSQL, Supabase,
and Notion/Airtable webhook pipelines.
"""
import os
import sqlite3
import requests
from typing import Dict, Any, List, Optional

DB_PATH = os.path.abspath("data/zieork_records.db")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

class DBCloudEngine:
    def __init__(self):
        self.db_path = DB_PATH
        self._init_sqlite()

    def _init_sqlite(self):
        """Ensure core CRM tables exist."""
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS crm_leads (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    entity TEXT,
                    email TEXT,
                    phone TEXT,
                    source_url TEXT,
                    platform TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS custom_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    collection TEXT,
                    data_json TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def sync_leads_to_db(self, leads: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Insert mined leads into active SQLite CRM table."""
        if not leads:
            return {"inserted": 0, "message": "No leads to insert."}

        count = 0
        with sqlite3.connect(self.db_path) as conn:
            c = conn.cursor()
            for lead in leads:
                c.execute("""
                    INSERT INTO crm_leads (name, entity, email, phone, source_url, platform)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    lead.get("name", "Unknown Contact"),
                    lead.get("entity", ""),
                    lead.get("email", ""),
                    lead.get("phone", ""),
                    lead.get("source_url", ""),
                    lead.get("platform", "web")
                ))
                count += 1
            conn.commit()

        return {
            "success": True,
            "inserted_count": count,
            "database": "data/zieork_records.db",
            "table": "crm_leads"
        }

    def query_leads(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieve recent synchronized leads from local CRM database."""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            c = conn.cursor()
            rows = c.execute("SELECT * FROM crm_leads ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
            return [dict(r) for r in rows]

    def push_to_webhook(self, webhook_url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatch payload to external Notion / Zapier / Slack / Make webhook."""
        try:
            resp = requests.post(webhook_url, json=payload, timeout=10)
            return {
                "success": resp.status_code in [200, 201, 202, 204],
                "status_code": resp.status_code,
                "response": resp.text[:200]
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

db_cloud_engine = DBCloudEngine()
