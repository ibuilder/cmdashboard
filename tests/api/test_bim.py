import json
import pytest

from app.models.bim import BIMModel
from app.models.project import Project

from tests.utils import get_api_headers

def test_get_project_bim_models(client, test_db, admin_user, project_factory, bim_model_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()
    
    bim_model1 = bim_model_factory(project_id=project.id)
    bim_model2 = bim_model_factory(project_id=project.id)
    test_db.session.add_all([bim_model1, bim_model2])
    test_db.session.commit()

    response = client.get(f'/api/projects/{project.id}/bim', headers=get_api_headers(admin_user))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 2
    assert {bm['id'] for bm in data['data']} == {bim_model1.id, bim_model2.id}

def test_get_project_bim_models_empty(client, test_db, admin_user, project_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    response = client.get(f'/api/projects/{project.id}/bim', headers=get_api_headers(admin_user))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert len(data['data']) == 0

def test_get_project_bim_models_wrong_project(client, test_db, admin_user, project_factory, bim_model_factory):
    project = project_factory()
    bim_model1 = bim_model_factory(project_id=project.id)
    test_db.session.add_all([project,bim_model1])
    test_db.session.commit()

    response = client.get(f'/api/projects/999/bim', headers=get_api_headers(admin_user))
    assert response.status_code == 404
    assert json.loads(response.data)['status'] == 'error'

def test_add_project_bim_model(client, test_db, admin_user, project_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    bim_data = {
        'title': 'BIM Model 1',
        'description': 'Description 1',
        'file_path': '/path/to/file1.ifc'
    }

    response = client.post(f'/api/projects/{project.id}/bim', headers=get_api_headers(admin_user), json=bim_data)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'BIM model added successfully'
    bim_model = BIMModel.query.filter_by(project_id=project.id).first()
    assert bim_model is not None
    assert bim_model.title == 'BIM Model 1'
    assert bim_model.description == 'Description 1'
    assert bim_model.file_path == '/path/to/file1.ifc'

def test_add_project_bim_model_wrong_data(client, test_db, admin_user, project_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    bim_data = {
        'title': '',
        'description': '',
        'file_path': ''
    }

    response = client.post(f'/api/projects/{project.id}/bim', headers=get_api_headers(admin_user), json=bim_data)
    assert response.status_code == 400
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_delete_project_bim_model(client, test_db, admin_user, project_factory, bim_model_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    bim_model = bim_model_factory(project_id=project.id)
    test_db.session.add(bim_model)
    test_db.session.commit()

    response = client.delete(f'/api/projects/{project.id}/bim/{bim_model.id}', headers=get_api_headers(admin_user))
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['status'] == 'success'
    assert data['message'] == 'BIM model deleted successfully'
    deleted_bim_model = BIMModel.query.get(bim_model.id)
    assert deleted_bim_model is None

def test_get_project_bim_models_unauthorized(client, user, project_factory, test_db, bim_model_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()
    
    response = client.get(f'/api/projects/{project.id}/bim', headers=get_api_headers(user))
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_add_project_bim_model_unauthorized(client, user, project_factory, test_db):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    bim_data = {
        'title': 'BIM Model 1',
        'description': 'Description 1',
        'file_path': '/path/to/file1.ifc'
    }

    response = client.post(f'/api/projects/{project.id}/bim', headers=get_api_headers(user), json=bim_data)
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_delete_project_bim_model_unauthorized(client, user, project_factory, test_db, bim_model_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()

    bim_model = bim_model_factory(project_id=project.id)
    test_db.session.add(bim_model)
    test_db.session.commit()

    response = client.delete(f'/api/projects/{project.id}/bim/{bim_model.id}', headers=get_api_headers(user))
    assert response.status_code == 403
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_get_project_bim_models_project_not_found(client, admin_user):
    response = client.get('/api/projects/999/bim', headers=get_api_headers(admin_user))
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'



def test_add_project_bim_model_project_not_found(client, admin_user):
    bim_data = {
        'title': 'BIM Model 1',
        'description': 'Description 1',
        'file_path': '/path/to/file1.ifc'
    }

    response = client.post('/api/projects/999/bim', headers=get_api_headers(admin_user), json=bim_data)
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_delete_project_bim_model_project_not_found(client, admin_user):
    response = client.delete('/api/projects/999/bim/1', headers=get_api_headers(admin_user))
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'

def test_delete_project_bim_model_bim_not_found(client, test_db, admin_user, project_factory, bim_model_factory):
    project = project_factory()
    test_db.session.add(project)
    test_db.session.commit()
    response = client.delete(f'/api/projects/{project.id}/bim/999', headers=get_api_headers(admin_user))
    assert response.status_code == 404
    data = json.loads(response.data)
    assert data['status'] == 'error'