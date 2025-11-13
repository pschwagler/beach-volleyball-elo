"""
User service layer for user and verification code database operations.
"""

from typing import Optional, Dict
from datetime import datetime, timedelta
from backend.database import db
import logging

logger = logging.getLogger(__name__)

# Verification code expiration (in minutes)
VERIFICATION_CODE_EXPIRATION_MINUTES = 10


def create_user(
    phone_number: str,
    password_hash: Optional[str] = None,
    name: Optional[str] = None,
    email: Optional[str] = None
) -> int:
    """
    Create a new user account.
    
    Checks if a verified user with the phone number already exists.
    Optionally cleans up old unverified accounts with the same phone.
    
    Args:
        phone_number: Phone number in E.164 format
        password_hash: Optional hashed password
        name: Optional user name
        email: Optional user email
        
    Returns:
        User ID of the created user
        
    Raises:
        ValueError: If a verified user with this phone number already exists
    """
    with db.get_db() as conn:
        # Check if verified user already exists
        cursor = conn.execute(
            "SELECT id FROM users WHERE phone_number = ? AND is_verified = 1",
            (phone_number,)
        )
        if cursor.fetchone():
            raise ValueError(f"Phone number {phone_number} is already registered and verified")
        
        # Clean up old unverified accounts with same phone
        conn.execute(
            "DELETE FROM users WHERE phone_number = ? AND is_verified = 0",
            (phone_number,)
        )
        
        # Create new user
        cursor = conn.execute(
            """INSERT INTO users (phone_number, password_hash, name, email, is_verified)
               VALUES (?, ?, ?, ?, 0)""",
            (phone_number, password_hash, name, email)
        )
        
        return cursor.lastrowid


