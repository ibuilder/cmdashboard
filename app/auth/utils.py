def hash_password(password):
    from werkzeug.security import generate_password_hash
    return generate_password_hash(password)

def check_password(hashed_password, password):
    from werkzeug.security import check_password_hash
    return check_password_hash(hashed_password, password)

def generate_token(user_id):
    import jwt
    from datetime import datetime, timedelta
    secret_key = "your_secret_key"  # Replace with your actual secret key
    expiration = datetime.utcnow() + timedelta(days=1)
    token = jwt.encode({'user_id': user_id, 'exp': expiration}, secret_key, algorithm='HS256')
    return token

def decode_token(token):
    import jwt
    secret_key = "your_secret_key"  # Replace with your actual secret key
    try:
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload['user_id']
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None