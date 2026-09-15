"""
Interactive Data Analysis & In-Memory SQL Engine for Zieork.
Allows querying CSV, Excel, and JSON data with full SQL, computing statistics,
and auto-exporting transformed data to styled Excel workbooks.
"""
import os
import sys
import sqlite3
import pandas as pd
from typing import Dict, Any, Optional, List

sys.path.insert(0, os.path.abspath("libs"))
from tools.generator import create_excel_file

class DataEngine:
    def __init__(self):
        self.conn = sqlite3.connect(":memory:", check_same_thread=False)
        self.active_tables: Dict[str, pd.DataFrame] = {}

    def load_file(self, filepath: str, table_name: str = "dataset") -> Dict[str, Any]:
        """Load a CSV or Excel file into an in-memory SQLite table."""
        if not os.path.exists(filepath):
            return {"error": f"File not found: {filepath}"}

        ext = os.path.splitext(filepath)[1].lower()
        try:
            if ext == ".csv":
                df = pd.read_csv(filepath)
            elif ext in [".xlsx", ".xls"]:
                df = pd.read_excel(filepath)
            elif ext == ".json":
                df = pd.read_json(filepath)
            else:
                return {"error": f"Unsupported file extension: {ext}"}

            # Normalize column names for clean SQL
            df.columns = [str(c).strip().replace(" ", "_").replace("-", "_").lower() for c in df.columns]
            clean_table = table_name.strip().replace(" ", "_").lower()

            df.to_sql(clean_table, self.conn, if_exists="replace", index=False)
            self.active_tables[clean_table] = df

            stats = {
                "rows": int(df.shape[0]),
                "columns": list(df.columns),
                "column_count": int(df.shape[1]),
                "table_name": clean_table,
                "preview": df.head(5).to_dict(orient="records")
            }
            return {"success": True, "stats": stats}
        except Exception as e:
            return {"error": f"Failed to load dataset: {str(e)}"}

    def run_sql(self, sql_query: str) -> Dict[str, Any]:
        """Execute a SQL query against the in-memory SQLite database."""
        try:
            # Basic sanity check
            query_clean = sql_query.strip()
            df_res = pd.read_sql_query(query_clean, self.conn)
            
            headers = list(df_res.columns)
            rows = df_res.values.tolist()
            
            return {
                "success": True,
                "query": query_clean,
                "row_count": len(rows),
                "headers": headers,
                "rows": rows[:50],  # Return up to 50 rows for display
                "truncated": len(rows) > 50
            }
        except Exception as e:
            return {"error": f"SQL Execution Error: {str(e)}"}

    def export_sql_to_excel(self, sql_query: str, title: str = "SQL_Export") -> Dict[str, Any]:
        """Run SQL and export the resulting dataset directly to a styled Excel workbook."""
        res = self.run_sql(sql_query)
        if "error" in res:
            return res

        headers = res["headers"]
        rows = res["rows"]

        sheets_data = {
            "Query_Results": {
                "headers": headers,
                "rows": rows,
                "has_total": any(k in h.lower() for h in headers for k in ["price", "cost", "revenue", "amount", "total"])
            }
        }
        return create_excel_file(title, sheets_data)

    def get_summary(self, table_name: str) -> Dict[str, Any]:
        """Compute statistical summary for a loaded table."""
        if table_name not in self.active_tables:
            return {"error": f"Table '{table_name}' not loaded"}

        df = self.active_tables[table_name]
        num_summary = df.describe().to_dict() if not df.empty else {}
        null_counts = df.isnull().sum().to_dict()

        return {
            "table_name": table_name,
            "shape": df.shape,
            "numeric_summary": num_summary,
            "null_counts": null_counts
        }

# Global singleton instance
data_engine = DataEngine()
