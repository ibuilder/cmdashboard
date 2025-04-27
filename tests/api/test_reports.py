import pytest
from app.models.project import Project
from app.models.field import DailyReport
from app import db

def test_get_daily_report(client, auth, app):
    with app.app_context():
        project = Project(name='Test Project', number='TP1', description='Test project description')
        db.session.add(project)
        db.session.commit()
        auth.login()
        
        daily_report = DailyReport(
            project_id=project.id,
            report_number="DR-001",
            report_date="2024-01-01",
            weather_conditions="Sunny",
            temperature_high=25,
            temperature_low=15,
            precipitation=0,
            wind_speed=10,
            delays=False,
            delay_description=None,
            manpower_count=10,
            work_performed="Foundation work",
            materials_received="Concrete",
            equipment_used="Excavator",
            visitors="None",
            safety_incidents="None",
            quality_issues="None",
        )
        db.session.add(daily_report)
        db.session.commit()

        response = client.get(f'/projects/{project.id}/reports/daily-report', headers={'Authorization': f'Bearer {auth.token}'})
        assert response.status_code == 200
        assert b'Test Project' in response.data
        assert b'DR-001' in response.data
        

def test_get_daily_report_unauthorized(client, auth, app):
    with app.app_context():
        project = Project(name='Test Project', number='TP1', description='Test project description')
        db.session.add(project)
        db.session.commit()
        
        response = client.get(f'/projects/{project.id}/reports/daily-report')
        assert response.status_code == 401

def test_get_daily_report_project_not_found(client, auth, app):
    with app.app_context():
        auth.login()
        response = client.get('/projects/999/reports/daily-report', headers={'Authorization': f'Bearer {auth.token}'})
        assert response.status_code == 404