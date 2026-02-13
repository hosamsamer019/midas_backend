#!/usr/bin/env python
"""
Debug script to check admin user and test authentication
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.contrib.auth import authenticate
from users.models import User, Role

def check_admin_user():
    print("=== Checking Admin User ===")

    # Check if admin user exists
    admin = User.objects.filter(email='admin@test.com').first()
    if not admin:
        print("❌ Admin user does not exist")
        print("Total users in database:", User.objects.count())

        # List all users
        print("\nAll users in database:")
        for user in User.objects.all():
            print(f"  - {user.email} ({user.status})")

        return False

    print("✅ Admin user found:")
    print(f"  Email: {admin.email}")
    print(f"  Full Name: {admin.full_name}")
    print(f"  Status: {admin.status}")
    print(f"  Is Active: {admin.is_active}")
    print(f"  Failed Attempts: {admin.failed_attempts}")
    print(f"  Lock Until: {admin.lock_until}")
    print(f"  Role: {admin.role_id.role_name if admin.role_id else 'None'}")
    print(f"  Is Verified: {admin.is_verified}")
    print(f"  2FA Enabled: {admin.two_factor_enabled}")

    return True

def test_authentication():
    print("\n=== Testing Authentication ===")

    # Test authentication
    user = authenticate(username='admin@test.com', password='admin123')
    if user:
        print("✅ Authentication successful!")
        print(f"  User: {user.email}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Role: {user.role_id.role_name if user.role_id else 'None'}")
    else:
        print("❌ Authentication failed")

        # Check if user is locked
        admin = User.objects.filter(email='admin@test.com').first()
        if admin and admin.is_locked():
            print("  Reason: Account is locked")
        elif admin and not admin.is_active:
            print("  Reason: Account is not active")
        elif admin and admin.status != 'Active':
            print(f"  Reason: Account status is '{admin.status}'")
        else:
            print("  Reason: Invalid password or other issue")

def check_roles():
    print("\n=== Checking Roles ===")

    roles = Role.objects.all()
    print(f"Total roles: {roles.count()}")
    for role in roles:
        print(f"  - {role.role_name}: {role.description}")

def main():
    try:
        check_admin_user()
        test_authentication()
        check_roles()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
