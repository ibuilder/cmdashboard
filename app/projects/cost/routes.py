from flask import Blueprint, request, jsonify
from app.integrations.accounting import AccountingSystem


cost_bp = Blueprint('cost', __name__)

accounting_system = AccountingSystem()


@cost_bp.route('/invoices', methods=['POST'])
def create_invoice():
    """
    Creates a new invoice in the accounting system.
    """
    data = request.get_json()

    if not data or 'project_id' not in data or 'amount' not in data or 'description' not in data:
        return jsonify({'error': 'Invalid invoice data'}), 400

    try:
        invoice_id = accounting_system.create_invoice(data)
        return jsonify({'invoice_id': invoice_id}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500