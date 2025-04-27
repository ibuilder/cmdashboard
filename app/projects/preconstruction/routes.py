from flask import Blueprint, request, jsonify, abort, g
from app.models.preconstruction import Estimate, Proposal, Schedule
from app.models.project import Project
from app.utils.cache import cache
from app import db
import logging

logger = logging.getLogger(__name__)


preconstruction_bp = Blueprint('preconstruction', __name__)

# Helper function to get a project or return 404
def get_project_or_404(project_id):
    project = Project.query.get(project_id)
    if not project:
        logger.error(f"Project with ID {project_id} not found.")
        abort(404, description="Project not found")
    return project


# --- Estimates ---


@preconstruction_bp.route('/projects/<int:project_id>/estimates', methods=['POST'])
@cache.cached(timeout=60)
def create_estimate(project_id):
    project = get_project_or_404(project_id)
    data = request.get_json()
    if not data:
        abort(400, description="No input data provided")
    try:
        estimate = Estimate(**data, project_id=project.id)
        db.session.add(estimate)
        db.session.commit()
        logger.info(f"Estimate {estimate.id} created for project {project_id}.")
        return jsonify({"message": "Estimate created", "id": estimate.id}), 201
    except Exception as e:
        logger.error(f"Error creating estimate: {e}")
        db.session.rollback()
        abort(400, description=str(e))


@preconstruction_bp.route('/projects/<int:project_id>/estimates/<int:estimate_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_estimate(project_id, estimate_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    
    estimate = g.get(f'estimate_{estimate_id}')
    if not estimate:
      estimate = Estimate.query.get(estimate_id)
      if not estimate:
          logger.warning(f"Estimate {estimate_id} not found for project {project_id}.")
          abort(404, description="Estimate not found")
      g.estimate = estimate
      logger.info(f"Estimate {estimate_id} retrieved for project {project_id}.")
      

    return jsonify(estimate.to_dict())


@preconstruction_bp.route('/projects/<int:project_id>/estimates/<int:estimate_id>', methods=['PUT'])
def update_estimate(project_id, estimate_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        logger.warning(f"Estimate {estimate_id} not found for project {project_id}.")
        abort(404, description="Estimate not found")
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(estimate, key, value)
        db.session.commit()
        logger.info(f"Estimate {estimate_id} updated for project {project_id}.")
        return jsonify({"message": "Estimate updated"})
    except Exception as e:
        logger.error(f"Error updating estimate {estimate_id}: {e}")
        db.session.rollback()
        abort(400, description=str(e))


@preconstruction_bp.route('/projects/<int:project_id>/estimates/<int:estimate_id>', methods=['DELETE'])
def delete_estimate(project_id, estimate_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    estimate = Estimate.query.get(estimate_id)
    if not estimate:
        logger.warning(f"Estimate {estimate_id} not found for project {project_id}.")
        abort(404, description="Estimate not found")
    try:
        db.session.delete(estimate)
        db.session.commit()
        logger.info(f"Estimate {estimate_id} deleted for project {project_id}.")
        return jsonify({"message": "Estimate deleted"})
    except Exception as e:
        logger.error(f"Error deleting estimate {estimate_id}: {e}")
        db.session.rollback()
        abort(500, description="Error deleting estimate")


# --- Proposals ---


@preconstruction_bp.route('/projects/<int:project_id>/proposals', methods=['POST'])
@cache.cached(timeout=60)
def create_proposal(project_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    data = request.get_json()
    try:
        proposal = Proposal(**data, project_id=project.id)
        db.session.add(proposal)
        db.session.commit()
        logger.info(f"Proposal {proposal.id} created for project {project_id}.")
        return jsonify({"message": "Proposal created", "id": proposal.id}), 201
    except Exception as e:
        logger.error(f"Error creating proposal: {e}")
        db.session.rollback()
        abort(400, description=str(e))


@preconstruction_bp.route('/projects/<int:project_id>/proposals/<int:proposal_id>', methods=['GET'])
@cache.cached(timeout=60, query_string=True)
def get_proposal(project_id, proposal_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    
    proposal = g.get(f'proposal_{proposal_id}')
    if not proposal:
      proposal = Proposal.query.get(proposal_id)
      if not proposal:
          logger.warning(f"Proposal {proposal_id} not found for project {project_id}.")
          abort(404, description="Proposal not found")
      g.proposal = proposal
    
    logger.info(f"Proposal {proposal_id} retrieved for project {project_id}.")
    logger.info(f"Proposal {proposal_id} retrieved for project {project_id}.")
    return jsonify(proposal.to_dict())


@preconstruction_bp.route('/projects/<int:project_id>/proposals/<int:proposal_id>', methods=['PUT'])
def update_proposal(project_id, proposal_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    proposal = Proposal.query.get(proposal_id)
    if not proposal:
        logger.warning(f"Proposal {proposal_id} not found for project {project_id}.")
        abort(404, description="Proposal not found")
    data = request.get_json()
    try:
        for key, value in data.items():
            setattr(proposal, key, value)
        db.session.commit()
        logger.info(f"Proposal {proposal_id} updated for project {project_id}.")
        return jsonify({"message": "Proposal updated"})
    except Exception as e:
        logger.error(f"Error updating proposal {proposal_id}: {e}")
        db.session.rollback()
        abort(400, description=str(e))


@preconstruction_bp.route('/projects/<int:project_id>/proposals/<int:proposal_id>', methods=['DELETE'])
def delete_proposal(project_id, proposal_id):
    project = get_project_or_404(project_id)
    if not project:
        abort(404, description="Project not found")
    proposal = Proposal.query.get(proposal_id)
    if not proposal:
        logger.warning(f"Proposal {proposal_id} not found for project {project_id}.")
        abort(404, description="Proposal not found")
    db.session.delete(proposal)
    db.session.commit()
    logger.info(f"Proposal {proposal_id} deleted for project {project_id} .")
    return jsonify({"message": "Proposal deleted"})