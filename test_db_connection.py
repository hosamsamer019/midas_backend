#!/usr/bin/env python
"""
Test database connection and basic operations
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection
from users.models import User, Role, Permission

def test_database_connection():
    """Test basic database connectivity"""
    print("🔍 Testing Database Connection...")
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_models():
    """Test if models can be accessed"""
    print("\n🔍 Testing Models...")
    try:
        # Test User model
        user_count = User.objects.count()
        print(f"✅ User model accessible: {user_count} users")

        # Test Role model
        role_count = Role.objects.count()
        print(f"✅ Role model accessible: {role_count} roles")

        # Test Permission model
        perm_count = Permission.objects.count()
        print(f"✅ Permission model accessible: {perm_count} permissions")

        return True
    except Exception as e:
        print(f"❌ Model access failed: {e}")
        return False

def test_user_creation():
    """Test creating a test user"""
    print("\n🔍 Testing User Creation...")
    try:
        # Check if admin user exists
        admin_user = User.objects.filter(email='admin@test.com').first()
        if admin_user:
            print("✅ Admin user exists")
            return True
        else:
            print("❌ Admin user not found")
            return False
    except Exception as e:
        print(f"❌ User creation test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Testing Database and Models...")
    print("=" * 50)

    tests = [
        test_database_connection,
        test_models,
        test_user_creation
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 50)
    passed = sum(results)
    total = len(results)

    if passed == total:
        print("🎉 ALL TESTS PASSED - Database is working!")
        return 0
    else:
        print(f"❌ {total - passed} out of {total} tests failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())
