import uuid
import os
import jwt
import subprocess
import logging
from datetime import datetime, timedelta
from sqlalchemy import text
from app import db
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

def perform_database_maintenance():
    """
    Performs database maintenance tasks such as cleaning up old data.
    """
    logger.info("Performing database maintenance...")
    try:
        # Example: Delete old logs from the 'logs' table
        with db.engine.connect() as connection:
          connection.execute(text("DELETE FROM logs WHERE timestamp < :old_date"), {"old_date": datetime.now() - timedelta(days=30)})
          connection.commit()
        logger.info("Old data removed.")
    except Exception as e:
        logger.error(f"Error during database maintenance: {e}")



def check_dependencies_updates():
    """
    Checks for available updates to the project's dependencies.

    Returns:
        str: A string containing the output of the pip list command 
             with outdated packages, or an error message if the command fails.
    """
    logger.info("Checking for dependencies updates...")
    try:
        result = subprocess.run(['pip', 'list', '--outdated'], capture_output=True, text=True, check=True)
        logger.info("Dependencies updates checked.")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Error checking for dependency updates: {e}")
        return f"Error checking for dependency updates: {e}"

def update_dependencies():
    """
    Updates the project's dependencies to their latest versions.
    """
    logger.info("Updating dependencies...")
    try:
        subprocess.run(['pip', 'install', '--upgrade', '-r', 'requirements.txt'], check=True)
        logger.info("Dependencies updated.")
    except subprocess.CalledProcessError as e:
        logger.error(f"Error updating dependencies: {e}")
