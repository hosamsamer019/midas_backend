#!/usr/bin/env python
"""
Test SQLite database directly
"""
import sqlite3
import os

def test_sqlite():
    """Test SQLite database directly"""
    db_path = 'db.sqlite3'

    if not os.path.exists(db_path):
        print(f"❌ Database file {db_path} does not exist")
        return False

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Test basic query
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ Basic query successful: {result}")

        # Check if tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [t[0] for t in tables]
        print(f"✅ Found {len(table_names)} tables: {table_names}")

        # Check users table
        if 'users' in table_names:
            cursor.execute("SELECT COUNT(*) FROM users")
            user_count = cursor.fetchone()[0]
            print(f"✅ Users table has {user_count} records")
        else:
            print("❌ Users table not found")

        # Check roles table
        if 'roles' in table_names:
            cursor.execute("SELECT COUNT(*) FROM roles")
            role_count = cursor.fetchone()[0]
            print(f"✅ Roles table has {role_count} records")
        else:
            print("❌ Roles table not found")

        conn.close()
        return True

    except Exception as e:
        print(f"❌ SQLite test failed: {e}")
        return False

if __name__ == '__main__':
    print("Testing SQLite Database...")
    print("=" * 50)
    success = test_sqlite()
    print("=" * 50)
    if success:
        print("🎉 SQLite database is accessible!")
    else:
        print("❌ SQLite database has issues")
