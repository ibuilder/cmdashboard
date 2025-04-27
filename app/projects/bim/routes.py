"""BIM model routes for the application."""
import logging
import os, json
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.utils import secure_filename

from app.models.project import Project
from app.models.bim import BIMModel
from app.extensions import db

bim_bp = Blueprint('bim', __name__, template_folder='templates', static_folder='static')

logger = logging.getLogger(__name__)


def allowed_file(filename):
    """
    Check if the file extension is allowed.

    Args:
        filename (str): The name of the file.

    Returns:
        bool: True if the file extension is allowed, False otherwise.
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['ifc']


@bim_bp.route('/<int:project_id>/bim_models')
@login_required
def index(project_id):
    """
    Display a list of BIM models for a project.

    Args:
        project_id (int): The ID of the project.

    Returns:
        flask.Response: The rendered BIM model index page.
    """
    project = Project.query.get_or_404(project_id)
    bim_models = BIMModel.query.filter_by(project_id=project_id).all()
    return render_template('bim/index.html', project=project, bim_models=bim_models)


@bim_bp.route('/<int:project_id>/bim_models/<int:bim_model_id>/view', methods=['GET'])
@login_required
def view_bim_model(project_id, bim_model_id):
    """
    Display a list of BIM models for a project.

    Args:
        project_id (int): The ID of the project.
        bim_model_id (int): The ID of the BIM model.

    Returns:
        flask.Response: The rendered BIM model view page.
    """
    project = Project.query.get_or_404(project_id)
    bim_model = BIMModel.query.get_or_404(bim_model_id)
    if bim_model.project_id != project.id:
        logger.warning(f"Unauthorized attempt to view BIM model {bim_model_id} from project {project_id}")
        abort(403)
    
    if bim_model.file_path.endswith('.ifc'):
        with open(bim_model.file_path, 'r') as file:
            content = file.read()
        return render_template('bim/view_ifc.html', project=project, bim_model=bim_model, content=content)
    else:
        flash(f"BIM model '{bim_model_id}' file not supported in this application.", 'danger')
        logger.error(f"BIM model '{bim_model_id}' file not supported in this application for project ID: {project_id}")
        return redirect(url_for('bim.index', project_id=project_id))


@bim_bp.route('/<int:project_id>/bim_models/add', methods=['GET', 'POST'])
@login_required
def add_bim_model(project_id):
    """
    Add a new BIM model for a project, handling file uploads.

    Args:
        project_id (int): The ID of the project.

    Returns:
        flask.Response: The rendered BIM model add page or a redirect to the index page.
    """
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        try:
            # Check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part', 'danger')
                logger.warning(f"No file part in request for project ID: {project_id}")
                return redirect(request.url)
            file = request.files['file']
            if file.filename == '':
                flash('No selected file', 'danger')
                logger.warning(f"No selected file for project ID: {project_id}")
                return redirect(request.url)
            # If the file is present and the extension is allowed
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Creates the file path if it doesn't exist
                file_path = os.path.join(os.getcwd(), 'app', 'static', 'uploads',
                                         'bim_files', str(project_id))
                os.makedirs(file_path, exist_ok=True)
                file_path = os.path.join(file_path, filename)
                file.save(file_path)
                # Save the data into the database
                bim_model = BIMModel(filename=filename, file_path=file_path, project_id=project_id)
                db.session.add(bim_model)
                db.session.commit()
                flash('BIM model added successfully', 'success')
                logger.info(f"BIM model '{filename}' added successfully for project ID: {project_id}")
                return redirect(url_for('bim.index', project_id=project_id))
        except SQLAlchemyError as e:
            db.session.rollback()
            flash('An error occurred while adding the BIM model', 'danger')
            logger.error(f"Database error adding BIM model for project ID {project_id}: {e}", exc_info=True)
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while adding the BIM model', 'danger')
            logger.error(f"Error adding BIM model for project ID {project_id}: {e}", exc_info=True)

    return render_template('bim/add.html', project=project)


@bim_bp.route('/<int:project_id>/bim_models/<int:bim_model_id>/delete', methods=['POST'])
@login_required
def delete_bim_model(project_id, bim_model_id):
    """
    Delete a BIM model.

    Args:
        project_id (int): The ID of the project.
        bim_model_id (int): The ID of the BIM model to delete.

    Returns:
        flask.Response: A redirect to the BIM model index page.
    """
    bim_model = BIMModel.query.get_or_404(bim_model_id)
    project = Project.query.get_or_404(project_id)
    if bim_model.project_id != project.id:
        logger.warning(f"Unauthorized attempt to delete BIM model {bim_model_id} from project {project_id}")
        abort(403)
    try:
        # Delete the file from the file system
        if os.path.exists(bim_model.file_path):
            os.remove(bim_model.file_path)
            logger.info(f"BIM model file deleted from path: {bim_model.file_path}")
        db.session.delete(bim_model)
        db.session.commit()
        flash('BIM model deleted successfully', 'success')
        logger.info(f"BIM model '{bim_model_id}' deleted successfully from project ID: {project_id}")
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while deleting the BIM model', 'danger')
        logger.error(f"Database error deleting BIM model {bim_model_id} from project {project_id}: {e}", exc_info=True)
    except Exception as e:
        flash('An error occurred while deleting the BIM model', 'danger')
        logger.error(f"Error deleting BIM model {bim_model_id} from project {project_id}: {e}", exc_info=True)
    return redirect(url_for('bim.index', project_id=project_id))
