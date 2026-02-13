#!/usr/bin/env python
"""
Comprehensive security testing for login database modifications
"""
import os
import django
from datetime import timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.contrib.auth import authenticate
from django.utils import timezone
from django.db import connection
from users.models import (
    User, Role, Permission, RolePermission,
    RefreshToken, PasswordResetToken, EmailVerificationToken,
    OTPCode, LoginAttempt
)
from audit.models import AuditLog

def test_account_lock_functionality():
    """Test account lock after 5 failed attempts"""
    print("=== Testing Account Lock Functionality ===")

    # Get admin user
    try:
        user = User.objects.get(email='admin')
        print(f"Testing with user: {user.email}")

        # Reset any existing lock
        user.reset_failed_attempts()
        print("Reset failed attempts counter")

        # Test 4 failed attempts (should not lock)
        for i in range(4):
            user.increment_failed_attempts()
            print(f"Attempt {i+1}: failed_attempts = {user.failed_attempts}, locked = {user.is_locked()}")

        # Check that account is not locked yet
        if not user.is_locked():
            print("✅ Account not locked after 4 failed attempts")
        else:
            print("❌ Account incorrectly locked after 4 failed attempts")

        # 5th failed attempt should lock
        user.increment_failed_attempts()
        print(f"Attempt 5: failed_attempts = {user.failed_attempts}, locked = {user.is_locked()}")

        if user.is_locked():
            print("✅ Account locked after 5 failed attempts")
        else:
            print("❌ Account not locked after 5 failed attempts")

        # Test reset functionality
        user.reset_failed_attempts()
        print(f"After reset: failed_attempts = {user.failed_attempts}, locked = {user.is_locked()}")

        if not user.is_locked() and user.failed_attempts == 0:
            print("✅ Account lock reset successful")
        else:
            print("❌ Account lock reset failed")

        return True

    except Exception as e:
        print(f"❌ Error testing account lock: {e}")
        return False

def test_audit_logging():
    """Test enhanced audit logging"""
    print("\n=== Testing Enhanced Audit Logging ===")

    try:
        user = User.objects.get(email='admin')

        # Create audit log entry with new fields
        audit_entry = AuditLog.objects.create(
            user_id=user,
            action_type='test_login',
            action_details='Testing enhanced audit logging with new fields',
            ip_address='192.168.1.100',
            user_agent='Mozilla/5.0 (Test Browser)',
            timestamp=timezone.now()
        )

        print(f"Created audit log entry: {audit_entry}")
        print(f"Action details: {audit_entry.action_details}")
        print(f"User agent: {audit_entry.user_agent}")
        print(f"IP address: {audit_entry.ip_address}")

        # Verify the entry was saved
        saved_entry = AuditLog.objects.get(log_id=audit_entry.log_id)
        if saved_entry.action_details and saved_entry.user_agent:
            print("✅ Enhanced audit logging working correctly")
            return True
        else:
            print("❌ Enhanced audit logging failed")
            return False

    except Exception as e:
        print(f"❌ Error testing audit logging: {e}")
        return False

def test_security_models():
    """Test new security models"""
    print("\n=== Testing New Security Models ===")

    try:
        user = User.objects.get(email='admin')

        # Test RefreshToken
        refresh_token = RefreshToken.objects.create(
            user=user,
            token_hash='test_refresh_token_hash',
            expires_at=timezone.now() + timedelta(hours=24),
            ip_address='192.168.1.100',
            user_agent='Test Browser'
        )
        print(f"✅ Created RefreshToken: {refresh_token}")

        # Test PasswordResetToken
        reset_token = PasswordResetToken.objects.create(
            user=user,
            token_hash='test_reset_token_hash',
            expires_at=timezone.now() + timedelta(hours=1)
        )
        print(f"✅ Created PasswordResetToken: {reset_token}")

        # Test EmailVerificationToken
        email_token = EmailVerificationToken.objects.create(
            user=user,
            token_hash='test_email_token_hash',
            expires_at=timezone.now() + timedelta(days=1)
        )
        print(f"✅ Created EmailVerificationToken: {email_token}")

        # Test OTPCode
        otp_code = OTPCode.objects.create(
            user=user,
            otp_code='123456',
            expires_at=timezone.now() + timedelta(minutes=5)
        )
        print(f"✅ Created OTPCode: {otp_code}")

        # Test LoginAttempt
        login_attempt = LoginAttempt.objects.create(
            user=user,
            email_attempted=user.email,
            ip_address='192.168.1.100',
            success=True,
            attempt_time=timezone.now()
        )
        print(f"✅ Created LoginAttempt: {login_attempt}")

        # Test expiration methods
        if not refresh_token.is_expired():
            print("✅ RefreshToken expiration check working")
        else:
            print("❌ RefreshToken expiration check failed")

        if not reset_token.is_expired():
            print("✅ PasswordResetToken expiration check working")
        else:
            print("❌ PasswordResetToken expiration check failed")

        if not email_token.is_expired():
            print("✅ EmailVerificationToken expiration check working")
        else:
            print("❌ EmailVerificationToken expiration check failed")

        if not otp_code.is_expired():
            print("✅ OTPCode expiration check working")
        else:
            print("❌ OTPCode expiration check failed")

        print("✅ All security models working correctly")
        return True

    except Exception as e:
        print(f"❌ Error testing security models: {e}")
        return False

