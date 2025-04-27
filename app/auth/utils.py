from app import db
from app.models.user import User
from werkzeug.security import generate_password_hash


def create_user(username, password, email=None, role="user"):
    """Creates a new user in the database.

    Args:
        username (str): The username of the new user.
        password (str): The password of the new user.
        email (str, optional): The email of the new user. Defaults to None.
        role (str, optional): The role of the user. Defaults to "user".

    Returns:
        User: The newly created User object.
    """
    user = User(username=username, email=email, password_hash=generate_password_hash(password), role=role)
    db.session.add(user)
    db.session.commit()
    return user