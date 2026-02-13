#!/usr/bin/env python
"""
Test admin authentication directly
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.contrib.auth import authenticate
from users.models import User, Role
from django.db import connection

def check_database():
    """Check database tables and data"""
    print("=== Database Check ===")

    with connection.cursor() as cursor:
        # Check if users table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        if cursor.fetchone():
            print("✅ Users table exists")
        else:
            print("❌ Users table does not exist")
            return

        # Check users count
        cursor.execute("SELECT COUNT(*) FROM users;")
        count = cursor.fetchone()[0]
        print(f"Total users in database: {count}")

        # Check admin user
        cursor.execute("SELECT user_id, full_name, email, pass_hash, role_id, status, is_active, is_staff, is_superuser FROM users WHERE email='admin@test.com';")
        admin_data = cursor.fetchone()
        if admin_data:
            print("✅ Admin user found in database:")
            print(f"  ID: {admin_data[0]}")
            print(f"  Name: {admin_data[1]}")
            print(f"  Email: {admin_data[2]}")
            print(f"  Password hash: {admin_data[3][:20]}...")
            print(f"  Role ID: {admin_data[4]}")
            print(f"  Status: {admin_data[5]}")
            print(f"  Is Active: {admin_data[6]}")
            print(f"  Is Staff: {admin_data[7]}")
            print(f"  Is Superuser: {admin_data[8]}")
        else:
            print("❌ Admin user not found in database")

def test_django_auth():
    """Test Django authentication"""
    print("\n=== Django Authentication Test ===")

    # Get user from database
    try:
        user = User.objects.get(email='admin@test.com')
        print("✅ User object retrieved from Django ORM")
        print(f"  Email: {user.email}")
        print(f"  Password hash: {user.password[:20]}...")
        print(f"  Is active: {user.is_active}")
        print(f"  Check password 'admin123': {user.check_password('admin123')}")

        # Test authenticate function
        auth_user = authenticate(username='admin@test.com', password='admin123')
        if auth_user:
            print("✅ Authentication successful!")
            print(f"  Authenticated user: {auth_user.email}")
        else:
            print("❌ Authentication failed")

            # Try with different username field
            auth_user2 = authenticate(email='admin@test.com', password='admin123')
            if auth_user2:
                print("✅ Authentication successful with email field!")
            else:
                print("❌ Authentication still failed")

    except User.DoesNotExist:
        print("❌ User does not exist in Django ORM")

def check_roles():
    """Check roles"""
    print("\n=== Roles Check ===")

    roles = Role.objects.all()
    print(f"Total roles: {roles.count()}")
    for role in roles:
        print(f"  - {role.role_name} (ID: {role.role_id})")

def main():
    try:
        check_database()
        test_django_auth()
        check_roles()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
