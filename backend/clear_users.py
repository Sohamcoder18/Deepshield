#!/usr/bin/env python3
"""
Clear SQLite user data to allow fresh signup testing
Run this before testing the signup with all fields
"""

import sqlite3
import os

db_path = 'deepfake_detection.db'

if not os.path.exists(db_path):
    print(f"✓ Database doesn't exist yet - nothing to clear")
    exit(0)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Show current users
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    print(f"Current users in database: {count}")
    
    # Clear all users
    cursor.execute("DELETE FROM users")
    conn.commit()
    
    print("✓ All user data cleared from SQLite")
    print("✓ Ready for fresh signup test!")
    
    conn.close()
except Exception as e:
    print(f"Error: {str(e)}")
    print("Note: Database might not have users table yet - that's fine")
