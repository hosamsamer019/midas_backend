"""
Create users with specific permissions based on BRD specification
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User, Role, Permission, RolePermission
from django.contrib.auth import get_user_model

def create_permissions():
    """Create all required permissions"""
    permissions = [
        'create_user',
        'edit_permissions', 
        'upload_data',
        'view_analytics',
        'generate_reports',
        'use_ai',
        'send_messages',
        'delete_data',
    ]
    
    created_perms = []
    for perm_name in permissions:
        perm, created = Permission.objects.get_or_create(
            permission_name=perm_name,
            defaults={'description': f'Permission to {perm_name.replace("_", " ")}'}
        )
        created_perms.append(perm)
        if created:
            print(f"Created permission: {perm_name}")
    
    return created_perms

def assign_permissions():
    """Assign permissions to roles based on BRD specification"""
    
    # Get or create roles
    admin_role, _ = Role.objects.get_or_create(role_name='Administrator')
    doctor_role, _ = Role.objects.get_or_create(role_name='Doctor')
    lab_role, _ = Role.objects.get_or_create(role_name='Lab')
    viewer_role, _ = Role.objects.get_or_create(role_name='Viewer')
    
    # Get permissions
    perms = {p.permission_name: p for p in Permission.objects.all()}
    
    # Clear existing role permissions
    RolePermission.objects.all().delete()
    
    # Admin permissions (all permissions)
    admin_perms = ['create_user', 'edit_permissions', 'upload_data', 'view_analytics', 
                  'generate_reports', 'use_ai', 'send_messages', 'delete_data']
    for perm_name in admin_perms:
        if perm_name in perms:
            RolePermission.objects.create(role=admin_role, permission=perms[perm_name])
            print(f"Admin: {perm_name} ✅")
    
    # Doctor permissions
    doctor_perms = ['view_analytics', 'generate_reports', 'use_ai', 'send_messages']
    for perm_name in doctor_perms:
        if perm_name in perms:
            RolePermission.objects.create(role=doctor_role, permission=perms[perm_name])
            print(f"Doctor: {perm_name} ✅")
    
    # Lab permissions
    lab_perms = ['upload_data', 'view_analytics']
    for perm_name in lab_perms:
        if perm_name in perms:
            RolePermission.objects.create(role=lab_role, permission=perms[perm_name])
            print(f"Lab: {perm_name} ✅")
    
    # Viewer permissions
    viewer_perms = ['view_analytics']
    for perm_name in viewer_perms:
        if perm_name in perms:
            RolePermission.objects.create(role=viewer_role, permission=perms[perm_name])
            print(f"Viewer: {perm_name} ✅")
    
    print("\nPermissions assigned successfully!")

def create_users():
    """Create test users for each role"""
    
    # Get roles
    admin_role = Role.objects.get(role_name='Administrator')
    doctor_role = Role.objects.get(role_name='Doctor')
    lab_role = Role.objects.get(role_name='Lab')
    viewer_role = Role.objects.get(role_name='Viewer')
    
    users_to_create = [
        {
            'email': 'admin@hospital.com',
            'full_name': 'Admin User',
            'password': 'admin123',
            'role': admin_role,
            'is_superuser': True,
            'is_staff': True
        },
        {
            'email': 'doctor@hospital.com', 
            'full_name': 'Doctor User',
            'password': 'doctor123',
            'role': doctor_role,
            'is_superuser': False,
            'is_staff': False
        },
        {
            'email': 'lab@hospital.com',
            'full_name': 'Lab Technician',
            'password': 'lab123',
            'role': lab_role,
            'is_superuser': False,
            'is_staff': False
        },
        {
            'email': 'viewer@hospital.com',
            'full_name': 'Viewer User',
            'password': 'viewer123',
            'role': viewer_role,
            'is_superuser': False,
            'is_staff': False
        }
    ]
    
    created_users = []
    for user_data in users_to_create:
        role = user_data.pop('role')
        is_superuser = user_data.pop('is_superuser')
        is_staff = user_data.pop('is_staff')
        
        user, created = User.objects.get_or_create(
            email=user_data['email'],
            defaults={
                **user_data,
                'is_superuser': is_superuser,
                'is_staff': is_staff,
                'status': 'Active',
                'is_verified': True
            }
        )
        
        if created:
            user.set_password(user_data['password'])
            user.role_id = role
            user.save()
            print(f"Created user: {user.email} with role: {role.role_name}")
        else:
            # Update existing user role
            user.role_id = role
            user.save()
            print(f"Updated user: {user.email} with role: {role.role_name}")
        
        created_users.append(user)
    
    return created_users

def verify_permissions():
    """Verify permissions for each user"""
    print("\n=== Verifying User Permissions ===")
    
    for user in User.objects.all():
        print(f"\nUser: {user.email} ({user.role_id.role_name if user.role_id else 'No role'})")
        perms = user.get_all_permissions()
        for perm in sorted(perms):
            print(f"  - {perm}")

def main():
    print("=== Setting up Roles, Permissions and Users ===\n")
    
    # Step 1: Create permissions
    print("Step 1: Creating permissions...")
    create_permissions()
    
    # Step 2: Assign permissions to roles
    print("\nStep 2: Assigning permissions to roles...")
    assign_permissions()
    
    # Step 3: Create users
    print("\nStep 3: Creating users...")
    create_users()
    
    # Step 4: Verify
    print("\nStep 4: Verifying setup...")
    verify_permissions()
    
    print("\n=== Setup Complete ===")
    print("\nUsers created:")
    print("  Admin: admin@hospital.com / admin123")
    print("  Doctor: doctor@hospital.com / doctor123")
    print("  Lab: lab@hospital.com / lab123")
    print("  Viewer: viewer@hospital.com / viewer123")

if __name__ == '__main__':
    main()
