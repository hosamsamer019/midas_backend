from django.core.management.base import BaseCommand
from users.models import Role, Permission, RolePermission

class Command(BaseCommand):
    help = 'Set up BRD-compliant authentication system with roles and permissions'

    def handle(self, *args, **options):
        self.stdout.write('Setting up BRD Authentication System...\n')

        # Create permissions based on BRD requirements
        permissions_data = [
            # Core permissions
            {'name': 'view_dashboard', 'description': 'Access to main dashboard'},
            {'name': 'view_stats', 'description': 'View statistical data'},
            {'name': 'view_reports', 'description': 'Access to reports'},
            {'name': 'generate_reports', 'description': 'Generate and download reports'},
            {'name': 'view_data', 'description': 'View data records'},
            {'name': 'upload_data', 'description': 'Upload data files'},
            {'name': 'manage_users', 'description': 'Create, edit, and manage users'},
            {'name': 'use_ai', 'description': 'Access AI features'},
            {'name': 'send_messages', 'description': 'Send internal messages'},
            {'name': 'view_analytics', 'description': 'Access analytics features'},
            {'name': 'modify_data', 'description': 'Modify existing data'},
            {'name': 'delete_data', 'description': 'Delete data records'},
        ]

        permissions = {}
        for perm_data in permissions_data:
            perm, created = Permission.objects.get_or_create(
                permission_name=perm_data['name'],
                defaults={'description': perm_data['description']}
            )
            permissions[perm_data['name']] = perm
            if created:
                self.stdout.write(f'Created permission: {perm.permission_name}')

        # Create roles based on BRD
        roles_data = [
            {
                'name': 'Administrator',
                'description': 'Full system administrator with all permissions',
                'permissions': [
                    'view_dashboard', 'view_stats', 'view_reports', 'generate_reports',
                    'view_data', 'upload_data', 'manage_users', 'use_ai', 'send_messages',
                    'view_analytics', 'modify_data', 'delete_data'
                ]
            },
            {
                'name': 'Doctor',
                'description': 'Medical professional with analysis and reporting access',
                'permissions': [
                    'view_dashboard', 'view_stats', 'view_reports', 'generate_reports',
                    'view_data', 'use_ai', 'send_messages', 'view_analytics'
                ]
            },
            {
                'name': 'Lab',
                'description': 'Laboratory staff with data upload and viewing access',
                'permissions': [
                    'view_dashboard', 'view_stats', 'view_data', 'upload_data', 'use_ai'
                ]
            },
            {
                'name': 'Presenter',
                'description': 'Read-only access for presentations and basic viewing',
                'permissions': [
                    'view_dashboard', 'view_stats'
                ]
            }
        ]

        for role_data in roles_data:
            role, created = Role.objects.get_or_create(
                role_name=role_data['name'],
                defaults={'description': role_data['description']}
            )
            if created:
                self.stdout.write(f'Created role: {role.role_name}')

            # Assign permissions to role
            for perm_name in role_data['permissions']:
                if perm_name in permissions:
                    RolePermission.objects.get_or_create(
                        role=role,
                        permission=permissions[perm_name]
                    )

        self.stdout.write('\n✅ BRD Authentication System setup completed!')
        self.stdout.write('Roles and permissions have been created according to BRD specifications.')
