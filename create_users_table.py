#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from django.db import connection

def create_users_table():
    with connection.cursor() as cursor:
        # Drop table if exists
        cursor.execute('DROP TABLE IF EXISTS users;')

        # Create users table
        cursor.execute('''
        CREATE TABLE users (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name VARCHAR(255) NOT NULL,
            email VARCHAR(254) NOT NULL UNIQUE,
            password VARCHAR(128) NOT NULL,
            role_id INTEGER,
            status VARCHAR(20) NOT NULL DEFAULT 'Active',
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            last_login DATETIME NULL,
            is_active BOOLEAN NOT NULL DEFAULT 1,
            is_staff BOOLEAN NOT NULL DEFAULT 0,
            is_superuser BOOLEAN NOT NULL DEFAULT 0,
            FOREIGN KEY (role_id) REFERENCES roles (role_id)
        );
        ''')

        # Verify table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
        result = cursor.fetchone()
        print(f'✅ Users table created: {result is not None}')

if __name__ == '__main__':
    create_users_table()
