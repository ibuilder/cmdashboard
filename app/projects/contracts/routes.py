from flask import Blueprint, request, jsonify, abort
from app.models.contracts import Contract, ChangeOrder
from app import db
from app import cache
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.auth.utils import token_required
from app.utils.utils import generate_response, validate_schema
import logging

logger = logging.getLogger(__name__)

contracts_bp = Blueprint('contracts', __name__)


@contracts_bp.route('/projects/<int:project_id>/contracts', methods=['GET'])
@token_required
@cache.cached(timeout=60)
def get_contracts(current_user, project_id):
    """
    Get all contracts for a specific project.
    """
    try:
        contracts = Contract.query.filter(Contract.project_id == project_id).all()
        return generate_response([contract.to_dict() for contract in contracts])
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error getting contracts: {e}")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting contracts: {e}")
        return jsonify({'status': 'error', 'message': 'Error getting contracts'}), 500


@contracts_bp.route('/projects/<int:project_id>/contracts', methods=['POST'])
@token_required
def create_contract(current_user, project_id):
    """
    Create a new contract for a specific project.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No input data provided'}), 400

        contract = Contract(project_id=project_id, **data)        
        db.session.add(contract)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Contract created', 'contract_id': contract.id}), 201
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database IntegrityError creating contract: {e}")
        return jsonify({'status': 'error', 'message': 'Database integrity error'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error creating contract: {e}")
        db.session.rollback()
        logger.error(f"Error creating contract: {e}")
        return jsonify({'status': 'error', 'message': 'Error creating contract'}), 500


@contracts_bp.route('/contracts/<int:contract_id>', methods=['GET'])
@token_required
@cache.cached(timeout=60)
def get_contract(current_user, contract_id):
    """
    Get a specific contract by ID.
    """
    try:
        contract = Contract.query.get_or_404(contract_id)
        return generate_response(contract.to_dict())
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error getting contract: {e}")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error getting contract: {e}")
        return jsonify({'status': 'error', 'message': 'Error getting contract'}), 500


@contracts_bp.route('/contracts/<int:contract_id>', methods=['PUT'])
@token_required
def update_contract(current_user, contract_id):
    """
    Update a specific contract by ID.
    """
    try:
        contract = Contract.query.get_or_404(contract_id)
        data = request.get_json()
        if not data:
            return jsonify({'status': 'error', 'message': 'No input data provided'}), 400

        for key, value in data.items():
            setattr(contract, key, value)

        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Contract updated'}), 200
    except IntegrityError as e:
        db.session.rollback()
        logger.error(f"Database IntegrityError updating contract: {e}")
        return jsonify({'status': 'error', 'message': 'Database integrity error'}), 400
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Error updating contract: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': 'Error updating contract'}), 500


@contracts_bp.route('/contracts/<int:contract_id>', methods=['DELETE'])
@token_required
def delete_contract(current_user, contract_id):
    """
    Delete a specific contract by ID.
    """
    try:
        contract = Contract.query.get_or_404(contract_id)
        db.session.delete(contract)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Contract deleted'}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        logger.error(f"Database error deleting contract: {e}")
        return jsonify({'status': 'error', 'message': 'Database error'}), 500
    except Exception as e:
        logger.error(f"Unexpected error deleting contract: {e}")
        return jsonify({'status': 'error', 'message': 'Error deleting contract'}), 500