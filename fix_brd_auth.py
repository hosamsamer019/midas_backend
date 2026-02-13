#!/usr/bin/env python
import os
import django
import requests

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission
from audit.models import AuditLog

def diagnose_and_fix_auth():
    print('🔍 DIAGNOSING BRD AUTHENTICATION SYSTEM')
    print('=' * 50)

    # Step 1: Check database tables
    print('\n1. Checking Database Tables...')
    from django.db import connection
    cursor = connection.cursor()

    tables = ['users', 'roles', 'permissions', 'role_permissions', 'audit_log']
    for table in tables:
        cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}';")
        result = cursor.fetchone()
        status = '✅' if result else '❌'
        print(f'   {status} {table}: {"EXISTS" if result else "MISSING"}')

    # Step 2: Check roles
    print('\n2. Checking Roles...')
    roles = Role.objects.all()
    if roles.exists():
        print(f'   ✅ Found {roles.count()} roles: {[r.role_name for r in roles]}')
    else:
        print('   ❌ No roles found - creating them...')
        roles_data = [
            ('Administrator', 'System Administrator with full access'),
            ('Doctor', 'Medical professional with analysis access'),
            ('Lab', 'Lab technician with data entry access'),
            ('Presenter', 'Read-only access for presentations')
        ]
        for role_name, description in roles_data:
            Role.objects.get_or_create(role_name=role_name, defaults={'description': description})
        print('   ✅ Created default roles')

    # Step 3: Check permissions
    print('\n3. Checking Permissions...')
    permissions = Permission.objects.all()
    if permissions.exists():
        print(f'   ✅ Found {permissions.count()} permissions')
    else:
        print('   ❌ No permissions found - creating them...')
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
        for perm_name, description in permissions_data:
            Permission.objects.get_or_create(permission_name=perm_name, defaults={'description': description})
        print('   ✅ Created default permissions')

    # Step 4: Check admin user
    print('\n4. Checking Admin User...')
    try:
        admin_user = User.objects.get(email='admin@hospital.com')
        print(f'   ✅ Admin user exists: {admin_user.full_name}')
        print(f'      Email: {admin_user.email}')
        print(f'      Role: {admin_user.role.role_name if admin_user.role else "None"}')
        print(f'      Status: {admin_user.status}')
        print(f'      Is Active: {admin_user.is_active}')
    except User.DoesNotExist:
        print('   ❌ Admin user NOT found - creating...')
        try:
            admin_role = Role.objects.get(role_name='Administrator')

            # Assign all permissions to admin role
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

    # Step 5: Test Django authentication
    print('\n5. Testing Django Authentication...')
    from django.contrib.auth import authenticate

    # Test with username parameter (email)
    test_user = authenticate(username='admin@hospital.com', password='admin123')
    if test_user:
        print('   ✅ Django authenticate(username=email) PASSED')
        print(f'      User: {test_user.full_name}')
        print(f'      Role: {test_user.role.role_name if test_user.role else "None"}')
    else:
        print('   ❌ Django authenticate(username=email) FAILED')

    # Test with email parameter
    test_user2 = authenticate(email='admin@hospital.com', password='admin123')
    if test_user2:
        print('   ✅ Django authenticate(email=...) PASSED')
    else:
        print('   ❌ Django authenticate(email=...) FAILED')

    # Step 6: Test API login
    print('\n6. Testing API Login...')
    try:
        response = requests.post(
            'http://localhost:8000/api/auth/token/',
            json={
                'email': 'admin@hospital.com',
                'password': 'admin123'
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            print('   ✅ API login PASSED')
            print(f'      Access token: {data.get("access", "")[:20]}...')
            print(f'      User: {data.get("user", {}).get("full_name", "Unknown")}')
        else:
            print(f'   ❌ API login FAILED: HTTP {response.status_code}')
            print(f'      Response: {response.text}')

    except requests.exceptions.ConnectionError:
        print('   ❌ API test failed: Server not running (connection refused)')
    except requests.exceptions.Timeout:
        print('   ❌ API test failed: Server timeout')
    except Exception as e:
        print(f'   ❌ API test failed: {e}')

    print('\n' + '=' * 50)
    print('🔍 DIAGNOSIS COMPLETE')
    print('\n📝 SUMMARY:')
    print('- Database tables: Check above')
    print('- Roles: Should have Administrator, Doctor, Lab, Presenter')
    print('- Permissions: Should have 9 basic permissions')
    print('- Admin user: admin@hospital.com / admin123')
    print('- Django auth: Should work with username=email')
    print('- API login: Should return JWT tokens')

if __name__ == '__main__':
    diagnose_and_fix_auth()
