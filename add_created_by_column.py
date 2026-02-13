#!/usr/bin/env python
"""
Script to add created_by_id column to samples_sample table
"""
import sqlite3
import os

# Database path
db_path = os.path.join(os.path.dirname(__file__), 'icu_antibiotic.db')

# Connect to the database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if the column already exists
cursor.execute("PRAGMA table_info(samples_sample)")
columns = [col[1] for col in cursor.fetchall()]

if 'created_by_id' not in columns:
    # Add the column
    cursor.execute("ALTER TABLE samples_sample ADD COLUMN created_by_id INTEGER REFERENCES users_user(user_id)")
    conn.commit()
    print("Column 'created_by_id' added successfully!")
else:
    print("Column 'created_by_id' already exists.")

# Verify the column is there now
cursor.execute("PRAGMA table_info(samples_sample)")
columns = [col[1] for col in cursor.fetchall()]
print(f"Current columns: {columns}")

conn.close()
print("Done!")
