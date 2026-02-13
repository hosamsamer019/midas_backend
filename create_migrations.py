#!/usr/bin/env python
"""
Script to create migrations with automatic default value
"""

import os
import sys
import subprocess

# Change to the project directory
os.chdir(os.path.dirname(__file__))

# Run makemigrations with automatic input
cmd = [sys.executable, 'manage.py', 'makemigrations', 'users', 'audit']

# Start the process
process = subprocess.Popen(
    cmd,
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True
)

# Wait for the prompt and provide the default value
stdout, stderr = process.communicate(input='Migrated User\n')

print("STDOUT:")
print(stdout)
print("STDERR:")
print(stderr)
print(f"Return code: {process.returncode}")
