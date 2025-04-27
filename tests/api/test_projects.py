import unittest
import json
from app import create_app, db
from app.models.project import Project
from app.models.user import User
from app.auth.utils import generate_token


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        self.client = self.app.test_client()

        # Create a test user and project
        self.user = User(name='Test User', email='test@example.com', password='password', role='Admin')
        db.session.add(self.user)
        db.session.commit()

        self.project = Project(name='Test Project', number='123', status='Active', owner_id=1)
        self.project.users.append(self.user)
        db.session.add(self.project)
        db.session.commit()
        
        # Get an authentication token
        response = self.client.post('/auth/token', json={'email': 'test@example.com', 'password': 'password'})
        data = json.loads(response.data.decode())
        self.token = data['token']
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_projects(self):
        response = self.client.get('/api/projects', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
        self.assertTrue(len(data['data']) > 0)

    def test_get_project(self):
        response = self.client.get(f'/api/projects/{self.project.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['data']['name'], 'Test Project')

    def test_get_project_not_found(self):
        response = self.client.get('/api/projects/999', headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_project_rfis(self):
        response = self.client.get(f'/api/projects/{self.project.id}/rfis', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')

    def test_get_project_submittals(self):
        response = self.client.get(f'/api/projects/{self.project.id}/submittals', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')

    def test_get_project_daily_reports(self):
        response = self.client.get(f'/api/projects/{self.project.id}/daily-reports', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')

    def test_get_daily_report(self):
        from app.models.field import DailyReport
        daily_report = DailyReport(project_id=self.project.id, report_number='DR-0001', report_date='2024-05-01', created_by=self.user.id)
        db.session.add(daily_report)
        db.session.commit()
        response = self.client.get(f'/api/daily-reports/{daily_report.id}', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
    
    def test_create_daily_report(self):
        data = {
            'project_id': self.project.id,
            'weather_condition': 'Sunny',
            'temperature_high': 80,
            'temperature_low': 60,
            'precipitation': 0,
            'wind_speed': 10,
            'labor_count': 5,
            'work_performed': 'Test work'
        }
        response = self.client.post('/api/daily-reports/create', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
        self.assertTrue('report_id' in data)

    def test_get_project_safety_observations(self):
        response = self.client.get(f'/api/projects/{self.project.id}/safety/observations', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
    
    def test_get_project_change_orders(self):
        response = self.client.get(f'/api/projects/{self.project.id}/cost/change-orders', headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')
        
    def test_verify_document(self):
        data = {
            'document_type': 'test',
            'document_id': '1',
            'hash': 'test_hash'
        }
        response = self.client.post('/api/verify-document', json=data, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data.decode())
        self.assertEqual(data['status'], 'success')

    def test_get_auth_token(self):
      response = self.client.post('/auth/token', json={'email': 'test@example.com', 'password': 'password'})
      self.assertEqual(response.status_code, 200)
      data = json.loads(response.data.decode())
      self.assertEqual(data['status'], 'success')
      self.assertIsNotNone(data['token'])

    def test_get_auth_token_invalid(self):
      response = self.client.post('/auth/token', json={'email': 'test@example.com', 'password': 'wrong_password'})
      self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main()