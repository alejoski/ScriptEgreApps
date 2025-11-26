import requests
import os

class APIClient:
    def __init__(self):
        self.url = os.getenv('API_URL')
        self.token = os.getenv('API_TOKEN')

    def call_endpoint(self):
        headers = {'Authorization': f'Bearer {self.token}'}
        try:
            response = requests.get(self.url, headers=headers)
            print(f'Respuesta API: {response.status_code}')
            return response.json()
        except Exception as e:
            print(f'Error consumiendo API: {e}')
