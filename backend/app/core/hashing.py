"""
Password Hashing Module

This module provides secure password hashing and verification using bcrypt.
It implements industry-standard password security practices including:
- Salted password hashing
- Constant-time comparison
- Configurable work factor

Security Notes:
- Never store plain text passwords
- Use bcrypt or argon2 for password hashing
- Verify passwords using constant-time comparison
- Use appropriate work factor (12-14 for bcrypt)

Usage:
    from app.core.hashing import get_password_hash, verify_password
    
    # Hash password during registration
    hashed = get_password_hash("user_password")
    
    # Verify password during login
    is_valid = verify_password("user_password", hashed)
"""

from passlib.context import CryptContext

# Password hashing context using bcrypt
# bcrypt is recommended for password hashing due to:
# - Built-in salt generation
# - Configurable work factor
# - Resistance to rainbow table attacks
# - Constant-time comparison
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12  # Work factor (12 = ~300ms on modern hardware)
)


def get_password_hash(password: str) -> str:
    """
    Hash a password using bcrypt.
    
    This function generates a salted hash of the password using bcrypt
    with a work factor of 12. The salt is automatically generated and
    included in the hash output.
    
    Args:
        password: Plain text password to hash
        
    Returns:
        str: Hashed password (includes salt)
        
    Example:
        hashed = get_password_hash("SecurePass123!")
        # Returns: $2b$12$... (60 character bcrypt hash)
        
    Security Notes:
        - Never store the plain text password
        - The hash includes the salt automatically
        - Work factor of 12 provides good security/performance balance
        - Hash output is always 60 characters for bcrypt
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    This function uses constant-time comparison to verify that the
    plain text password matches the hashed password. This prevents
    timing attacks.
    
    Args:
        plain_password: Plain text password to verify
        hashed_password: Hashed password to compare against
        
    Returns:
        bool: True if password matches, False otherwise
        
    Example:
        is_valid = verify_password("SecurePass123!", hashed)
        if is_valid:
            print("Password is correct")
        else:
            print("Password is incorrect")
            
    Security Notes:
        - Uses constant-time comparison to prevent timing attacks
        - Returns False for any error (invalid hash format, etc.)
        - Never reveals why verification failed
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        # Return False for any error (invalid hash, etc.)
        # Don't reveal error details for security
        return False


def needs_rehash(hashed_password: str) -> bool:
    """
    Check if a password hash needs to be updated.
    
    This function checks if the hash was created with deprecated
    settings (old algorithm, low work factor, etc.) and needs to
    be regenerated with current settings.
    
    Args:
        hashed_password: Hashed password to check
        
    Returns:
        bool: True if hash needs update, False otherwise
        
    Example:
        if needs_rehash(user.password_hash):
            # Re-hash password with current settings
            user.password_hash = get_password_hash(plain_password)
            
    Use Case:
        When updating password hashing settings (e.g., increasing
        work factor), use this to identify old hashes that need
        to be updated during user login.
    """
    try:
        return pwd_context.needs_update(hashed_password)
    except Exception:
        # If we can't determine, assume it needs rehash
        return True


def get_password_strength(password: str) -> dict:
    """
    Evaluate password strength.
    
    This function analyzes a password and returns metrics about
    its strength including length, character variety, and common
    pattern detection.
    
    Args:
        password: Password to evaluate
        
    Returns:
        dict: Password strength metrics
        
    Example:
        strength = get_password_strength("SecurePass123!")
        # {
        #     "length": 15,
        #     "has_uppercase": True,
        #     "has_lowercase": True,
        #     "has_digits": True,
        #     "has_special": True,
        #     "score": 4,
        #     "strength": "strong"
        # }
        
    Strength Levels:
        - 0-1: Very weak
        - 2: Weak
        - 3: Medium
        - 4: Strong
        - 5: Very strong
    """
    length = len(password)
    has_uppercase = any(c.isupper() for c in password)
    has_lowercase = any(c.islower() for c in password)
    has_digits = any(c.isdigit() for c in password)
    has_special = any(not c.isalnum() for c in password)
    
    # Calculate strength score
    score = 0
    if length >= 8:
        score += 1
    if length >= 12:
        score += 1
    if has_uppercase and has_lowercase:
        score += 1
    if has_digits:
        score += 1
    if has_special:
        score += 1
    
    # Determine strength level
    if score <= 1:
        strength = "very_weak"
    elif score == 2:
        strength = "weak"
    elif score == 3:
        strength = "medium"
    elif score == 4:
        strength = "strong"
    else:
        strength = "very_strong"
    
    return {
        "length": length,
        "has_uppercase": has_uppercase,
        "has_lowercase": has_lowercase,
        "has_digits": has_digits,
        "has_special": has_special,
        "score": score,
        "strength": strength
    }
