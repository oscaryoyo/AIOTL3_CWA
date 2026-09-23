"""
Database Viewer Utility Script
Run `python view_db.py` in your terminal to inspect the contents of data.db.
"""

import sqlite3
import pandas as pd
import os

import sys

# Ensure UTF-8 stdout on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")

def main():
    if not os.path.exists(DB_PATH):
        print(f"Database file '{DB_PATH}' does not exist yet. Please run `python fetch_data.py` first.")
        return

    conn = sqlite3.connect(DB_PATH)
    
    # Get table list
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall() if not row[0].startswith("sqlite_")]
    
    print("=" * 60)
    print(f"SQLite Database: {os.path.abspath(DB_PATH)}")
    print(f"Tables found: {tables}")
    print("=" * 60)

    for table in tables:
        print(f"\nTable: [{table}]")
        df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
        if df.empty:
            print("  (Table is empty)")
        else:
            print(df.to_string(index=False))
            print("-" * 60)
            print(f"Total rows: {len(df)}")
    
    conn.close()

if __name__ == "__main__":
    main()

