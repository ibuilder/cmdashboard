import uuid
import os
import jwt
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

def generate_request_id():
    """Generate a unique request ID."""
    return str(uuid.uuid4())

def hash_password(password):
    """
    Hash a password using Werkzeug's generate_password_hash.
    
    Args:
        password (str): The password to hash.

    Returns:
        str: The hashed password.
    """
    return generate_password_hash(password)

def check_password(hashed_password, password):
    """
    Check if a password matches a hashed password using Werkzeug's check_password_hash.
    
    Args:
        hashed_password (str): The hashed password.
        password (str): The password to check.

    Returns:
        bool: True if the password matches, False otherwise.
    """
    return check_password_hash(hashed_password, password)

def generate_token(user_id):
    """Generate a JWT token for a given user ID with a 1-day expiration."""
    secret_key = os.environ.get("SECRET_KEY")
    expiration = datetime.utcnow() + timedelta(days=1)
    token = jwt.encode({"user_id": user_id, "exp": expiration}, secret_key, algorithm="HS256")
    return token

def decode_token(token):
    """Decode a JWT token and return the user ID, or None if the token is invalid."""
    secret_key = os.environ.get("SECRET_KEY")
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
        return payload["user_id"]
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None