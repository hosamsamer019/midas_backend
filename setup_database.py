#!/usr/bin/env python
"""
Force setup database tables and create admin user
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from users.models import User, Role
from audit.models import AuditLog

def create_tables():
    """Create all necessary tables manually"""
    print("Creating database tables...")

    with connection.cursor() as cursor:
        # Create roles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS roles (
                role_id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_name VARCHAR(50) UNIQUE NOT NULL,
                description TEXT
            )
        ''')

        # Create permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS permissions (
                permission_id INTEGER PRIMARY KEY AUTOINCREMENT,
                permission_name VARCHAR(100) UNIQUE NOT NULL,
                description TEXT
            )
        ''')

        # Create role_permissions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS role_permissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role_id INTEGER NOT NULL,
                permission_id INTEGER NOT NULL,
                FOREIGN KEY (role_id) REFERENCES roles (role_id),
                FOREIGN KEY (permission_id) REFERENCES permissions (permission_id),
                UNIQUE(role_id, permission_id)
            )
        ''')

        # Drop users table if it exists to recreate with all fields
        cursor.execute('DROP TABLE IF EXISTS users;')

        # Create users table with all new fields (using Django's naming convention)
        cursor.execute('''
            CREATE TABLE users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                full_name VARCHAR(255) NOT NULL,
                email VARCHAR(254) UNIQUE NOT NULL,
                pass_hash VARCHAR(128) NOT NULL,
                role_id_id INTEGER,
                create_by_id INTEGER,
                create_at DATETIME NOT NULL,
                status VARCHAR(20) DEFAULT 'Active',
                is_verified BOOLEAN DEFAULT FALSE,
                failed_attempts INTEGER DEFAULT 0,
                lock_until DATETIME NULL,
                two_factor_enabled BOOLEAN DEFAULT FALSE,
                two_factor_secret VARCHAR(255),
                last_login DATETIME NULL,
                is_active BOOLEAN DEFAULT TRUE,
                is_staff BOOLEAN DEFAULT FALSE,
                is_superuser BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (role_id_id) REFERENCES roles (role_id),
                FOREIGN KEY (create_by_id) REFERENCES users (user_id)
            )
        ''')

        # Create admin_email_control table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS admin_email_control (
                control_id INTEGER PRIMARY KEY AUTOINCREMENT,
                admin_email VARCHAR(254) UNIQUE NOT NULL,
                is_primary BOOLEAN DEFAULT FALSE
            )
        ''')

        # Create audit_auditlog table with new fields
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS audit_auditlog (
                log_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action_type VARCHAR(100) NOT NULL,
                action_details TEXT,
                ip_address VARCHAR(39),
                user_agent TEXT,
                timestamp DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create refresh_tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS refresh_tokens (
                token_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                revoked BOOLEAN DEFAULT FALSE,
                ip_address VARCHAR(39),
                user_agent TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create password_reset_tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS password_reset_tokens (
                reset_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create email_verification_tokens table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS email_verification_tokens (
                verification_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash VARCHAR(255) NOT NULL,
                expires_at DATETIME NOT NULL,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create otp_codes table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS otp_codes (
                otp_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                otp_code VARCHAR(10) NOT NULL,
                expires_at DATETIME NOT NULL,
                used BOOLEAN DEFAULT FALSE,
                created_at DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

        # Create login_attempts table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_attempts (
                attempt_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                email_attempted VARCHAR(254) NOT NULL,
                ip_address VARCHAR(39),
                success BOOLEAN NOT NULL,
                attempt_time DATETIME NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')

    print("Tables created successfully!")

def create_roles_and_admin():
    """Create roles and admin user"""
    print("Creating roles and admin user...")

    # Create roles
    admin_role, created = Role.objects.get_or_create(
        role_name='Administrator',
        defaults={'description': 'System Administrator with full access'}
    )
    if created:
        print("Created Administrator role")

    doctor_role, created = Role.objects.get_or_create(
        role_name='Doctor',
        defaults={'description': 'Medical doctor with analysis access'}
    )
    if created:
        print("Created Doctor role")

    lab_role, created = Role.objects.get_or_create(
        role_name='Lab',
        defaults={'description': 'Lab technician with analysis access'}
    )
    if created:
        print("Created Lab role")

    viewer_role, created = Role.objects.get_or_create(
        role_name='Viewer',
        defaults={'description': 'Read-only access to reports'}
    )
    if created:
        print("Created Viewer role")

    # Create admin user
    admin_user, created = User.objects.get_or_create(
        email='admin',
        defaults={
            'full_name': 'System Administrator',
            'role_id': admin_role,
            'status': 'Active',
            'is_verified': True,
            'is_active': True,
            'is_staff': True
        }
    )

    if created:
        admin_user.set_password('password123')
        admin_user.save()
        print("Created admin user: admin with password: password123")
    else:
        # Update password if user exists but password might be wrong
        admin_user.set_password('password123')
        admin_user.save()
        print("Updated admin user password")

    return admin_user

def test_login():
    """Test admin login"""
    print("\nTesting admin login...")

    from django.contrib.auth import authenticate

    user = authenticate(username='admin', password='password123')
    if user:
        print("✅ Login successful!")
        print(f"  User: {user.email}")
        print(f"  Full Name: {user.full_name}")
        print(f"  Role: {user.role_id.role_name if user.role_id else 'None'}")
        print(f"  Is Admin: {user.is_admin}")
        return True
    else:
        print("❌ Login failed")
        return False

def main():
    try:
        create_tables()
        admin_user = create_roles_and_admin()
        success = test_login()

        if success:
            print("\n🎉 Database setup completed successfully!")
            print("Admin login credentials:")
            print("  Email: admin@test.com")
            print("  Password: admin123")
        else:
            print("\n❌ Login test failed")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
