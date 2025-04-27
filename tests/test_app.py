import pytest
from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.project import Project
from app.models.field import DailyReport
from app.auth.utils import generate_token
import json
from datetime import datetime, timedelta
import tempfile
import os
from werkzeug.security import generate_password_hash

@pytest.fixture(scope='module')
def test_client():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use an in-memory database
    with app.test_client() as testing_client:
        with app.app_context():
            db.create_all()
            yield testing_client
            db.session.remove()
            db.drop_all()

@pytest.fixture(scope='module')
def add_user(test_client):
    def _add_user(email, password, role):
        hashed_password = generate_password_hash(password)
        new_user = User(email=email, password_hash=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return new_user
    return _add_user

@pytest.fixture(scope='module')
def add_project(test_client):
    def _add_project(name, number, status, start_date=None, end_date=None):
        new_project = Project(name=name, number=number, status=status, start_date=start_date, end_date=end_date)
        db.session.add(new_project)
        db.session.commit()
        return new_project
    return _add_project

@pytest.fixture(scope='module')
def add_daily_report(test_client):
    def _add_daily_report(project, report_date, report_number, user):
        new_daily_report = DailyReport(project_id=project.id, report_date=report_date, report_number=report_number, created_by=user.id)
        db.session.add(new_daily_report)
        db.session.commit()
        return new_daily_report
    return _add_daily_report

def test_get_projects_unauthenticated(test_client):
    response = test_client.get('/api/projects')
    assert response.status_code == 401

def test_get_projects_authenticated(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}'}
    project = add_project('Test Project', 'TP-001', 'Active')
    response = test_client.get('/api/projects', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1
    assert data['data'][0]['name'] == 'Test Project'

def test_get_project_details_authenticated(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}'}
    project = add_project('Test Project', 'TP-001', 'Active')
    response = test_client.get(f'/api/projects/{project.id}', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['data']['name'] == 'Test Project'

def test_get_projects_normal_user(test_client, add_user, add_project):
    admin = add_user('admin@example.com', 'password', 'Admin')
    user = add_user('test@example.com', 'password', 'User')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}'}
    project = add_project('Test Project', 'TP-001', 'Active')
    project.users.append(user)
    db.session.commit()
    response = test_client.get('/api/projects', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['count'] == 1
    assert data['data'][0]['name'] == 'Test Project'

def test_get_project_details_unauthorized(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'User')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}'}
    project = add_project('Test Project', 'TP-001', 'Active')
    response = test_client.get(f'/api/projects/{project.id}', headers=headers)
    assert response.status_code == 403

def test_get_project_details_not_found(test_client, add_user):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}'}
    response = test_client.get('/api/projects/999', headers=headers)
    assert response.status_code == 404

def test_create_daily_report_invalid_data(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    project = add_project('Test Project', 'TP-001', 'Active')
    data = {}
    response = test_client.post('/api/daily-reports/create', headers=headers, data=json.dumps(data))
    assert response.status_code == 400

def test_create_daily_report_unauthorized(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'User')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    project = add_project('Test Project', 'TP-001', 'Active')
    data = {
        'project_id': project.id,
        'weather_condition': 'Sunny',
        'temperature_high': 85,
        'temperature_low': 65,
        'manpower_count': 10,
    }
    response = test_client.post('/api/daily-reports/create', headers=headers, data=json.dumps(data))
    assert response.status_code == 403

def test_create_daily_report_already_exists(test_client, add_user, add_project, add_daily_report):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    project = add_project('Test Project', 'TP-001', 'Active')
    add_daily_report(project, datetime.now(), 'DR-0001', user)
    data = {
        'project_id': project.id,
        'weather_condition': 'Sunny',
        'temperature_high': 85,
        'temperature_low': 65,
        'manpower_count': 10,
    }
    response = test_client.post('/api/daily-reports/create', headers=headers, data=json.dumps(data))
    assert response.status_code == 400

def test_create_daily_report_success(test_client, add_user, add_project):
    user = add_user('test@example.com', 'password', 'Admin')
    token = generate_token(user.id)
    headers = {'Authorization': f'Bearer {token}', 'Content-Type': 'application/json'}
    project = add_project('Test Project', 'TP-001', 'Active')
    data = {
        'project_id': project.id,
        'weather_condition': 'Sunny',
        'temperature_high': 85,
        'temperature_low': 65,
        'manpower_count': 10,
    }
    response = test_client.post('/api/daily-reports/create', headers=headers, data=json.dumps(data))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert 'report_id' in data