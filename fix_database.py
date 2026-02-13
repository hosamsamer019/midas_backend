#!/usr/bin/env python
"""
Database fix script - recreate database and setup properly
"""
import os
import sys
import django
import shutil

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.core.management import call_command

def main():
    print("🔧 FIXING DATABASE ISSUES")
    print("=" * 50)

    # Step 1: Remove old database if exists
    db_path = 'db.sqlite3'
    if os.path.exists(db_path):
        print("Removing old database file...")
        os.remove(db_path)
        print("✅ Old database removed")

    # Step 2: Run migrations
    print("Running migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

    # Step 3: Create test users
    print("Creating test users...")
    try:
        from setup_test_users import create_test_users
        create_test_users()
        print("✅ Test users created")
    except Exception as e:
        print(f"❌ Failed to create test users: {e}")
        return False

    # Step 4: Verify setup
    print("Verifying setup...")
    try:
        from django.db import connection
        from users.models import User, Role

        # Check tables
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = ['users', 'roles', 'permissions', 'role_permissions', 'admin_email_control', 'audit_auditlog']
        missing = [t for t in required_tables if t not in tables]
        if missing:
            print(f"❌ Missing tables: {missing}")
            return False

        # Check users
        user_count = User.objects.count()
        if user_count == 0:
            print("❌ No users created")
            return False

        # Check roles
        role_count = Role.objects.count()
        if role_count == 0:
            print("❌ No roles created")
            return False

        print(f"✅ Database ready: {user_count} users, {role_count} roles, {len(tables)} tables")

    except Exception as e:
        print(f"❌ Verification failed: {e}")
        return False

    print("\n🎉 DATABASE FIXED SUCCESSFULLY!")
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
