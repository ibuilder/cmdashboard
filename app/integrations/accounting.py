import requests
import json
import logging

class AccountingSystemIntegration:
    def __init__(self, api_url, api_key):
        self.api_url = api_url
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }

    def connect(self):
        logging.info("Connecting to accounting system...")
        try:
            response = requests.get(f'{self.api_url}/ping', headers=self.headers)
            response.raise_for_status()  # Raise an exception for bad status codes
            logging.info("Successfully connected to accounting system.")
            return True
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to connect to accounting system: {e}")
            return False

    def send_data(self, endpoint, data):
        logging.info(f"Sending data to accounting system endpoint: {endpoint}")
        try:
            response = requests.post(f'{self.api_url}/{endpoint}', headers=self.headers, data=json.dumps(data))
            response.raise_for_status()
            logging.info(f"Successfully sent data to endpoint: {endpoint}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to send data to endpoint {endpoint}: {e}")
            return None

    def receive_data(self, endpoint, params=None):
        logging.info(f"Receiving data from accounting system endpoint: {endpoint}")
        try:
            response = requests.get(f'{self.api_url}/{endpoint}', headers=self.headers, params=params)
            response.raise_for_status()
            logging.info(f"Successfully received data from endpoint: {endpoint}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to receive data from endpoint {endpoint}: {e}")
            return None

    def create_invoice(self, invoice_data):
        logging.info("Creating new invoice in accounting system...")
        try:
            response = self.send_data('invoices', invoice_data)
            if response:
                logging.info(f"Successfully created invoice in accounting system: {response}")
                return response
            else:
                logging.error("Failed to create invoice in accounting system.")
                return None
        except Exception as e:
            logging.error(f"Error creating invoice in accounting system: {e}")
            return None