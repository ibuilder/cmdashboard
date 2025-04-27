# app/mobile/main.py
import requests
import json

class MobileApp:
    def __init__(self, api_base_url):
        self.api_base_url = api_base_url
        self.token = None

    def login(self, email, password):
        url = f"{self.api_base_url}/auth/token"
        payload = {"email": email, "password": password}
        headers = {'Content-Type': 'application/json'}
        try:
            response = requests.post(url, data=json.dumps(payload), headers=headers)
            response.raise_for_status()
            data = response.json()
            self.token = data.get("token")
            print("Login successful!")
            return True
        except requests.exceptions.HTTPError as e:
            print(f"Login failed: {e}")
            return False

    def get_projects(self):
        if not self.token:
            print("Not logged in.")
            return
        url = f"{self.api_base_url}/projects"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            print("Projects:")
            for project in data.get("data", []):
                print(f"- {project['name']} (ID: {project['id']})")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get projects: {e}")

    def get_project_details(self, project_id):
        if not self.token:
            print("Not logged in.")
            return
        url = f"{self.api_base_url}/projects/{project_id}"
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            project = data.get("data")
            print("Project Details:")
            print(f"- Name: {project['name']}")
            print(f"- Number: {project['number']}")
            print(f"- Description: {project['description']}")
        except requests.exceptions.HTTPError as e:
            print(f"Failed to get project details: {e}")
            

    def run(self):
      
        if self.login("test@example.com", "password"):
          self.get_projects()
          self.get_project_details(1)
          
if __name__ == "__main__":
    app = MobileApp("http://localhost:8000/api") 
    app.run()