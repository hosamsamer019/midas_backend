#!/usr/bin/env python
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission
from audit.models import AuditLog

def test_brd_authentication():
    print('=== BRD AUTHENTICATION SYSTEM TEST ===')

    # Check database state
    print('\n1. Database State:')
    roles = Role.objects.all()
    permissions = Permission.objects.all()
    users = User.objects.all()

    print(f'   Roles: {list(roles.values_list("role_name", flat=True))}')
    print(f'   Permissions: {list(permissions.values_list("permission_name", flat=True))}')
    print(f'   Users: {list(users.values_list("email", flat=True))}')

    # Check admin user
    print('\n2. Admin User Check:')
    try:
        admin_user = User.objects.get(email='admin@hospital.com')
        print(f'   ✅ Admin user found: {admin_user.full_name}')
        print(f'   Role: {admin_user.role.role_name if admin_user.role else "None"}')
        print(f'   Status: {admin_user.status}')
        print(f'   Permissions: {list(admin_user.get_all_permissions())}')
    except User.DoesNotExist:
        print('   ❌ Admin user NOT found - creating one...')

        # Create admin user if not exists
        try:
            # Get or create admin role
            admin_role, _ = Role.objects.get_or_create(
                role_name='Administrator',
                defaults={'description': 'System Administrator with full access'}
            )

            # Create permissions
            permissions_data = [
                ('create_user', 'Create new user accounts'),
                ('edit_user', 'Edit user information'),
                ('delete_user', 'Delete user accounts'),
                ('upload_data', 'Upload data files'),
                ('modify_data', 'Modify existing data'),
                ('view_reports', 'View analysis reports'),
                ('delete_data', 'Delete data records'),
                ('view_dashboard', 'Access dashboard'),
                ('manage_system', 'System administration'),
            ]

            for perm_name, desc in permissions_data:
                Permission.objects.get_or_create(
                    permission_name=perm_name,
                    defaults={'description': desc}
                )

            # Assign all permissions to admin
            for perm in Permission.objects.all():
                RolePermission.objects.get_or_create(role=admin_role, permission=perm)

            # Create admin user
            admin_user = User.objects.create_user(
                email='admin@hospital.com',
                full_name='System Administrator',
                password='admin123',
                role=admin_role,
                status='Active'
            )
            print(f'   ✅ Admin user created: {admin_user.email}')

        except Exception as e:
            print(f'   ❌ Error creating admin user: {e}')
            return

    # Test authentication
    print('\n3. Authentication Test:')
    from django.contrib.auth import authenticate

    test_user = authenticate(username='admin@hospital.com', password='admin123')
    if test_user:
        print('   ✅ Django authenticate() PASSED')
    else:
        print('   ❌ Django authenticate() FAILED')

    # Test API login
    print('\n4. API Login Test:')
    try:
        response = requests.post(
            'http://localhost:8000/api/auth/token/',
            json={
                'email': 'admin@hospital.com',
                'password': 'admin123'
            },
            timeout=5
        )

        if response.status_code == 200:
            data = response.json()
            print('   ✅ API login PASSED')
            print(f'   Access token: {data.get("access", "")[:20]}...')
            print(f'   User: {data.get("user", {}).get("full_name", "Unknown")}')
        else:
            print(f'   ❌ API login FAILED: {response.status_code}')
            print(f'   Response: {response.text}')

    except requests.exceptions.RequestException as e:
        print(f'   ❌ API test failed (server not running?): {e}')

if __name__ == '__main__':
    test_brd_authentication()
