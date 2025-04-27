import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AccountingSystem:
    """
    Represents a generic accounting system for integration.
    """

    def __init__(self, api_key=None, base_url=None):
        """
        Initializes the AccountingSystem with connection details.

        Args:
            api_key (str, optional): The API key for authentication. Defaults to None.
            base_url (str, optional): The base URL of the accounting system. Defaults to None.
        """
        self.api_key = api_key
        self.base_url = base_url
        logger.info("AccountingSystem initialized")

    def connect(self):
        """
        Simulates connecting to the accounting system.
        """
        logger.info(f"Connecting to accounting system at {self.base_url}...")
        if not self.api_key or not self.base_url:
            logger.error("API key or base URL not provided.")
            raise ConnectionError("API key or base URL not provided.")

        # Simulate connection logic here
        logger.info("Successfully connected to accounting system.")

    def create_invoice(self, invoice_data):
        """
        Simulates creating a new invoice in the accounting system.

        Args:
            invoice_data (dict): The data of the invoice to be created.

        Returns:
            dict: The response from the accounting system.
        """
        logger.info(f"Creating invoice with data: {invoice_data}")
        if not isinstance(invoice_data, dict):
            logger.error("Invalid invoice data format.")
            raise ValueError("Invoice data must be a dictionary.")

        # Simulate creating an invoice in the accounting system here
        logger.info("Invoice created successfully.")
        return {"status": "success", "message": "Invoice created.", "invoice_id": "INV-12345"}

    def get_invoice(self, invoice_id):
        """
        Simulates getting an invoice from the accounting system.

        Args:
            invoice_id (str): The ID of the invoice to be retrieved.

        Returns:
            dict: The response from the accounting system.
        """
        logger.info(f"Getting invoice with id: {invoice_id}")
        if not isinstance(invoice_id, str):
            logger.error("Invalid invoice id format.")
            raise ValueError("Invoice id must be a string.")
        # Simulate getting an invoice in the accounting system here
        logger.info("Invoice retrieved successfully.")
        return {"status": "success", "message": "Invoice retrieved.", "invoice_id": invoice_id}