from app import db
from app.models.user import User
from flask import current_app


def create_user(username, password, email=None, is_admin=False, full_name=None):
    """
    Create a new user in the database.

    :param username: The username of the new user.
    :param password: The password of the new user.
    :param email: The email of the new user (optional).
    :param is_admin: Whether the user is an admin (default: False).
    :return: The newly created User object.
    """
    user = User(username=username, email=email, is_admin=is_admin)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user