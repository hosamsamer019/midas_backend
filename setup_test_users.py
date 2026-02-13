#!/usr/bin/env python
"""
Setup test users for IRD implementation testing
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission, AdminEmailControl

def create_roles_and_permissions():
    """Create roles and permissions"""
    print("Creating roles and permissions...")

    # Create roles
    roles = {}
    role_names = ['Administrator', 'Doctor', 'Lab', 'Viewer']
    for role_name in role_names:
        role, created = Role.objects.get_or_create(
            role_name=role_name,
            defaults={'description': f'{role_name} role'}
        )
        roles[role_name] = role
        print(f"✓ {role_name} role: {'created' if created else 'exists'}")

    # Create permissions
    permissions = {}
    perm_names = [
        'CREATE_USER', 'EDIT_USER', 'DELETE_USER', 'LOAD_DATA',
        'CREATE_REPORT', 'VIEW_ANALYSIS', 'SEND_MESSAGE'
    ]
    for perm_name in perm_names:
        perm, created = Permission.objects.get_or_create(
            permission_name=perm_name,
            defaults={'description': f'{perm_name} permission'}
        )
        permissions[perm_name] = perm
        print(f"✓ {perm_name} permission: {'created' if created else 'exists'}")

    # Assign permissions to roles
    # Admin gets all permissions
    admin_perms = perm_names
    for perm_name in admin_perms:
        rp, created = RolePermission.objects.get_or_create(
            role=roles['Administrator'],
            permission=permissions[perm_name]
        )

    # Doctor gets some permissions
    doctor_perms = ['VIEW_ANALYSIS', 'CREATE_REPORT', 'SEND_MESSAGE']
    for perm_name in doctor_perms:
        rp, created = RolePermission.objects.get_or_create(
            role=roles['Doctor'],
            permission=permissions[perm_name]
        )

    # Lab gets data loading
    lab_perms = ['LOAD_DATA', 'VIEW_ANALYSIS']
    for perm_name in lab_perms:
        rp, created = RolePermission.objects.get_or_create(
            role=roles['Lab'],
            permission=permissions[perm_name]
        )

    # Viewer gets minimal permissions
    viewer_perms = ['VIEW_ANALYSIS']
    for perm_name in viewer_perms:
        rp, created = RolePermission.objects.get_or_create(
            role=roles['Viewer'],
            permission=permissions[perm_name]
        )

    print("✓ Permissions assigned to roles")
    return roles

def create_test_users(roles):
    """Create test users"""
    print("\nCreating test users...")

    # Using @hospital.com domain as requested
    users_data = [
        {
            'email': 'admin@hospital.com',
            'username': 'admin',
            'full_name': 'System Administrator',
            'password': 'admin123',
            'role': roles['Administrator']
        },
        {
            'email': 'doctor@hospital.com',
            'username': 'doctor',
            'full_name': 'Dr. Smith',
            'password': 'doctor123',
            'role': roles['Doctor']
        },
        {
            'email': 'lab@hospital.com',
            'username': 'lab',
            'full_name': 'Lab Technician',
            'password': 'lab123',
            'role': roles['Lab']
        },
        {
            'email': 'viewer@hospital.com',
            'username': 'viewer',
            'full_name': 'Data Viewer',
            'password': 'viewer123',
            'role': roles['Viewer']
        }
    ]

    created_users = []
    for user_data in users_data:
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                'username': user_data['username'],
                'full_name': user_data['full_name'],
                'role': user_data['role'],
                'status': 'Active'
            }
        )
        if created:
            user.set_password(user_data['password'])
            user.save()
            print(f"✓ Created user: {user.email}")
        else:
            # Update password if user exists
            user.set_password(user_data['password'])
            user.username = user_data['username']
            user.full_name = user_data['full_name']
            user.role = user_data['role']
            user.save()
            print(f"✓ Updated user: {user.email}")

        created_users.append(user)

    return created_users

def create_admin_email_control():
    """Create admin email control"""
    print("\nCreating admin email control...")

    admin_email, created = AdminEmailControl.objects.get_or_create(
        admin_email='admin@hospital.com',
        defaults={'is_primary': True}
    )
    print(f"✓ Admin email control: {'created' if created else 'exists'}")

    return admin_email

def main():
    """Setup test data"""
    print("Setting up test users for IRD implementation...")
    print("=" * 50)

    try:
        # Create roles and permissions
        roles = create_roles_and_permissions()

        # Create test users
        users = create_test_users(roles)

        # Create admin email control
        admin_email = create_admin_email_control()

        print("\n" + "=" * 50)
        print("✅ Test users setup completed!")
        print("\nTest Credentials:")
        print("admin@hospital.com / admin123 (Administrator)")
        print("doctor@hospital.com / doctor123 (Doctor)")
        print("lab@hospital.com / lab123 (Lab)")
        print("viewer@hospital.com / viewer123 (Viewer)")

    except Exception as e:
        print(f"\n❌ Setup failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == '__main__':
    sys.exit(main())
