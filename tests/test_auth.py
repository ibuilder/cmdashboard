from app import create_app, db
from app.models.user import User
import pytest

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_register(client):
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'testpassword',
        'role': 'user'
    })
    assert response.status_code == 200
    assert b'Registration successful' in response.data

def test_login(client):
    client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'testpassword',
        'role': 'user'
    })
    response = client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    assert response.status_code == 200
    assert b'Login successful' in response.data

def test_login_fail(client):
    response = client.post('/auth/login', data={
        'username': 'wronguser',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_logout(client):
    client.post('/auth/register', data={
        'username': 'testuser',
        'password': 'testpassword',
        'role': 'user'
    })
    client.post('/auth/login', data={
        'username': 'testuser',
        'password': 'testpassword'
    })
    response = client.get('/auth/logout')
    assert response.status_code == 200
    assert b'Logout successful' in response.data