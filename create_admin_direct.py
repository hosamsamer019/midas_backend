#!/usr/bin/env python
"""
Direct SQL script to create BRD-compliant admin user
"""
import os
import sys
import django
from django.contrib.auth.hashers import make_password

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection

def main():
    print("🚀 Creating BRD-compliant Admin User (Direct SQL)")

    # Get admin role ID
    with connection.cursor() as cursor:
        cursor.execute("SELECT role_id FROM roles WHERE role_name = 'Administrator'")
        admin_role = cursor.fetchone()

        if not admin_role:
            print("❌ Administrator role not found")
            return

        admin_role_id = admin_role[0]
        print(f"✅ Found Administrator role ID: {admin_role_id}")

        # Check if admin user already exists
        cursor.execute("SELECT user_id FROM users_user WHERE email = 'admin@hospital.com'")
        existing_user = cursor.fetchone()

        if existing_user:
            print("✅ Admin user already exists")
            return

        # Create admin user directly
        hashed_password = make_password('admin123')

        cursor.execute("""
            INSERT INTO users_user (
                full_name, email, password_hash, role_id, status,
                created_at, is_active, is_staff
            ) VALUES (?, ?, ?, ?, ?, datetime('now'), 1, 1)
        """, [
            'System Administrator',
            'admin@hospital.com',
            hashed_password,
            admin_role_id,
            'Active'
        ])

        print("✅ Created admin user: admin@hospital.com / admin123")

        # Log the creation
        cursor.execute("""
            INSERT INTO audit_log (user_id, action_type, timestamp, ip_address)
            VALUES (?, ?, datetime('now'), ?)
        """, [cursor.lastrowid, 'user_created', '127.0.0.1'])

        print("✅ Logged admin user creation")

    print("\n🎉 BRD Admin User Setup Complete!")
    print("Login credentials: admin@hospital.com / admin123")

if __name__ == '__main__':
    main()
