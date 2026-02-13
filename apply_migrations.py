#!/usr/bin/env python
"""
Migration guide for critical database schema changes
Run Django migrations after making these model changes:

1. User model:
   - Removed duplicate 'password' CharField (uses AbstractBaseUser.password)
   - Removed duplicate 'last_login' DateTimeField (uses AbstractBaseUser.last_login)
   
   Commands:
   python manage.py makemigrations users
   python manage.py migrate users

2. AuditLog model:
   - Changed 'user' ForeignKey from CASCADE to SET_NULL
   - This preserves audit records when users are deleted
   
   Commands:
   python manage.py makemigrations audit
   python manage.py migrate audit

3. Message model:
   - Changed 'sender' ForeignKey from CASCADE to SET_NULL
   - Changed 'recipient' ForeignKey from CASCADE to SET_NULL
   - Changed 'content_type' ForeignKey from CASCADE to SET_NULL
   - This preserves messages when users or content types are deleted
   
   Commands:
   python manage.py makemigrations messaging
   python manage.py migrate messaging

4. After all migrations, verify schema:
   python manage.py dbshell
   
   # In PostgreSQL/SQLite shell:
   # Check users table lacks duplicate fields:
   SELECT column_name FROM information_schema.columns WHERE table_name='users' AND column_name IN ('password', 'last_login');
   
   # Check foreign keys have correct on_delete:
   SELECT constraint_name, constraint_type FROM information_schema.table_constraints WHERE table_name='audit_log';

IMPORTANT NOTES:
- Backup database before running migrations in production
- Test migrations on staging environment first
- Monitor for any CASCADE deletes that now become SET_NULL (users become null in audit_log/messages)
- Update any code that assumes sender/recipient/user is non-null (already fixed with null checks)
"""

import os
import subprocess
import sys

def run_command(cmd, description):
    """Run a command and report status"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {cmd}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False)
        if result.returncode == 0:
            print(f"✓ {description} completed successfully")
            return True
        else:
            print(f"✗ {description} failed with return code {result.returncode}")
            return False
    except Exception as e:
        print(f"✗ Error running {description}: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("MIGRATION HELPER")
    print("="*60)
    
    # Check if we're in Django project root
    if not os.path.exists('manage.py'):
        print("\n✗ ERROR: manage.py not found. Run this script from project root")
        sys.exit(1)
    
    # Make migrations
    success = True
    
    print("\n[Step 1/5] Creating migrations for users...")
    success &= run_command("python manage.py makemigrations users", "makemigrations users")
    
    print("\n[Step 2/5] Creating migrations for audit...")
    success &= run_command("python manage.py makemigrations audit", "makemigrations audit")
    
    print("\n[Step 3/5] Creating migrations for messaging...")
    success &= run_command("python manage.py makemigrations messaging", "makemigrations messaging")
    
    if not success:
        print("\n⚠ Some migration creation steps failed. Review errors above.")
        sys.exit(1)
    
    print("\n[Step 4/5] Showing migration plan...")
    result = run_command("python manage.py showmigrations --plan", "showmigrations")
    if result:
        lines = result.split('\n')
        print('\n'.join(lines[-20:]))  # Show last 20 lines
    
    # Ask before applying
    print("\n" + "="*60)
    response = input("\nApply migrations now? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("\n✓ Migrations created but not applied. Run 'python manage.py migrate' when ready.")
        sys.exit(0)
    
    print("\n[Step 5/5] Applying migrations...")
    
    # Backup reminder
    print("\nBACKUP REMINDER: Ensure your database is backed up before proceeding!")
    response = input("Continue with migration application? (yes/no): ").strip().lower()
    
    if response != 'yes':
        print("Cancelled. No migrations were applied.")
        sys.exit(0)
    
    success = True
    success &= run_command("python manage.py migrate users", "migrate users")
    success &= run_command("python manage.py migrate audit", "migrate audit")
    success &= run_command("python manage.py migrate messaging", "migrate messaging")
    
    if success:
        print("\n✓ All migrations applied successfully!")
        print("\nVerify with: python manage.py showmigrations")
    else:
        print("\n✗ Some migrations failed. Check database for inconsistencies.")
        sys.exit(1)

if __name__ == '__main__':
    main()
