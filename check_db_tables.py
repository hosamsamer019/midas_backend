#!/usr/bin/env python
"""
Check database tables and structure
"""
import sqlite3
import os

def check_tables():
    """Check database tables and their structure"""
    db_path = 'db.sqlite3'

    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("Database Tables:")
    print("=" * 50)

    for table in tables:
        table_name = table[0]
        print(f"\n📋 Table: {table_name}")

        # Get table structure
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()

        print("Columns:")
        for col in columns:
            col_id, col_name, col_type, not_null, default, pk = col
            print(f"  - {col_name} ({col_type}) {'PRIMARY KEY' if pk else ''} {'NOT NULL' if not_null else ''}")

        # Get row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"Records: {count}")
        except:
            print("Records: Unable to count")

    conn.close()

if __name__ == '__main__':
    check_tables()
