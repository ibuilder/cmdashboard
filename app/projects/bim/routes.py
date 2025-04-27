from flask import Blueprint, render_template, request, redirect, url_for, flash, send_from_directory, abort
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.bim import BIMModel
from app.extensions import db
import os
from werkzeug.utils import secure_filename

bim_bp = Blueprint('bim', __name__, template_folder='templates', static_folder='static')

def allowed_file(filename):
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['ifc', 'rvt', 'dwg', 'pdf']

@bim_bp.route('/<int:project_id>/bim_models')
@login_required
def index(project_id):
    """Display a list of BIM models for a project."""
    project = Project.query.get_or_404(project_id)
    bim_models = BIMModel.query.filter_by(project_id=project_id).all()
    return render_template('bim/index.html', project=project, bim_models=bim_models)

@bim_bp.route('/<int:project_id>/bim_models/add', methods=['GET', 'POST'])
@login_required
def add_bim_model(project_id):
    """Add a new BIM model for a project."""
    project = Project.query.get_or_404(project_id)
    if request.method == 'POST':
        # Check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part', 'danger')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an empty file without a filename
        if file.filename == '':
            flash('No selected file', 'danger')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(os.getcwd(), 'app', 'static', 'uploads', 'bim_files', str(project_id))
            os.makedirs(file_path, exist_ok=True)
            file_path = os.path.join(file_path, filename)
            file.save(file_path)
            bim_model = BIMModel(filename=filename, file_path=file_path, project_id=project_id)
            db.session.add(bim_model)
            db.session.commit()
            flash('BIM model added successfully', 'success')
            return redirect(url_for('projects.bim.index', project_id=project_id))
    return render_template('bim/add.html', project=project)

@bim_bp.route('/<int:project_id>/bim_models/<int:bim_model_id>/delete', methods=['POST'])
@login_required
def delete_bim_model(project_id, bim_model_id):
    """Delete a BIM model."""
    bim_model = BIMModel.query.get_or_404(bim_model_id)
    project = Project.query.get_or_404(project_id)
    if bim_model.project_id != project.id:
        abort(403)
    if os.path.exists(bim_model.file_path):
        os.remove(bim_model.file_path)
    db.session.delete(bim_model)
    db.session.commit()
    flash('BIM model deleted successfully', 'success')
    return redirect(url_for('projects.bim.index', project_id=project_id))