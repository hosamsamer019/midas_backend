#!/usr/bin/env python
"""
Simple test script for BRD Authentication System
Tests basic functionality of the new authentication system
"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission
from audit.models import AuditLog

def test_roles_permissions():
    """Test that roles and permissions are properly set up"""
    print("🧪 Testing BRD Authentication System")
    print("=" * 50)

    # Test roles
    roles = Role.objects.all()
    print(f"📋 Found {roles.count()} roles:")
    for role in roles:
        print(f"  - {role.role_name}: {role.description}")

    # Test permissions
    permissions = Permission.objects.all()
    print(f"\n🔐 Found {permissions.count()} permissions:")
    for perm in permissions:
        print(f"  - {perm.permission_name}: {perm.description}")

    # Test role-permissions
    role_perms = RolePermission.objects.all()
    print(f"\n🔗 Found {role_perms.count()} role-permission relationships")

    return roles.count() > 0 and permissions.count() > 0

def test_user_creation():
    """Test user creation with the new system"""
    print("\n👤 Testing User Creation")

    # Get admin role
    try:
        admin_role = Role.objects.get(role_name='Administrator')
        print(f"✅ Found Administrator role: {admin_role.role_name}")
    except Role.DoesNotExist:
        print("❌ Administrator role not found")
        return False

    # Test user creation
    try:
        test_user = User.objects.create_user(
            email='test@example.com',
            full_name='Test User',
            password='testpass123',
            role=admin_role
        )
        print(f"✅ Created test user: {test_user.full_name} ({test_user.email})")
        print(f"   Role: {test_user.role.role_name}")
        print(f"   Status: {test_user.status}")

        # Clean up
        test_user.delete()
        print("✅ Test user cleaned up")

        return True
    except Exception as e:
        print(f"❌ User creation failed: {e}")
        return False

def test_permissions():
    """Test permission checking"""
    print("\n🔒 Testing Permission System")

    try:
        admin_role = Role.objects.get(role_name='Administrator')

        # Create a test user
        test_user = User.objects.create_user(
            email='permtest@example.com',
            full_name='Permission Test User',
            password='testpass123',
            role=admin_role
        )

        # Test permission checking
        has_view_dashboard = test_user.has_perm('view_dashboard')
        has_manage_users = test_user.has_perm('manage_users')
        has_nonexistent = test_user.has_perm('nonexistent_permission')

        print(f"✅ User has 'view_dashboard' permission: {has_view_dashboard}")
        print(f"✅ User has 'manage_users' permission: {has_manage_users}")
        print(f"✅ User does NOT have 'nonexistent_permission': {not has_nonexistent}")

        # Clean up
        test_user.delete()
        print("✅ Permission test user cleaned up")

        return has_view_dashboard and has_manage_users and not has_nonexistent

    except Exception as e:
        print(f"❌ Permission testing failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting BRD Authentication System Tests\n")

    success = True

    # Test 1: Roles and Permissions setup
    if not test_roles_permissions():
        success = False

    # Test 2: User creation
    if not test_user_creation():
        success = False

    # Test 3: Permission system
    if not test_permissions():
        success = False

    print("\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED! BRD Authentication System is working correctly.")
        print("\n📋 Next Steps:")
        print("1. Run: python manage.py createsuperuser --email admin@example.com --full_name 'System Administrator'")
        print("2. Start the server: python manage.py runserver")
        print("3. Test login at: http://localhost:8000/api/auth/login/")
        print("4. Access admin panel at: http://localhost:8000/admin/")
    else:
        print("❌ SOME TESTS FAILED. Please check the output above.")

    return success

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
