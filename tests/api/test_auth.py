import json
import pytest
from app.models.user import User
from app.models.project import Project
from app import db
from app.auth.utils import generate_token


def test_token_auth_login_success(client, auth_user):
    """Test successful login with correct credentials."""
    response = client.post('/api/auth/token', json={
        'email': auth_user.email,
        'password': 'password'
    })
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'token' in data['data']


def test_token_auth_login_incorrect_password(client, auth_user):
    """Test failed login with incorrect password."""
    response = client.post('/api/auth/token', json={
        'email': auth_user.email,
        'password': 'wrong_password'
    })
    assert response.status_code == 401
    assert json.loads(response.data) == {'status': 'error', 'message': 'Invalid password'}


def test_token_auth_login_user_not_found(client):
    """Test failed login with non-existent user."""
    response = client.post('/api/auth/token', json={
        'email': 'nonexistent@example.com',
        'password': 'password'
    })
    assert response.status_code == 401
    assert json.loads(response.data) == {'status': 'error', 'message': 'User not found'}


def test_token_auth_valid_token_access(client, auth_user):
    """Test accessing a protected endpoint with a valid token."""
    token = generate_token(auth_user.id)
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == 200


def test_token_auth_invalid_token_access(client):
    """Test accessing a protected endpoint with an invalid token."""
    headers = {'Authorization': 'Bearer invalid_token'}
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == 401
    assert json.loads(response.data) == {'status': 'error', 'message': 'Token validation failed'}


def test_token_auth_expired_token_access(client, auth_user):
    """Test accessing a protected endpoint with an expired token."""
    
    from datetime import datetime, timedelta
    import jwt

    payload = {
        'user_id': auth_user.id,
        'exp': datetime.utcnow() - timedelta(minutes=1)
    }
    
    token = jwt.encode(payload, 'your_secret_key', algorithm='HS256')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects', headers=headers)
    assert response.status_code == 401
    assert json.loads(response.data) == {'status': 'error', 'message': 'Token validation failed'}

def test_token_auth_login_missing_email(client):
    """Test failed login with missing email."""
    response = client.post('/api/auth/token', json={'password': 'password'})
    assert response.status_code == 400

def test_token_auth_login_missing_password(client, auth_user):
    """Test failed login with missing password."""
    response = client.post('/api/auth/token', json={'email': auth_user.email})
    assert response.status_code == 400

def test_token_auth_login_empty_credentials(client):
    """Test failed login with empty credentials."""
    response = client.post('/api/auth/token', json={})
    assert response.status_code == 400
    