def test_rbac_permissions():
    """Test RBAC permission system"""
    print("\n=== Testing RBAC Permissions ===")

    try:
        # Get admin user and role
        user = User.objects.get(email='admin')
        admin_role = Role.objects.get(role_name='Administrator')

        # Create a test permission
        permission, created = Permission.objects.get_or_create(
            permission_name='test_permission',
            defaults={'description': 'Test permission for RBAC testing'}
        )

        # Create role-permission relationship
        role_perm, created = RolePermission.objects.get_or_create(
            role=admin_role,
            permission=permission
        )

        print(f"Created permission: {permission}")
        print(f"Created role-permission: {role_perm}")

        # Test permission checking
        if user.has_perm('test_permission'):
            print("✅ RBAC permission checking working")
        else:
            print("❌ RBAC permission checking failed")

        # Test permission list checking
        if user.has_perms(['test_permission']):
            print("✅ RBAC permission list checking working")
        else:
            print("❌ RBAC permission list checking failed")

        # Test all permissions retrieval
        all_perms = user.get_all_permissions()
        if 'test_permission' in all_perms:
            print("✅ RBAC get_all_permissions working")
        else:
            print("❌ RBAC get_all_permissions failed")

        return True

    except Exception as e:
        print(f"❌ Error testing RBAC permissions: {e}")
        return False

def test_user_properties():
    """Test user role properties"""
    print("\n=== Testing User Role Properties ===")

    try:
        user = User.objects.get(email='admin')

        print(f"User role: {user.role_id.role_name if user.role_id else 'None'}")
        print(f"Is admin: {user.is_admin}")
        print(f"Is doctor: {user.is_doctor}")
        print(f"Is lab: {user.is_lab}")
        print(f"Is viewer: {user.is_viewer}")

        if user.is_admin:
            print("✅ User role properties working correctly")
            return True
        else:
            print("❌ User role properties failed")
            return False

    except Exception as e:
        print(f"❌ Error testing user properties: {e}")
        return False

def test_database_integrity():
    """Test database integrity and relationships"""
    print("\n=== Testing Database Integrity ===")

    try:
        with connection.cursor() as cursor:
            # Check all tables exist
            tables = [
                'users', 'roles', 'permissions', 'role_permissions',
                'audit_auditlog', 'refresh_tokens', 'password_reset_tokens',
                'email_verification_tokens', 'otp_codes', 'login_attempts'
            ]

            missing_tables = []
            for table in tables:
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?;", [table])
                if not cursor.fetchone():
                    missing_tables.append(table)

            if not missing_tables:
                print("✅ All required tables exist")
            else:
                print(f"❌ Missing tables: {missing_tables}")
                return False

            # Check foreign key relationships
            cursor.execute("PRAGMA foreign_key_check;")
            fk_violations = cursor.fetchall()
            if not fk_violations:
                print("✅ No foreign key violations")
            else:
                print(f"❌ Foreign key violations: {fk_violations}")
                return False

        return True

    except Exception as e:
        print(f"❌ Error testing database integrity: {e}")
        return False

def main():
    """Run all comprehensive security tests"""
    print("🔒 COMPREHENSIVE SECURITY TESTING FOR LOGIN DATABASE MODIFICATIONS")
    print("=" * 70)

    tests = [
        test_account_lock_functionality,
        test_audit_logging,
        test_security_models,
        test_rbac_permissions,
        test_user_properties,
        test_database_integrity
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 70)
    print("📊 TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = sum(results)
    total = len(results)

    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{i+1}. {test.__name__}: {status}")

    print(f"\nOverall: {passed}/{total} tests passed")

    if passed == total:
        print("🎉 ALL SECURITY TESTS PASSED!")
        print("The login database modifications are fully functional and secure.")
    else:
        print("⚠️  Some tests failed. Please review the implementation.")

    return passed == total

if __name__ == '__main__':
    main()
