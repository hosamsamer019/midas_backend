#!/usr/bin/env python
"""
Fix admin user to have correct email and password
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role

def fix_admin_user():
    print("Fixing admin user...")

    # Check if admin@test.com exists
    correct_admin = User.objects.filter(email='admin@test.com').first()
    if correct_admin:
        print("✅ Admin user with correct email already exists")
        # Ensure password is set correctly
        correct_admin.set_password('admin123')
        correct_admin.save()
        print("✅ Password updated for admin@test.com")
        return

    # Check if there's a user with email 'admin'
    wrong_admin = User.objects.filter(email='admin').first()
    if wrong_admin:
        print("Found user with email 'admin', updating to 'admin@test.com'...")
        wrong_admin.email = 'admin@test.com'
        wrong_admin.set_password('admin123')
        wrong_admin.save()
        print("✅ Updated user email to admin@test.com and set password")
        return

    # If no admin user exists, create one
    print("No admin user found, creating new admin user...")
    admin_role, created = Role.objects.get_or_create(
        role_name='Administrator',
        defaults={'description': 'System Administrator with full access'}
    )

    admin = User.objects.create_user(
        email='admin@test.com',
        full_name='System Administrator',
        password='admin123',
        role=admin_role
    )
    print("✅ Created new admin user: admin@test.com")

if __name__ == '__main__':
    fix_admin_user()
