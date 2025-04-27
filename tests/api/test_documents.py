import pytest
from app import create_app, db
from app.models.document import Document
from tests.utils import get_api_key, create_test_user, create_test_document, delete_test_document
from flask import url_for
import json

@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def api_key(app):
    with app.app_context():
        return get_api_key(app)

@pytest.fixture
def user(app):
    with app.app_context():
        return create_test_user(app)

@pytest.fixture
def document(app, user):
    with app.app_context():
        return create_test_document(app, user)
    
def test_verify_document_success(client, api_key, document):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {document.created_by.generate_auth_token()}"
    }

    data = {
        "document_type": "test",
        "document_id": str(document.id),
        "hash": document.hash
    }
    response = client.post(url_for("api.verify_document"), headers=headers, data=json.dumps(data), content_type="application/json")

    assert response.status_code == 200
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data["status"] == "success"
    assert response_data["verified"] is True
    assert response_data["data"]["is_valid"] is True

def test_verify_document_invalid_hash(client, api_key, document):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {document.created_by.generate_auth_token()}"
    }
    data = {
        "document_type": "test",
        "document_id": str(document.id),
        "hash": "invalid_hash"
    }
    response = client.post(url_for("api.verify_document"), headers=headers, data=json.dumps(data), content_type="application/json")

    assert response.status_code == 200
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data["status"] == "success"
    assert response_data["verified"] is False

def test_verify_document_invalid_api_key(client, document):
    headers = {
        "X-API-Key": "invalid_api_key",
        "Authorization": f"Bearer {document.created_by.generate_auth_token()}"
    }
    data = {
        "document_type": "test",
        "document_id": str(document.id),
        "hash": document.hash
    }
    response = client.post(url_for("api.verify_document"), headers=headers, data=json.dumps(data), content_type="application/json")

    assert response.status_code == 401
    response_data = json.loads(response.get_data(as_text=True))
    assert response_data["error"] == "Invalid API key"

def test_verify_document_unauthorized(client, api_key, document):
    headers = {
        "X-API-Key": api_key,
    }

    data = {
        "document_type": "test",
        "document_id": str(document.id),
        "hash": document.hash
    }
    response = client.post(url_for("api.verify_document"), headers=headers, data=json.dumps(data), content_type="application/json")
    assert response.status_code == 401

def test_verify_document_invalid_data(client, api_key, document):
    headers = {
        "X-API-Key": api_key,
        "Authorization": f"Bearer {document.created_by.generate_auth_token()}"
    }
    data = {
        "document_type": "test",
    }
    response = client.post(url_for("api.verify_document"), headers=headers, data=json.dumps(data), content_type="application/json")
    assert response.status_code == 400