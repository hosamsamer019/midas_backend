#!/usr/bin/env python
"""
Check saved login passwords in the database
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User

def check_saved_passwords():
    """Check and display user passwords (hashed)"""
    print("Checking saved login passwords in database...")
    print("=" * 60)

    users = User.objects.all().order_by('email')

    if not users:
        print("❌ No users found in database!")
        print("Run setup_test_users.py first to create test users.")
        return

    print(f"Found {len(users)} users:")
    print("-" * 60)

    for user in users:
        print(f"Email: {user.email}")
        print(f"Full Name: {user.full_name}")
        print(f"Role: {user.role.role_name if user.role else 'None'}")
        print(f"Status: {user.status}")
        print(f"Password Hash: {user.password}")
        print(f"Is Verified: {user.is_verified}")
        print(f"Failed Attempts: {user.failed_attempts}")
        print(f"Account Locked: {user.is_locked()}")
        print(f"Last Login: {user.last_login}")
        print("-" * 40)

    print("\nTest Credentials (Plain Text):")
    print("=" * 40)
    print("admin@test.com / admin123 (Administrator)")
    print("doctor@test.com / doctor123 (Doctor)")
    print("lab@test.com / lab123 (Lab)")
    print("viewer@test.com / viewer123 (Viewer)")

if __name__ == '__main__':
    check_saved_passwords()
