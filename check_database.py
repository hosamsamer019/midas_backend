#!/usr/bin/env python
"""
Database diagnostic script to check tables, migrations, and data
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection
from django.core.management import call_command
from users.models import User, Role
from audit.models import AuditLog

def check_database_file():
    """Check if database file exists"""
    db_path = 'db.sqlite3'
    exists = os.path.exists(db_path)
    print(f"Database file exists: {exists}")
    if exists:
        size = os.path.getsize(db_path)
        print(f"Database file size: {size} bytes")
    return exists

def check_tables():
    """Check all required tables"""
    required_tables = [
        'users', 'roles', 'permissions', 'role_permissions',
        'admin_email_control', 'audit_auditlog'
    ]

    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    existing_tables = [row[0] for row in cursor.fetchall()]

    print(f"Existing tables: {existing_tables}")

    missing_tables = []
    for table in required_tables:
        if table not in existing_tables:
            missing_tables.append(table)

    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    else:
        print("✅ All required tables exist")
        return True

def check_migrations():
    """Check migration status"""
    print("Checking migration status...")
    try:
        from django.core.management import execute_from_command_line
        # This will show migration status
        execute_from_command_line(['manage.py', 'showmigrations'])
    except Exception as e:
        print(f"Error checking migrations: {e}")

def check_users():
    """Check if users exist"""
    try:
        user_count = User.objects.count()
        print(f"Total users in database: {user_count}")

        if user_count > 0:
            users = User.objects.all()
            for user in users:
                print(f"  - {user.email} ({user.role_id.role_name if user.role_id else 'No role'})")
            return True
        else:
            print("❌ No users found in database")
            return False
    except Exception as e:
        print(f"❌ Error checking users: {e}")
        return False

def check_roles():
    """Check if roles exist"""
    try:
        role_count = Role.objects.count()
        print(f"Total roles in database: {role_count}")

        if role_count > 0:
            roles = Role.objects.all()
            for role in roles:
                print(f"  - {role.role_name}")
            return True
        else:
            print("❌ No roles found in database")
            return False
    except Exception as e:
        print(f"❌ Error checking roles: {e}")
        return False

def run_migrations():
    """Run pending migrations"""
    print("Running migrations...")
    try:
        call_command('migrate', verbosity=2)
        print("✅ Migrations completed")
        return True
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        return False

def create_test_data():
    """Create test users and roles"""
    print("Creating test data...")
    try:
        from setup_test_users import create_test_users
        create_test_users()
        print("✅ Test data created")
        return True
    except Exception as e:
        print(f"❌ Failed to create test data: {e}")
        return False

def main():
    print("=" * 60)
    print("DATABASE DIAGNOSTIC TOOL")
    print("=" * 60)

    # Check database file
    db_exists = check_database_file()
    print()

    if not db_exists:
        print("Database file does not exist. Running migrations to create it...")
        run_migrations()
        print()

    # Check tables
    tables_ok = check_tables()
    print()

    # Check migrations
    check_migrations()
    print()

    # If tables are missing, run migrations
    if not tables_ok:
        print("Tables missing. Running migrations...")
        run_migrations()
        print()
        tables_ok = check_tables()
        print()

    # Check roles
    roles_ok = check_roles()
    print()

    # Check users
    users_ok = check_users()
    print()

    # If no users, create test data
    if not users_ok:
        print("No users found. Creating test data...")
        create_test_data()
        print()
        users_ok = check_users()
        print()

    # Summary
    print("=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    print(f"Database file: {'✅' if db_exists else '❌'}")
    print(f"Tables: {'✅' if tables_ok else '❌'}")
    print(f"Roles: {'✅' if roles_ok else '❌'}")
    print(f"Users: {'✅' if users_ok else '❌'}")

    all_ok = db_exists and tables_ok and roles_ok and users_ok
    print(f"\nOverall status: {'✅ READY' if all_ok else '❌ NEEDS FIXING'}")

    return all_ok

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
