import unittest
from app import create_app, db
from app.models.user import User
from app.models.project import Project
from app.models.engineering import RFI
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import os

class TestModels(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test user
        self.test_user = User(
            name='Test User',
            email='test@example.com',
            password=generate_password_hash('password123'),
            role='Admin',
            status='active'
        )
        db.session.add(self.test_user)
        
        # Create test project
        self.test_project = Project(
            name='Test Project',
            number='TP-001',
            description='A test project',
            status='active',
            start_date=datetime.now().date(),
            end_date=(datetime.now() + timedelta(days=100)).date(),
            created_by=1
        )
        db.session.add(self.test_project)
        db.session.commit()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_user_model(self):
        """Test User model"""
        user = User.query.filter_by(email='test@example.com').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.name, 'Test User')
        self.assertEqual(user.role, 'Admin')
        self.assertEqual(user.status, 'active')
    
    def test_project_model(self):
        """Test Project model"""
        project = Project.query.filter_by(number='TP-001').first()
        self.assertIsNotNone(project)
        self.assertEqual(project.name, 'Test Project')
        self.assertEqual(project.status, 'active')
        self.assertIsNotNone(project.start_date)
        self.assertIsNotNone(project.end_date)
    
    def test_rfi_creation(self):
        """Test RFI creation"""
        rfi = RFI(
            project_id=self.test_project.id,
            number='RFI-0001',
            subject='Test RFI',
            question='This is a test question?',
            status='open',
            date_submitted=datetime.now().date(),
            submitted_by=self.test_user.id
        )
        db.session.add(rfi)
        db.session.commit()
        
        saved_rfi = RFI.query.filter_by(number='RFI-0001').first()
        self.assertIsNotNone(saved_rfi)
        self.assertEqual(saved_rfi.subject, 'Test RFI')
        self.assertEqual(saved_rfi.status, 'open')
        self.assertEqual(saved_rfi.project_id, self.test_project.id)
    
    def test_user_project_relationship(self):
        """Test User-Project relationship"""
        user = User.query.get(self.test_user.id)
        project = Project.query.get(self.test_project.id)
        
        # Add user to project
        project.users.append(user)
        db.session.commit()
        
        # Verify relationship
        self.assertIn(user, project.users)
        self.assertIn(project, user.projects)