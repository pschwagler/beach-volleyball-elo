#!/usr/bin/env python3
"""
Migration script to add users and verification_codes tables.
Run this script to update an existing database to support user authentication.
"""

import sqlite3
from pathlib import Path

# Database file location
DB_PATH = Path(__file__).parent / "volleyball.db"


def migrate():
    """Run the migration to add users and verification_codes tables."""
    print(f"Migrating database at {DB_PATH}...")
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Check if users table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='users'"
        )
        users_exists = cursor.fetchone() is not None
        
        if not users_exists:
            print("Creating users table...")
            cursor.execute("""
                CREATE TABLE users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    password_hash TEXT,
                    name TEXT,
                    email TEXT,
                    is_verified INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute(
                "CREATE INDEX idx_users_phone ON users(phone_number)"
            )
            cursor.execute(
                "CREATE INDEX idx_users_phone_verified ON users(phone_number, is_verified)"
            )
            print("✓ Users table created")
        else:
            print("✓ Users table already exists")
        
        # Check if verification_codes table already exists
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='verification_codes'"
        )
        verification_codes_exists = cursor.fetchone() is not None
        
        if not verification_codes_exists:
            print("Creating verification_codes table...")
            cursor.execute("""
                CREATE TABLE verification_codes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    phone_number TEXT NOT NULL,
                    code TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    used INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes
            cursor.execute(
                "CREATE INDEX idx_verification_codes_phone ON verification_codes(phone_number)"
            )
            cursor.execute(
                "CREATE INDEX idx_verification_codes_expires ON verification_codes(expires_at)"
            )
            print("✓ Verification codes table created")
        else:
            print("✓ Verification codes table already exists")
        
        conn.commit()
        print("\n✅ Migration completed successfully!")
        
    except Exception as e:
        conn.rollback()
        print(f"\n❌ Migration failed: {e}")
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    migrate()


