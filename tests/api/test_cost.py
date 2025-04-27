import pytest
from app import create_app
from app.models.user import User
from app.models.cost import ChangeOrder, Invoice
from app import db
import json

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def add_user(app):
    def _add_user(email, password, role='user'):
        user = User(email=email, password=password, role=role)
        with app.app_context():
            db.session.add(user)
            db.session.commit()
        return user
    return _add_user

@pytest.fixture
def add_change_order(app):
    def _add_change_order(project_id, number, title, amount, status, date_issued, date_approved):
        change_order = ChangeOrder(project_id=project_id, number=number, title=title, amount=amount, status=status, date_issued=date_issued, date_approved=date_approved)
        with app.app_context():
            db.session.add(change_order)
            db.session.commit()
        return change_order
    return _add_change_order

@pytest.fixture
def add_invoice(app):
    def _add_invoice(project_id, invoice_number, vendor, amount, status, invoice_date, due_date):
        invoice = Invoice(project_id=project_id, invoice_number=invoice_number, vendor=vendor, amount=amount, status=status, invoice_date=invoice_date, due_date=due_date)
        with app.app_context():
            db.session.add(invoice)
            db.session.commit()
        return invoice
    return _add_invoice

def get_auth_token(client, email, password):
    response = client.post('/api/auth/token', data=json.dumps(dict(email=email, password=password)), content_type='application/json')
    return json.loads(response.data)['token']

def test_get_change_orders(client, add_user, add_change_order):
    user = add_user('test@example.com', 'password', role='admin')
    token = get_auth_token(client, 'test@example.com', 'password')
    add_change_order(1, 'CO-001', 'Test Change Order 1', 1000.00, 'pending', '2023-01-01', None)
    add_change_order(1, 'CO-002', 'Test Change Order 2', 2000.00, 'approved', '2023-01-02', '2023-01-05')

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects/1/cost/change-orders', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 2

def test_get_invoices(client, add_user, add_invoice):
    user = add_user('test@example.com', 'password', role='admin')
    token = get_auth_token(client, 'test@example.com', 'password')
    add_invoice(1, 'INV-001', 'Vendor 1', 500.00, 'paid', '2023-01-01', '2023-01-15')
    add_invoice(1, 'INV-002', 'Vendor 2', 1500.00, 'pending', '2023-01-05', '2023-01-20')

    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects/1/cost/invoices', headers=headers)
    assert response.status_code == 200
    data = json.loads(response.data)
    assert len(data['data']) == 2

def test_get_change_orders_unauthorized(client):
    response = client.get('/api/projects/1/cost/change-orders')
    assert response.status_code == 401

def test_get_invoices_unauthorized(client):
    response = client.get('/api/projects/1/cost/invoices')
    assert response.status_code == 401

def test_get_change_orders_forbidden(client, add_user):
    user = add_user('test@example.com', 'password', role='user')
    token = get_auth_token(client, 'test@example.com', 'password')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects/1/cost/change-orders', headers=headers)
    assert response.status_code == 403

def test_get_invoices_forbidden(client, add_user):
    user = add_user('test@example.com', 'password', role='user')
    token = get_auth_token(client, 'test@example.com', 'password')
    headers = {'Authorization': f'Bearer {token}'}
    response = client.get('/api/projects/1/cost/invoices', headers=headers)
    assert response.status_code == 403