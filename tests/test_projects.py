import pytest
from app import create_app, db
from app.models.project import Project

@pytest.fixture
def client():
    app = create_app('testing')
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()

def test_create_project(client):
    response = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'This is a test project.'
    })
    assert response.status_code == 201
    assert response.json['name'] == 'Test Project'

def test_get_projects(client):
    client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'This is a test project.'
    })
    response = client.get('/api/projects')
    assert response.status_code == 200
    assert len(response.json) > 0

def test_update_project(client):
    response = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'This is a test project.'
    })
    project_id = response.json['id']
    response = client.put(f'/api/projects/{project_id}', json={
        'name': 'Updated Project',
        'description': 'This is an updated test project.'
    })
    assert response.status_code == 200
    assert response.json['name'] == 'Updated Project'

def test_delete_project(client):
    response = client.post('/api/projects', json={
        'name': 'Test Project',
        'description': 'This is a test project.'
    })
    project_id = response.json['id']
    response = client.delete(f'/api/projects/{project_id}')
    assert response.status_code == 204

    response = client.get(f'/api/projects/{project_id}')
    assert response.status_code == 404