import uuid
import os
import jwt
import logging
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)

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

def generate_token(user_id: int, expires_delta: timedelta = timedelta(days=1)) -> str:
    """
    Generate a JWT (JSON Web Token) for a given user ID with a specified expiration time.

    Args:
        user_id (int): The ID of the user for whom the token is being generated.
        expires_delta (timedelta, optional): The time delta representing the token's expiration period. 
                                             Defaults to 1 day.

    Returns:
        str: The encoded JWT token.

    Raises:
        ValueError: If the SECRET_KEY environment variable is not set.
    """
    secret_key = os.environ.get("SECRET_KEY")  # Retrieve the secret key from environment variables
    if not secret_key:
        logger.error("SECRET_KEY environment variable is not set.")
        raise ValueError("SECRET_KEY environment variable is not set.")

    expiration = datetime.utcnow() + expires_delta # Calculate the token's expiration time
    token = jwt.encode({"user_id": user_id, "exp": expiration}, secret_key, algorithm="HS256")  # Encode the token
    return token  # Return the encoded token

def decode_token(token: str) -> int | None:
    """
    Decode a JWT token and return the user ID, or None if the token is invalid or expired.
    """
    secret_key = os.environ.get("SECRET_KEY")  # Retrieve the secret key from environment variables
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])  # Decode the token
        return payload["user_id"]  # Return the user ID from the payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        logger.warning(f"Invalid or expired token: {token}")
        return None
