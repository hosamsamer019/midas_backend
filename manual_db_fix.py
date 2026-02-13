#!/usr/bin/env python
"""
Manually fix the admin user in the database
"""
import sqlite3
import os

def fix_admin_user():
    db_path = os.path.join(os.path.dirname(__file__), 'db.sqlite3')

    if not os.path.exists(db_path):
        print("Database file not found")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check current users
    cursor.execute("SELECT user_id, email, full_name FROM users")
    users = cursor.fetchall()
    print("Current users:")
    for user in users:
        print(f"  ID: {user[0]}, Email: {user[1]}, Name: {user[2]}")

    # Update user with email 'admin' to 'admin@test.com'
    cursor.execute("UPDATE users SET email = ? WHERE email = ?", ('admin@test.com', 'admin'))

    # Set password hash for admin123 (Django's hash)
    from django.contrib.auth.hashers import make_password
    hashed_password = make_password('admin123')
    cursor.execute("UPDATE users SET pass_hash = ? WHERE email = ?", (hashed_password, 'admin@test.com'))

    # Check if admin role exists
    cursor.execute("SELECT role_id FROM roles WHERE role_name = ?", ('Administrator',))
    role = cursor.fetchone()
    if role:
        cursor.execute("UPDATE users SET role_id = ? WHERE email = ?", (role[0], 'admin@test.com'))

    conn.commit()
    conn.close()

    print("✅ Admin user updated to admin@test.com with password admin123")

if __name__ == '__main__':
    fix_admin_user()
