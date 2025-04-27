import unittest
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from flask_login import login_user
from flask import url_for
import json

class TestRoutes(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
        self.app_context = self.app.app_context()
        self.app_context.push()
        self.client = self.app.test_client(use_cookies=True)
        db.create_all()
        
        # Create test users
        admin_user = User(
            name='Admin User',
            email='admin@example.com',
            password=generate_password_hash('password123'),
            role='Admin',
            status='active'
        )
        normal_user = User(
            name='Normal User',
            email='user@example.com',
            password=generate_password_hash('password123'),
            role='User',
            status='active'
        )
        db.session.add_all([admin_user, normal_user])
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login(self, email, password):
        return self.client.post('/auth/login', data={
            'email': email,
            'password': password
        }, follow_redirects=True)
    
    def logout(self):
        return self.client.get('/auth/logout', follow_redirects=True)
    
    def test_home_page(self):
        """Test home page redirect"""
        response = self.client.get('/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_page(self):
        """Test login page"""
        response = self.client.get('/auth/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_login_logout(self):
        """Test login and logout functionality"""
        # Login with valid credentials
        response = self.login('admin@example.com', 'password123')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
        
        # Logout
        response = self.logout()
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
    
    def test_invalid_login(self):
        """Test login with invalid credentials"""
        response = self.login('admin@example.com', 'wrong-password')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid email or password', response.data)
    
    def test_dashboard_access(self):
        """Test dashboard access control"""
        # Without login, should redirect to login page
        response = self.client.get('/dashboard/', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        
        # Login and access dashboard
        self.login('admin@example.com', 'password123')
        response = self.client.get('/dashboard/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_admin_access(self):
        """Test admin section access control"""
        # Login as admin
        self.login('admin@example.com', 'password123')
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'User Management', response.data)
        
        # Logout and login as normal user
        self.logout()
        self.login('user@example.com', 'password123')
        
        # Should be forbidden for normal user
        response = self.client.get('/admin/users')
        self.assertEqual(response.status_code, 302)  # Redirect to dashboard
        
        # Follow redirect
        response = self.client.get('/admin/users', follow_redirects=True)
        self.assertIn(b'You do not have permission', response.data)