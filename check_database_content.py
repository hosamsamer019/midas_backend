#!/usr/bin/env python
"""
Database Content Check Script
Checks if the database exists, has tables, and contains data.
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')

# Setup Django
django.setup()

def check_database():
    print('=== DATABASE STATUS CHECK ===')
    db_path = 'icu_antibiotic.db'
    print(f'Database file exists: {os.path.exists(db_path)}')
    if os.path.exists(db_path):
        print(f'Database file size: {os.path.getsize(db_path)} bytes')

    print()
    print('=== TABLES IN DATABASE ===')
    from django.db import connection
    cursor = connection.cursor()
    cursor.execute('SELECT name FROM sqlite_master WHERE type="table"')
    tables = cursor.fetchall()
    table_names = [table[0] for table in tables]
    print(f'Number of tables: {len(table_names)}')
    for table in table_names:
        print(f'- {table}')

    print()
    print('=== DATA IN TABLES ===')
    for table_name in table_names:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            print(f'{table_name}: {count} records')
        except Exception as e:
            print(f'{table_name}: Error - {e}')

    print()
    print('=== SAMPLE DATA CHECK ===')
    # Check for sample data in key tables
    key_tables = ['users_user', 'bacteria_bacteria', 'antibiotics_antibiotic', 'results_testresult']
    for table in key_tables:
        if table in table_names:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                if count > 0:
                    print(f'{table}: Has {count} records')
                else:
                    print(f'{table}: Empty (0 records)')
            except Exception as e:
                print(f'{table}: Error checking - {e}')
        else:
            print(f'{table}: Table does not exist')

    print()
    print('=== CONCLUSION ===')
    total_records = 0
    for table_name in table_names:
        try:
            cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
            count = cursor.fetchone()[0]
            total_records += count
        except:
            pass

    if total_records == 0:
        print('❌ DATABASE IS EMPTY - No data found in any table')
        print('💡 You need to populate the database with sample data')
    else:
        print(f'✅ DATABASE HAS DATA - Total {total_records} records across all tables')

if __name__ == '__main__':
    check_database()
