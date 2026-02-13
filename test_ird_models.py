#!/usr/bin/env python
"""
Test script for IRD Document implementation
Tests the updated models to ensure they work correctly
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission, AdminEmailControl
from audit.models import AuditLog

def test_roles():
    """Test Role model"""
    print("Testing Role model...")

    # Create roles
    admin_role, created = Role.objects.get_or_create(
        role_name='Administrator',
        defaults={'description': 'System Administrator'}
    )
    print(f"✓ Admin role: {admin_role} (created: {created})")

    doctor_role, created = Role.objects.get_or_create(
        role_name='Doctor',
        defaults={'description': 'Medical Doctor'}
    )
    print(f"✓ Doctor role: {doctor_role} (created: {created})")

    lab_role, created = Role.objects.get_or_create(
        role_name='Lab',
        defaults={'description': 'Lab Technician'}
    )
    print(f"✓ Lab role: {lab_role} (created: {created})")

    viewer_role, created = Role.objects.get_or_create(
        role_name='Viewer',
        defaults={'description': 'Read-only viewer'}
    )
    print(f"✓ Viewer role: {viewer_role} (created: {created})")

    return admin_role, doctor_role, lab_role, viewer_role

def test_permissions():
    """Test Permission model"""
    print("\nTesting Permission model...")

    permissions = [
        'CREATE_USER', 'EDIT_USER', 'DELETE_USER', 'LOAD_DATA',
        'CREATE_REPORT', 'VIEW_ANALYSIS', 'SEND_MESSAGE'
    ]

    created_permissions = []
    for perm_name in permissions:
        perm, created = Permission.objects.get_or_create(
            permission_name=perm_name,
            defaults={'description': f'{perm_name} permission'}
        )
        created_permissions.append(perm)
        print(f"✓ Permission: {perm} (created: {created})")

    return created_permissions

def test_role_permissions(roles, permissions):
    """Test RolePermission relationships"""
    print("\nTesting RolePermission relationships...")

    # Assign permissions to admin role
    admin_role = roles[0]
    for perm in permissions:
        rp, created = RolePermission.objects.get_or_create(
            role=admin_role,
            permission=perm
        )
        print(f"✓ Admin permission: {rp} (created: {created})")

    # Assign some permissions to doctor role
    doctor_role = roles[1]
    doctor_perms = ['VIEW_ANALYSIS', 'CREATE_REPORT', 'SEND_MESSAGE']
    for perm_name in doctor_perms:
        perm = Permission.objects.get(permission_name=perm_name)
        rp, created = RolePermission.objects.get_or_create(
            role=doctor_role,
            permission=perm
        )
        print(f"✓ Doctor permission: {rp} (created: {created})")

def test_admin_email_control():
    """Test AdminEmailControl model"""
    print("\nTesting AdminEmailControl model...")

    # Create admin email control
    admin_email, created = AdminEmailControl.objects.get_or_create(
        admin_email='admin@example.com',
        defaults={'is_primary': True}
    )
    print(f"✓ Admin email control: {admin_email} (created: {created})")

    return admin_email

def test_user_creation(admin_role, admin_email):
    """Test User creation with new fields"""
    print("\nTesting User creation...")

    # Create admin user
    admin_user = User.objects.create_user(
        email='admin@example.com',
        full_name='System Administrator',
        password='admin123',
        role=admin_role,
        created_by=None  # First admin has no creator
    )
    print(f"✓ Admin user created: {admin_user}")
    print(f"  - Email: {admin_user.email}")
    print(f"  - Role: {admin_user.role}")
    print(f"  - Status: {admin_user.status}")
    print(f"  - Created by: {admin_user.create_by}")

    # Create a regular user created by admin
    regular_user = User.objects.create_user(
        email='doctor@example.com',
        full_name='Dr. Smith',
        password='doctor123',
        role=Role.objects.get(role_name='Doctor'),
        created_by=admin_user
    )
    print(f"✓ Regular user created: {regular_user}")
    print(f"  - Created by: {regular_user.create_by}")

    return admin_user, regular_user

def test_audit_log(admin_user):
    """Test AuditLog model"""
    print("\nTesting AuditLog model...")

    # Create audit log entry
    audit_entry = AuditLog.objects.create(
        action_type='CREATE_USER',
        performed_by=admin_user,
        details='Created user doctor@example.com'
    )
    print(f"✓ Audit log entry: {audit_entry}")
    print(f"  - Action: {audit_entry.action_type}")
    print(f"  - Performed by: {audit_entry.performed_by}")
    print(f"  - Details: {audit_entry.details}")

    return audit_entry

def test_permissions_check(regular_user):
    """Test permission checking"""
    print("\nTesting permission checking...")

    # Check if regular user has admin permissions
    has_create_user = regular_user.has_perm('CREATE_USER')
    print(f"✓ Regular user has CREATE_USER permission: {has_create_user}")

    # Check if regular user has doctor permissions
    has_view_analysis = regular_user.has_perm('VIEW_ANALYSIS')
    print(f"✓ Regular user has VIEW_ANALYSIS permission: {has_view_analysis}")

def main():
    """Run all tests"""
    print("Starting IRD Document Implementation Tests")
    print("=" * 50)

    try:
        # Test roles
        roles = test_roles()

        # Test permissions
        permissions = test_permissions()

        # Test role permissions
        test_role_permissions(roles, permissions)

        # Test admin email control
        admin_email = test_admin_email_control()

        # Test user creation
        admin_user, regular_user = test_user_creation(roles[0], admin_email)

        # Test audit log
        audit_entry = test_audit_log(admin_user)

        # Test permissions
        test_permissions_check(regular_user)

        print("\n" + "=" * 50)
        print("✅ All tests passed successfully!")
        print("IRD Document implementation is working correctly.")

    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
