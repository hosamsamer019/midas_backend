#!/usr/bin/env python
"""
Final verification test for login database modifications
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.contrib.auth import authenticate
from django.db import connection
from users.models import User, Role, RefreshToken, AuditLog

def quick_verification():
    """Quick verification of key components"""
    print("🔍 FINAL VERIFICATION TEST")
    print("=" * 50)

    # 1. Check database tables
    print("1. Checking database tables...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('users', 'roles', 'audit_auditlog', 'refresh_tokens');")
        tables = [row[0] for row in cursor.fetchall()]
        required_tables = {'users', 'roles', 'audit_auditlog', 'refresh_tokens'}
        if required_tables.issubset(set(tables)):
            print("   ✅ All required tables exist")
        else:
            print(f"   ❌ Missing tables: {required_tables - set(tables)}")
            return False

    # 2. Check admin user
    print("2. Checking admin user...")
    try:
        user = User.objects.get(email='admin')
        print(f"   ✅ Admin user found: {user.email}")
        print(f"   ✅ Role: {user.role_id.role_name if user.role_id else 'None'}")
        print(f"   ✅ Security fields: failed_attempts={user.failed_attempts}, is_verified={user.is_verified}")
    except User.DoesNotExist:
        print("   ❌ Admin user not found")
        return False

    # 3. Test authentication
    print("3. Testing authentication...")
    auth_user = authenticate(username='admin', password='password123')
    if auth_user:
        print("   ✅ Authentication successful")
    else:
        print("   ❌ Authentication failed")
        return False

    # 4. Test account lock functionality
    print("4. Testing account lock...")
    user.reset_failed_attempts()
    for i in range(5):
        user.increment_failed_attempts()
    if user.is_locked():
        print("   ✅ Account lock working (locked after 5 attempts)")
        user.reset_failed_attempts()
        if not user.is_locked():
            print("   ✅ Account unlock working")
        else:
            print("   ❌ Account unlock failed")
            return False
    else:
        print("   ❌ Account lock not working")
        return False

    # 5. Test audit logging
    print("5. Testing audit logging...")
    audit_entry = AuditLog.objects.create(
        user_id=user,
        action_type='test_verification',
        action_details='Final verification test',
        ip_address='127.0.0.1',
        user_agent='Verification Script'
    )
    if audit_entry.action_details and audit_entry.user_agent:
        print("   ✅ Enhanced audit logging working")
    else:
        print("   ❌ Enhanced audit logging failed")
        return False

    # 6. Test security models
    print("6. Testing security models...")
    refresh_token = RefreshToken.objects.create(
        user=user,
        token_hash='test_hash',
        expires_at=django.utils.timezone.now() + django.utils.timezone.timedelta(hours=1),
        ip_address='127.0.0.1',
        user_agent='Test'
    )
    if refresh_token:
        print("   ✅ RefreshToken model working")
    else:
        print("   ❌ RefreshToken model failed")
        return False

    print("\n🎉 ALL VERIFICATION TESTS PASSED!")
    print("The login database modifications are fully implemented and functional.")
    return True

if __name__ == '__main__':
    success = quick_verification()
    if not success:
        print("\n❌ VERIFICATION FAILED - Please check the implementation")
        exit(1)
    else:
        print("\n✅ VERIFICATION SUCCESSFUL")
        exit(0)