def get_user_by_phone(phone_number: str, verified_only: bool = False) -> Optional[Dict]:
    """
    Get user by phone number.
    
    Args:
        phone_number: Phone number in E.164 format
        verified_only: If True, only return verified users
        
    Returns:
        User dictionary or None if not found
    """
    with db.get_db() as conn:
        if verified_only:
            cursor = conn.execute(
                """SELECT id, phone_number, password_hash, name, email, is_verified, 
                          created_at, updated_at
                   FROM users 
                   WHERE phone_number = ? AND is_verified = 1
                   ORDER BY created_at DESC
                   LIMIT 1""",
                (phone_number,)
            )
        else:
            cursor = conn.execute(
                """SELECT id, phone_number, password_hash, name, email, is_verified, 
                          created_at, updated_at
                   FROM users 
                   WHERE phone_number = ?
                   ORDER BY is_verified DESC, created_at DESC
                   LIMIT 1""",
                (phone_number,)
            )
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "phone_number": row["phone_number"],
                "password_hash": row["password_hash"],
                "name": row["name"],
                "email": row["email"],
                "is_verified": bool(row["is_verified"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None


def get_verified_user_by_phone(phone_number: str) -> Optional[Dict]:
    """
    Convenience method to get only verified user by phone number.
    
    Args:
        phone_number: Phone number in E.164 format
        
    Returns:
        Verified user dictionary or None if not found
    """
    return get_user_by_phone(phone_number, verified_only=True)


def get_user_by_id(user_id: int) -> Optional[Dict]:
    """
    Get user by ID.
    
    Args:
        user_id: User ID
        
    Returns:
        User dictionary or None if not found
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            """SELECT id, phone_number, password_hash, name, email, is_verified, 
                      created_at, updated_at
               FROM users 
               WHERE id = ?""",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "phone_number": row["phone_number"],
                "password_hash": row["password_hash"],
                "name": row["name"],
                "email": row["email"],
                "is_verified": bool(row["is_verified"]),
                "created_at": row["created_at"],
                "updated_at": row["updated_at"]
            }
        return None


def verify_user_phone(user_id: int, phone_number: str) -> bool:
    """
    Verify a user's phone number.
    
    Marks the user as verified and deletes any other unverified accounts
    with the same phone number. Enforces uniqueness for verified users.
    
    Args:
        user_id: User ID to verify
        phone_number: Phone number (for validation)
        
    Returns:
        True if successful, False otherwise
        
    Raises:
        ValueError: If another verified user with this phone already exists
    """
    with db.get_db() as conn:
        # Check if another verified user with this phone exists
        cursor = conn.execute(
            "SELECT id FROM users WHERE phone_number = ? AND is_verified = 1 AND id != ?",
            (phone_number, user_id)
        )
        if cursor.fetchone():
            raise ValueError(f"Phone number {phone_number} is already verified for another user")
        
        # Delete other unverified accounts with same phone
        conn.execute(
            "DELETE FROM users WHERE phone_number = ? AND is_verified = 0 AND id != ?",
            (phone_number, user_id)
        )
        
        # Mark user as verified
        cursor = conn.execute(
            """UPDATE users 
               SET is_verified = 1, updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND phone_number = ?""",
            (user_id, phone_number)
        )
        
        return cursor.rowcount > 0


def check_phone_exists(phone_number: str, verified_only: bool = False) -> bool:
    """
    Check if a phone number exists in the system.
    
    Args:
        phone_number: Phone number in E.164 format
        verified_only: If True, only check verified users
        
    Returns:
        True if phone exists, False otherwise
    """
    user = get_user_by_phone(phone_number, verified_only=verified_only)
    return user is not None


def delete_unverified_users(phone_number: str) -> int:
    """
    Delete all unverified users with the given phone number.
    
    Args:
        phone_number: Phone number in E.164 format
        
    Returns:
        Number of users deleted
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM users WHERE phone_number = ? AND is_verified = 0",
            (phone_number,)
        )
        return cursor.rowcount


def create_verification_code(phone_number: str, code: str, expires_in_minutes: int = VERIFICATION_CODE_EXPIRATION_MINUTES) -> bool:
    """
    Create a verification code record.
    
    Args:
        phone_number: Phone number in E.164 format
        code: Verification code
        expires_in_minutes: Expiration time in minutes (default 10)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        expires_at = datetime.utcnow() + timedelta(minutes=expires_in_minutes)
        expires_at_str = expires_at.isoformat()
        
        with db.get_db() as conn:
            # Invalidate any existing unused codes for this phone
            conn.execute(
                "UPDATE verification_codes SET used = 1 WHERE phone_number = ? AND used = 0",
                (phone_number,)
            )
            
            # Create new code
            conn.execute(
                """INSERT INTO verification_codes (phone_number, code, expires_at, used)
                   VALUES (?, ?, ?, 0)""",
                (phone_number, code, expires_at_str)
            )
            
            return True
    except Exception as e:
        logger.error(f"Error creating verification code: {str(e)}")
        return False


def verify_code(phone_number: str, code: str) -> bool:
    """
    Verify a code for a phone number.
    
    Checks if the code exists, is not expired, and hasn't been used.
    
    Args:
        phone_number: Phone number in E.164 format
        code: Verification code
        
    Returns:
        True if code is valid, False otherwise
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            """SELECT id, expires_at, used
               FROM verification_codes
               WHERE phone_number = ? AND code = ? AND used = 0
               ORDER BY created_at DESC
               LIMIT 1""",
            (phone_number, code)
        )
        
        row = cursor.fetchone()
        if not row:
            return False
        
        # Check expiration
        expires_at = datetime.fromisoformat(row["expires_at"])
        if datetime.utcnow() > expires_at:
            return False
        
        return True


def mark_code_used(phone_number: str, code: str) -> bool:
    """
    Mark a verification code as used.
    
    Args:
        phone_number: Phone number in E.164 format
        code: Verification code
        
    Returns:
        True if code was marked as used, False otherwise
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            """UPDATE verification_codes
               SET used = 1
               WHERE phone_number = ? AND code = ? AND used = 0""",
            (phone_number, code)
        )
        return cursor.rowcount > 0


