import pytest
from app.models.safety import SafetyObservation, IncidentReport
from app import db
from tests.utils import create_test_project, create_test_user, get_api_token, add_safety_observation, add_incident_report

def test_get_safety_observations_success(test_client, test_db):
    """Test successful retrieval of safety observations for a project."""
    project = create_test_project(test_db)
    user = create_test_user(test_db)
    token = get_api_token(test_client, user.email, "password")
    add_safety_observation(test_db, project_id=project.id)

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get(f"/api/projects/{project.id}/safety/observations", headers=headers)
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert len(response.json["data"]) == 1

def test_get_safety_observations_project_not_found(test_client, test_db):
    """Test retrieval of safety observations for a non-existent project."""
    user = create_test_user(test_db)
    token = get_api_token(test_client, user.email, "password")

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/projects/999/safety/observations", headers=headers)
    assert response.status_code == 404
    assert response.json["status"] == "error"

def test_get_safety_observations_unauthorized(test_client, test_db):
    """Test retrieval of safety observations without authentication."""
    project = create_test_project(test_db)
    response = test_client.get(f"/api/projects/{project.id}/safety/observations")
    assert response.status_code == 401

def test_get_safety_incidents_success(test_client, test_db):
    """Test successful retrieval of safety incidents for a project."""
    project = create_test_project(test_db)
    user = create_test_user(test_db)
    token = get_api_token(test_client, user.email, "password")
    add_incident_report(test_db, project_id=project.id)

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get(f"/api/projects/{project.id}/safety/incidents", headers=headers)
    assert response.status_code == 200
    assert response.json["status"] == "success"
    assert len(response.json["data"]) == 1

def test_get_safety_incidents_project_not_found(test_client, test_db):
    """Test retrieval of safety incidents for a non-existent project."""
    user = create_test_user(test_db)
    token = get_api_token(test_client, user.email, "password")

    headers = {"Authorization": f"Bearer {token}"}
    response = test_client.get("/api/projects/999/safety/incidents", headers=headers)
    assert response.status_code == 404
    assert response.json["status"] == "error"

def test_get_safety_incidents_unauthorized(test_client, test_db):
    """Test retrieval of safety incidents without authentication."""
    project = create_test_project(test_db)
    response = test_client.get(f"/api/projects/{project.id}/safety/incidents")
    assert response.status_code == 401