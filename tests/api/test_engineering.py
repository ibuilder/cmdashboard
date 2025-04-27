import pytest
from app import create_app
from app.models.user import User
from app.models.engineering import RFI, Submittal
from app import db

@pytest.fixture
def app():
    app = create_app(test_config=True)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def user(app):
    with app.app_context():
        user = User(email='test@example.com', password='password', name='Test User', role='Admin')
        db.session.add(user)
        db.session.commit()
        yield user

@pytest.fixture
def token(client, user):
    response = client.post('/api/auth/token', json={'email': 'test@example.com', 'password': 'password'})
    return response.get_json()['token']

@pytest.fixture
def rfi(app, user):
    with app.app_context():
        rfi = RFI(number='RFI-001', subject='Test RFI', status='Open', project_id=1, submitted_by=user.id)
        db.session.add(rfi)
        db.session.commit()
        yield rfi

@pytest.fixture
def submittal(app, user):
    with app.app_context():
        submittal = Submittal(number='SUB-001', title='Test Submittal', status='Submitted', project_id=1, submitted_by=user.id)
        db.session.add(submittal)
        db.session.commit()
        yield submittal

def test_get_rfis_for_project(client, token, rfi):
    headers = {'Authorization': 'Bearer ' + token}
    response = client.get('/api/projects/1/rfis', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['number'] == 'RFI-001'

def test_get_rfis_for_project_unauthorized(client):
    response = client.get('/api/projects/1/rfis')
    assert response.status_code == 401

def test_get_submittals_for_project(client, token, submittal):
    headers = {'Authorization': 'Bearer ' + token}
    response = client.get('/api/projects/1/submittals', headers=headers)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) == 1
    assert data['data'][0]['number'] == 'SUB-001'

def test_get_submittals_for_project_unauthorized(client):
    response = client.get('/api/projects/1/submittals')
    assert response.status_code == 401

def test_get_rfis_for_nonexistent_project(client, token):
    headers = {'Authorization': 'Bearer ' + token}
    response = client.get('/api/projects/999/rfis', headers=headers)
    assert response.status_code == 404

def test_get_submittals_for_nonexistent_project(client, token):
    headers = {'Authorization': 'Bearer ' + token}
    response = client.get('/api/projects/999/submittals', headers=headers)
    assert response.status_code == 404