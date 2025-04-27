import pytest
from app import create_app, db
from app.models.field import DailyReport
from app.models.project import Project
from app.models.user import User
from tests.utils import create_user, login, create_project, create_daily_report

@pytest.fixture(scope='module')
def test_client():
    app = create_app('testing')
    with app.test_client() as testing_client:
        with app.app_context():
            yield testing_client

@pytest.fixture(scope='module')
def init_database():
    db.create_all()
    yield db
    db.drop_all()

def test_get_daily_reports_for_project(test_client, init_database):
    """Test getting daily reports for a project."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')
    project = create_project(init_database, "Test Project", "1234", "Active")
    daily_report = create_daily_report(init_database, project.id)

    response = test_client.get(f'/api/projects/{project.id}/daily-reports', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert len(response.json['data']) == 1
    assert response.json['data'][0]['report_number'] == daily_report.report_number

def test_get_daily_reports_for_project_unauthorized(test_client, init_database):
    """Test getting daily reports for a project without a token."""
    project = create_project(init_database, "Test Project", "1234", "Active")
    response = test_client.get(f'/api/projects/{project.id}/daily-reports')
    assert response.status_code == 401

def test_get_daily_reports_for_project_not_found(test_client, init_database):
    """Test getting daily reports for a non-existent project."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')

    response = test_client.get(f'/api/projects/999/daily-reports', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404

def test_create_daily_report(test_client, init_database):
    """Test creating a new daily report."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')
    project = create_project(init_database, "Test Project", "1234", "Active")

    daily_report_data = {
        'project_id': project.id,
        'weather_conditions': 'Sunny',
        'temperature_high': 80,
        'temperature_low': 60,
        'manpower_count': 5,
        'delays': False,
        'work_performed': 'Excavation'
    }
    response = test_client.post('/api/daily-reports/create', json=daily_report_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['status'] == 'success'

def test_create_daily_report_unauthorized(test_client, init_database):
    """Test creating a new daily report without a token."""
    project = create_project(init_database, "Test Project", "1234", "Active")
    daily_report_data = {
        'project_id': project.id,
        'weather_conditions': 'Sunny',
        'temperature_high': 80,
        'temperature_low': 60,
        'manpower_count': 5,
        'delays': False,
        'work_performed': 'Excavation'
    }
    response = test_client.post('/api/daily-reports/create', json=daily_report_data)
    assert response.status_code == 401

def test_create_daily_report_bad_request(test_client, init_database):
    """Test creating a new daily report with bad data."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')

    daily_report_data = {}
    response = test_client.post('/api/daily-reports/create', json=daily_report_data, headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 400

def test_get_daily_report_by_id(test_client, init_database):
    """Test getting a daily report by its ID."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')
    project = create_project(init_database, "Test Project", "1234", "Active")
    daily_report = create_daily_report(init_database, project.id)

    response = test_client.get(f'/api/daily-reports/{daily_report.id}', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 200
    assert response.json['data']['id'] == daily_report.id

def test_get_daily_report_by_id_unauthorized(test_client, init_database):
    """Test getting a daily report by its ID without a token."""
    project = create_project(init_database, "Test Project", "1234", "Active")
    daily_report = create_daily_report(init_database, project.id)

    response = test_client.get(f'/api/daily-reports/{daily_report.id}')
    assert response.status_code == 401

def test_get_daily_report_by_id_not_found(test_client, init_database):
    """Test getting a non-existent daily report by its ID."""
    user = create_user(init_database, 'testuser', 'testuser@example.com', 'password', 'Admin')
    token = login(test_client, 'testuser@example.com', 'password')

    response = test_client.get('/api/daily-reports/999', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == 404