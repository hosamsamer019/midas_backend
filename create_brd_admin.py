#!/usr/bin/env python
"""
Script to create a BRD-compliant admin user for testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role

def main():
    print("🚀 Creating BRD-compliant Admin User")

    # Get or create admin role
    admin_role, created = Role.objects.get_or_create(
        role_name='Administrator',
        defaults={'description': 'System Administrator with full access'}
    )

    if created:
        print("✅ Created Administrator role")
    else:
        print("✅ Administrator role already exists")

    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin@hospital.com',
        defaults={
            'full_name': 'System Administrator',
            'role': admin_role,
            'status': 'Active',
            'is_active': True,
            'is_staff': True,
        }
    )

    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✅ Created admin user: admin@hospital.com / admin123")
    else:
        print("✅ Admin user already exists")

    # Test permissions
    print(f"🔐 Admin user permissions: {list(admin_user.get_all_permissions())}")
    print(f"👤 Admin role: {admin_user.role.role_name if admin_user.role else 'None'}")

    print("\n🎉 BRD Admin User Setup Complete!")
    print("Login credentials: admin@hospital.com / admin123")

if __name__ == '__main__':
    main()
