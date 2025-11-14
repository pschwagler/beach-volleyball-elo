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
                          failed_verification_attempts, locked_until,
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
                          failed_verification_attempts, locked_until,
                          created_at, updated_at
                   FROM users 
                   WHERE phone_number = ?
                   ORDER BY is_verified DESC, created_at DESC
                   LIMIT 1""",
                (phone_number,)
            )
        
        row = cursor.fetchone()
        if row:
            row_dict = dict(row)
            return {
                "id": row_dict["id"],
                "phone_number": row_dict["phone_number"],
                "password_hash": row_dict["password_hash"],
                "name": row_dict["name"],
                "email": row_dict["email"],
                "is_verified": bool(row_dict["is_verified"]),
                "failed_verification_attempts": row_dict.get("failed_verification_attempts", 0) or 0,
                "locked_until": row_dict.get("locked_until"),
                "created_at": row_dict["created_at"],
                "updated_at": row_dict["updated_at"]
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
                      failed_verification_attempts, locked_until,
                      created_at, updated_at
               FROM users 
               WHERE id = ?""",
            (user_id,)
        )
        
        row = cursor.fetchone()
        if row:
            row_dict = dict(row)
            return {
                "id": row_dict["id"],
                "phone_number": row_dict["phone_number"],
                "password_hash": row_dict["password_hash"],
                "name": row_dict["name"],
                "email": row_dict["email"],
                "is_verified": bool(row_dict["is_verified"]),
                "failed_verification_attempts": row_dict.get("failed_verification_attempts", 0) or 0,
                "locked_until": row_dict.get("locked_until"),
                "created_at": row_dict["created_at"],
                "updated_at": row_dict["updated_at"]
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
    
    Ensures only one active code exists per phone number by deleting
    any existing unused codes before creating a new one.
    
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
            # Delete any existing unused codes for this phone (ensures only 1 active code)
            conn.execute(
                "DELETE FROM verification_codes WHERE phone_number = ? AND used = 0",
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


def verify_and_mark_code_used(phone_number: str, code: str) -> bool:
    """
    Atomically verify a code and mark it as used.
    
    This prevents race conditions where the same code could be verified twice.
    Only marks as used if the code is valid and not expired.
    
    Args:
        phone_number: Phone number in E.164 format
        code: Verification code
        
    Returns:
        True if code was valid and marked as used, False otherwise
    """
    with db.get_db() as conn:
        # Atomically verify and mark as used in one operation
        # Only updates if code matches, is unused, and not expired
        cursor = conn.execute(
            """UPDATE verification_codes
               SET used = 1
               WHERE phone_number = ? 
                 AND code = ? 
                 AND used = 0
                 AND expires_at > datetime('now')""",
            (phone_number, code)
        )
        return cursor.rowcount > 0


# Account locking configuration
MAX_FAILED_ATTEMPTS = 5
LOCK_DURATION_MINUTES = 15


def is_account_locked(user: Dict) -> bool:
    """
    Check if a user account is currently locked.
    
    Args:
        user: User dictionary with locked_until field
        
    Returns:
        True if account is locked, False otherwise
    """
    if not user.get("locked_until"):
        return False
    
    locked_until = datetime.fromisoformat(user["locked_until"])
    if datetime.utcnow() < locked_until:
        return True
    
    # Lock has expired, clear it
    clear_account_lock(user["id"])
    return False


def increment_failed_attempts(phone_number: str) -> bool:
    """
    Increment failed verification attempts for a user.
    Locks the account if MAX_FAILED_ATTEMPTS is reached.
    
    Args:
        phone_number: Phone number in E.164 format
        
    Returns:
        True if account was locked, False otherwise
    """
    with db.get_db() as conn:
        # Get current attempts
        cursor = conn.execute(
            """SELECT id, failed_verification_attempts
               FROM users
               WHERE phone_number = ?
               ORDER BY is_verified DESC, created_at DESC
               LIMIT 1""",
            (phone_number,)
        )
        row = cursor.fetchone()
        if not row:
            return False

        row_dict = dict(row)
        user_id = row_dict["id"]
        current_attempts = row_dict.get("failed_verification_attempts", 0) or 0
        new_attempts = current_attempts + 1
        
        # Update attempts
        if new_attempts >= MAX_FAILED_ATTEMPTS:
            # Lock the account
            locked_until = datetime.utcnow() + timedelta(minutes=LOCK_DURATION_MINUTES)
            locked_until_str = locked_until.isoformat()
            conn.execute(
                """UPDATE users
                   SET failed_verification_attempts = ?,
                       locked_until = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (new_attempts, locked_until_str, user_id)
            )
            logger.warning(f"Account locked for phone {phone_number} after {new_attempts} failed attempts")
            return True
        else:
            # Just increment attempts
            conn.execute(
                """UPDATE users
                   SET failed_verification_attempts = ?,
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (new_attempts, user_id)
            )
            return False


def reset_failed_attempts(user_id: int):
    """
    Reset failed verification attempts for a user (on successful verification).
    
    Args:
        user_id: User ID
    """
    with db.get_db() as conn:
        conn.execute(
            """UPDATE users
               SET failed_verification_attempts = 0,
                   locked_until = NULL,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ?""",
            (user_id,)
        )


def clear_account_lock(user_id: int):
    """
    Clear an expired account lock.
    
    Args:
        user_id: User ID
    """
    with db.get_db() as conn:
        conn.execute(
            """UPDATE users
               SET locked_until = NULL,
                   updated_at = CURRENT_TIMESTAMP
               WHERE id = ? AND locked_until < datetime('now')""",
            (user_id,)
        )


# Refresh token functions

def create_refresh_token(user_id: int, token: str, expires_at: datetime) -> bool:
    """
    Create a refresh token record.
    
    Args:
        user_id: User ID
        token: Refresh token string
        expires_at: Expiration datetime
        
    Returns:
        True if successful, False otherwise
    """
    try:
        expires_at_str = expires_at.isoformat()
        with db.get_db() as conn:
            # Delete old refresh tokens for this user (single active token per user)
            conn.execute(
                "DELETE FROM refresh_tokens WHERE user_id = ?",
                (user_id,)
            )
            
            # Create new refresh token
            conn.execute(
                """INSERT INTO refresh_tokens (user_id, token, expires_at)
                   VALUES (?, ?, ?)""",
                (user_id, token, expires_at_str)
            )
            return True
    except Exception as e:
        logger.error(f"Error creating refresh token: {str(e)}")
        return False


def get_refresh_token(token: str) -> Optional[Dict]:
    """
    Get refresh token record by token string.
    
    Args:
        token: Refresh token string
        
    Returns:
        Refresh token dictionary with user_id and expires_at, or None if not found
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            """SELECT id, user_id, token, expires_at, created_at
               FROM refresh_tokens
               WHERE token = ?""",
            (token,)
        )
        row = cursor.fetchone()
        if row:
            return {
                "id": row["id"],
                "user_id": row["user_id"],
                "token": row["token"],
                "expires_at": row["expires_at"],
                "created_at": row["created_at"]
            }
        return None


def delete_refresh_token(token: str) -> bool:
    """
    Delete a refresh token (on logout or token rotation).
    
    Args:
        token: Refresh token string
        
    Returns:
        True if token was deleted, False otherwise
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM refresh_tokens WHERE token = ?",
            (token,)
        )
        return cursor.rowcount > 0


def delete_user_refresh_tokens(user_id: int) -> int:
    """
    Delete all refresh tokens for a user.
    
    Args:
        user_id: User ID
        
    Returns:
        Number of tokens deleted
    """
    with db.get_db() as conn:
        cursor = conn.execute(
            "DELETE FROM refresh_tokens WHERE user_id = ?",
            (user_id,)
        )
        return cursor.rowcount


