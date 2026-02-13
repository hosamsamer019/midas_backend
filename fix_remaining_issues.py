#!/usr/bin/env python
"""
Helper script to batch-fix common remaining issues
Run this from the Data_Analysis_Project directory
"""
import os
import re
import json
from pathlib import Path

def load_pii_patterns():
    """Load PII patterns from config file"""
    config_path = Path('pii_patterns.json')
    if not config_path.exists():
        print(f"Warning: {config_path} not found. Using default patterns.")
        return {
            r'[A-Za-z\u0600-\u06FF]{3,}\s[A-Za-z\u0600-\u06FF]{3,}': '[PATIENT_NAME]',
            r'\d{10,11}': '[PHONE]',
            r'\d{5,9}': '[ID]',
        }
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading PII patterns from config: {e}")
        return {}

def fix_pii_in_test_results():
    """Remove/anonymize PII from test result JSON files"""
    base_path = Path('.')
    test_files = sorted(base_path.glob('chatbot_test_results_*.json'))
    
    pii_patterns = load_pii_patterns()
    
    for file_path in test_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply PII redactions
            for pattern, replacement in pii_patterns.items():
                content = re.sub(pattern, replacement, content)
            
            # Remove debug sensitive data
            content = re.sub(r'0x[0-9A-Fa-f]+', '[MEMORY_ADDR]', content)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✓ Cleaned: {file_path}")
        except Exception as e:
            print(f"✗ Error processing {file_path}: {e}")

def add_gitignore_exclusions():
    """Add test artifact patterns to .gitignore"""
    gitignore_path = Path('.gitignore')
    patterns_to_add = [
        '# Test artifacts with timestamps',
        '**/chatbot_test_results_*.json',
        '**/chatbot_db_test_results_*.json',
        '',
    ]
    
    try:
        with open(gitignore_path, 'a') as f:
            f.write('\n'.join(patterns_to_add) + '\n')
        print("✓ Updated .gitignore")
    except Exception as e:
        print(f"✗ Error updating .gitignore: {e}")

def check_environment_variables():
    """Verify critical environment variables are documented"""
    required_env_vars = [
        'SECRET_KEY',
        'DATABASE_URL',
        'OPENAI_API_KEY',
        'DEBUG',
        'ALLOWED_HOSTS',
        'CORS_ALLOWED_ORIGINS',
        'CSRF_TRUSTED_ORIGINS',
    ]
    
    env_example_path = Path('.env.example')
    
    try:
        existing = set()
        if env_example_path.exists():
            with open(env_example_path, 'r') as f:
                existing = set(re.findall(r'^([A-Z_]+)=', f.read(), re.MULTILINE))
        
        missing = [var for var in required_env_vars if var not in existing]
        
        if missing:
            print(f"⚠ Missing in .env.example: {', '.join(missing)}")
            # Create/append to .env.example
            with open(env_example_path, 'a') as f:
                for var in missing:
                    if var == 'SECRET_KEY':
                        f.write(f"\n# Django secret key - generate with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\"\n")
                        f.write(f"{var}=your-secret-key-here\n")
                    elif var == 'DATABASE_URL':
                        f.write(f"\n# PostgreSQL connection string\n")
                        f.write(f"{var}=postgresql://user:password@localhost:5432/antibiogram\n")
                    elif var == 'OPENAI_API_KEY':
                        f.write(f"\n# Set only if using OpenAI (otherwise use LocalAI)\n")
                        f.write(f"{var}=sk-...\n")
                    else:
                        f.write(f"{var}=\n")
            print(f"✓ Created/updated .env.example")
        else:
            print("✓ All required env vars documented")
            
    except Exception as e:
        print(f"✗ Error checking env vars: {e}")

def verify_migrations():
    """List pending migrations"""
    os.system('python manage.py showmigrations --plan | grep "\[ \]"')

if __name__ == '__main__':
    print("=" * 60)
    print("Running batch fixes...")
    print("=" * 60)
    
    print("\n[1/4] Fixing PII in test results...")
    fix_pii_in_test_results()
    
    print("\n[2/4] Updating .gitignore...")
    add_gitignore_exclusions()
    
    print("\n[3/4] Checking environment variables...")
    check_environment_variables()
    
    print("\n[4/4] Listing pending migrations...")
    print("\nPending migrations that need to be created/applied:")
    verify_migrations()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("=" * 60)
    print("1. python manage.py makemigrations")
    print("2. python manage.py migrate")
    print("3. Review CRITICAL_ISSUES_REMAINING.md for remaining fixes")
    print("=" * 60)
