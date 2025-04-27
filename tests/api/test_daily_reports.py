import pytest
from app.models.user import User
from app.models.project import Project
from app.models.field import DailyReport
from app.extensions import db
from datetime import datetime
from flask import url_for

def test_get_daily_report_unauthorized(client, auth, test_project):
    """Test getting a daily report without authentication."""
    daily_report = DailyReport(project_id=test_project.id, report_date=datetime.now().date(), report_number="DR-0001", created_by=1)
    db.session.add(daily_report)
    db.session.flush()
    db.session.commit()

    response = client.get(url_for('api.get_daily_report', id=daily_report.id))
    assert response.status_code == 401

def test_get_daily_report_forbidden(client, auth, test_user, test_project):
    """Test getting a daily report with an unauthorized user."""
    auth.login()
    daily_report = DailyReport(project_id=test_project.id, report_date=datetime.now().date(), report_number="DR-0001", created_by=test_user.id)
    db.session.flush()
    db.session.add(daily_report)
    db.session.commit()

    response = client.get(url_for('api.get_daily_report', id=daily_report.id), headers=auth.get_auth_header())
    assert response.status_code == 403

def test_get_daily_report_not_found(client, auth, test_user, test_project):
    """Test getting a non-existent daily report."""
    auth.login()
    response = client.get(url_for('api.get_daily_report', id=999), headers=auth.get_auth_header())
    assert response.status_code == 404

def test_get_daily_report_success(client, auth, test_user, test_project):
    """Test successfully getting a daily report."""
    test_project.users.append(test_user)
    db.session.commit()
    auth.login(email = test_user.email)
    
    daily_report = DailyReport(project_id=test_project.id, report_date=datetime.now().date(), report_number="DR-0001", created_by=test_user.id)
    db.session.flush()
    db.session.add(daily_report)
    db.session.commit()

    response = client.get(url_for('api.get_daily_report', id=daily_report.id), headers=auth.get_auth_header())
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['data']['id'] == daily_report.id

def test_create_daily_report_unauthorized(client, test_project):
    """Test creating a daily report without authentication."""
    response = client.post(url_for('api.create_daily_report'), json={
        'project_id': test_project.id
    })
    assert response.status_code == 401

def test_create_daily_report_missing_project_id(client, auth):
    """Test creating a daily report with missing project ID."""
    auth.login()
    response = client.post(url_for('api.create_daily_report'), headers=auth.get_auth_header(), json={})
    assert response.status_code == 400
    assert response.json['message'] == 'Missing project_id'


def test_create_daily_report_forbidden(client, auth, test_user, test_project):
    """Test creating a daily report with an unauthorized user."""
    auth.login()
    response = client.post(url_for('api.create_daily_report'), headers=auth.get_auth_header(), json={
        'project_id': test_project.id
    })
    assert response.status_code == 403

def test_create_daily_report_already_exists(client, auth, test_user, test_project):
    """Test creating a daily report when one already exists for today."""
    test_project.users.append(test_user)
    db.session.commit()
    auth.login(email = test_user.email)
    
    daily_report = DailyReport(project_id=test_project.id, report_date=datetime.now().date(), report_number="DR-0001", created_by=test_user.id)
    db.session.flush()
    db.session.add(daily_report)
    db.session.commit()

    response = client.post(url_for('api.create_daily_report'), headers=auth.get_auth_header(), json={
        'project_id': test_project.id
    })
    assert response.status_code == 400
    assert response.json['message'] == 'A report for today already exists'

def test_create_daily_report_success(client, auth, test_user, test_project):
    """Test successfully creating a daily report."""
    test_project.users.append(test_user)
    db.session.commit()
    auth.login(email = test_user.email)
    
    data = {
        'project_id': test_project.id,
        'weather_condition': 'Sunny',
        'temperature_high': 85,
        'temperature_low': 65,
        'precipitation': 0,
        'wind_speed': 10,
        'work_status': 'working',
        'delay_reason': '',
        'labor_count': 10,
        'work_performed': 'Concrete pouring',
        'materials_received': 'Concrete, steel',
        'notes': 'All good'
    }

    response = client.post(url_for('api.create_daily_report'), headers=auth.get_auth_header(), json=data)
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert response.json['message'] == 'Daily report created successfully'
    assert 'report_id' in response.json
    
def test_get_project_daily_reports_unauthorized(client, test_project):
    """Test getting a project's daily reports without authentication."""
    response = client.get(url_for('api.get_project_daily_reports', id=test_project.id))
    assert response.status_code == 401

def test_get_project_daily_reports_forbidden(client, auth, test_user, test_project):
    """Test getting a project's daily reports with an unauthorized user."""
    auth.login()
    response = client.get(url_for('api.get_project_daily_reports', id=test_project.id), headers=auth.get_auth_header())
    assert response.status_code == 403

def test_get_project_daily_reports_not_found(client, auth, test_user, test_project):
    """Test getting daily reports for a non-existent project."""
    auth.login()
    response = client.get(url_for('api.get_project_daily_reports', id=999), headers=auth.get_auth_header())
    assert response.status_code == 404

def test_get_project_daily_reports_success(client, auth, test_user, test_project):
    """Test successfully getting a project's daily reports."""
    test_project.users.append(test_user)
    db.session.commit()
    auth.login(email = test_user.email)
    
    daily_report = DailyReport(project_id=test_project.id, report_date=datetime.now().date(), report_number="DR-0001", created_by=test_user.id)
    db.session.flush()
    db.session.add(daily_report)
    db.session.commit()

    response = client.get(url_for('api.get_project_daily_reports', id=test_project.id), headers=auth.get_auth_header())
    assert response.status_code == 200
    assert response.json['status'] == 'success'
    assert len(response.json['data']) > 0
    assert response.json['data'][0]['id'] == daily_report.id


def test_create_daily_report_invalid_data(client, auth, test_user, test_project):
    """Test creating a daily report with invalid data types."""
    test_project.users.append(test_user)
    db.session.commit()
    auth.login(email = test_user.email)

    data = {
        'project_id': test_project.id,
        'weather_condition': 123,  # Invalid data type
        'temperature_high': 'abc',  # Invalid data type
    }

    response = client.post(url_for('api.create_daily_report'), headers=auth.get_auth_header(), json=data)
    assert response.status_code == 400
    assert response.json['message'] == 'Invalid data'

    assert response.json['data'][0]['id'] == daily_report.id