from flask import abort
from functools import wraps

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Simulating user roles for demonstration
            user_roles = ['admin']  # Replace this with your actual user role logic

            if not any(role in user_roles for role in roles):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator