import pytest
from app import create_app
from app.models.user import User
from app.models.contracts import ChangeOrder, Invoice
from app import db
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_headers(client, app):
    with app.app_context():
        user = User(email="test@example.com", password="password", role="admin")
        db.session.add(user)
        db.session.commit()
        
        response = client.post('/api/auth/token', json={"email": "test@example.com", "password": "password"})
        token = json.loads(response.data.decode())['token']
        return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def create_change_order(app, auth_headers):
    with app.app_context():
        def _create_change_order(project_id):
            change_order = ChangeOrder(project_id=project_id, number="CO-001", title="Test Change Order", amount=1000.00, status="pending")
            db.session.add(change_order)
            db.session.commit()
            return change_order
        return _create_change_order

@pytest.fixture
def create_invoice(app, auth_headers):
    with app.app_context():
        def _create_invoice(project_id):
            invoice = Invoice(project_id=project_id, invoice_number="INV-001", vendor="Test Vendor", amount=500.00, status="paid")
            db.session.add(invoice)
            db.session.commit()
            return invoice
        return _create_invoice
        
def test_get_change_orders_for_project(client, auth_headers, create_change_order):
    with client.application.app_context():
        # Create a project for testing
        project_id = 1
        # Create a change order
        create_change_order(project_id)
        
        # Make a request to get change orders for the project
        response = client.get(f'/api/projects/{project_id}/cost/change-orders', headers=auth_headers)
        
        # Assert that the response is successful
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']) == 1

def test_get_invoices_for_project(client, auth_headers, create_invoice):
    with client.application.app_context():
        # Create a project for testing
        project_id = 1
        # Create an invoice
        create_invoice(project_id)
        
        # Make a request to get invoices for the project
        response = client.get(f'/api/projects/{project_id}/cost/invoices', headers=auth_headers)
        
        # Assert that the response is successful
        assert response.status_code == 200
        data = json.loads(response.data.decode())
        assert data['status'] == 'success'
        assert len(data['data']) == 1