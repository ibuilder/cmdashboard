import pytest
from app.models.closeout import Punchlist
from tests.conftest import auth_header


def test_get_punchlist(client, db, test_project, test_punchlist):
    response = client.get(f'/api/projects/{test_project.id}/punchlists', headers=auth_header)
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success'
    assert len(data['data']) > 0
    assert data['data'][0]['id'] == test_punchlist.id


def test_get_punchlist_not_found(client, db, test_project):
    response = client.get('/api/projects/999/punchlists', headers=auth_header)
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'error'


def test_get_punchlist_unauthorized(client, db, test_project):
    response = client.get(f'/api/projects/{test_project.id}/punchlists')
    assert response.status_code == 401