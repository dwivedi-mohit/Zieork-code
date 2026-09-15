"""Zieork Persistent Long-Term Memory Engine (SQLite-Backed)."""
import os
import sqlite3
import time
import re
from typing import List, Dict, Any, Optional

DB_DIR = os.path.abspath("data")
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, "zieork_memory.db")

class MemoryStore:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_conn(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    category TEXT NOT NULL,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_memory(self, key: str, value: str, category: str = "preference") -> Dict[str, Any]:
        """Insert or update a persistent fact."""
        clean_key = key.strip().lower()
        clean_val = value.strip()
        now = time.strftime("%Y-%m-%d %H:%M:%S")

        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO memories (category, key, value, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(key) DO UPDATE SET
                    value = excluded.value,
                    category = excluded.category,
                    updated_at = excluded.updated_at
            """, (category, clean_key, clean_val, now, now))
            conn.commit()

        return {
            "key": clean_key,
            "value": clean_val,
            "category": category,
            "updated_at": now
        }

    def get_all_memories(self) -> List[Dict[str, Any]]:
        """Retrieve all active memories."""
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, category, key, value, updated_at FROM memories ORDER BY id ASC")
            rows = cursor.fetchall()
            return [
                {"id": r[0], "category": r[1], "key": r[2], "value": r[3], "updated_at": r[4]}
                for r in rows
            ]

    def search_memories(self, query: str) -> List[Dict[str, Any]]:
        """Search memory for keywords."""
        words = query.lower().split()
        all_m = self.get_all_memories()
        matched = []
        for m in all_m:
            combined = f"{m['key']} {m['value']} {m['category']}".lower()
            if any(w in combined for w in words if len(w) > 2):
                matched.append(m)
        return matched

    def delete_memory(self, key: str) -> bool:
        """Remove a memory by key."""
        clean_key = key.strip().lower()
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM memories WHERE key = ?", (clean_key,))
            conn.commit()
            return cursor.rowcount > 0

    def clear_all(self):
        with self._get_conn() as conn:
            conn.cursor().execute("DELETE FROM memories")
            conn.commit()

    def extract_and_save_facts(self, user_text: str) -> Optional[Dict[str, Any]]:
        """
        Analyze dialogue and automatically extract persistent facts.
        Matches patterns like:
        - "remember that X is Y"
        - "my project is X"
        - "my company is X"
        - "my stack is X"
        - "i prefer X"
        """
        text = user_text.strip()
        t_lower = text.lower()

        # 1. "remember that [key] is [value]" or "remember [key]: [value]"
        rem_match = re.search(r'\bremember\s+(?:that\s+)?([^:=]+?)(\s+is|\s*[:=])\s+(.+)', text, re.I)
        if rem_match:
            k = rem_match.group(1).strip()
            v = rem_match.group(3).strip().rstrip(".")
            return self.save_memory(k, v, category="user_fact")

        # 2. "my [key] is [value]"
        my_match = re.search(r'\bmy\s+(name|startup|project|company|tech stack|stack|database|language|framework|role|goal)\s+(?:is|=|:)\s+(.+)', text, re.I)
        if my_match:
            k = my_match.group(1).strip()
            v = my_match.group(2).strip().rstrip(".")
            return self.save_memory(f"user_{k}", v, category="profile")

        # 3. "i prefer [value]"
        pref_match = re.search(r'\bi\s+(?:always\s+)?prefer\s+([^.,]+)', text, re.I)
        if pref_match:
            v = pref_match.group(1).strip()
            return self.save_memory("preferred_tech", v, category="preference")

        return None

    def get_memory_context(self) -> str:
        """Format stored memories into a clean string for system prompt injection."""
        memories = self.get_all_memories()
        if not memories:
            return ""

        lines = ["ZIEORK LONG-TERM PERSISTENT MEMORY (User Profile & Facts):"]
        for m in memories:
            lines.append(f"• {m['key'].title()}: {m['value']} ({m['category']})")
        return "\n".join(lines)

memory_store = MemoryStore()
