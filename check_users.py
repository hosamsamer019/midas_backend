#!/usr/bin/env python
"""
Check current users in the database
"""

import os
import sys
import django

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'antibiogram.settings')
django.setup()

from users.models import User

print('Current users in database:')
print('=' * 50)

for user in User.objects.all():
    print(f'ID: {user.id}')
    if hasattr(user, 'username'):
        print(f'  Username: {user.username}')
    if hasattr(user, 'email'):
        print(f'  Email: {user.email}')
    if hasattr(user, 'full_name'):
        print(f'  Full Name: {user.full_name}')
    if hasattr(user, 'role'):
        print(f'  Role: {user.role}')
    if hasattr(user, 'status'):
        print(f'  Status: {user.status}')
    print()

print(f'Total users: {User.objects.count()}')
