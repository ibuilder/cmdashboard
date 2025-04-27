from flask import Blueprint, render_template, abort, request, current_app, jsonify
from app.models.project import Project, ProjectStatusEnum
from flask_caching import Cache
from markupsafe import escape
from app.models.field import DailyReport, DailyReportSchema, db
import logging
from app.models.cost import ChangeOrder, Invoice, db
from app.models.safety import SafetyIncident, SafetyObservation

# Configure logging for the reports blueprint
logger = logging.getLogger(__name__)

reports_bp = Blueprint('reports', __name__)
# Initialize the cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})

@reports_bp.route('/project/<int:project_id>/daily-report', methods=['GET'])
def project_daily_report(project_id):
    """Generates an HTML daily report for a specified project.
    
    This route retrieves project details and associated daily reports from the database,
    then renders an HTML template to display this information.

    Args:
        project_id (int): The ID of the project.

    Returns:
        Response: An HTML response containing the project's daily report,
                  or an error response if the project is not found or an error occurs.

    Raises:
        404: If the project with the given ID is not found.
        500: If any error occurs during the process of generating the report.
    """
    logger.info(f"Generating daily report for project {project_id}")
    cache_key = f'daily_report_{project_id}'
    cached_report = cache.get(cache_key)
    if cached_report:
        return cached_report
    try:
        project = Project.query.get(project_id)

        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")
        
        # Fetch daily reports with optimized query
        daily_reports = DailyReport.query.filter(DailyReport.project_id == project_id).order_by(DailyReport.report_date.asc()).all()
        # Prepare data for rendering in the HTML template
        
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
                'description': escape(project.description),
                'start_date': project.start_date.isoformat() if project.start_date else 'N/A',
                'end_date': project.end_date.isoformat() if project.end_date else 'N/A',
            },
            'daily_reports': [{ # Escape data to prevent XSS
                'report_number': escape(report.report_number),
                'report_date': escape(report.report_date.isoformat()),
                'weather_condition': report.weather_condition,
                'temperature_high': report.temperature_high,
                'temperature_low': report.temperature_low
            } for report in daily_reports]
        }

        report = render_template('reports/daily_report.html', report_data=report_data)
        cache.set(cache_key, report)
        return report
    except Exception as error:
        logger.error(f"An error occurred while generating the daily report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/monthly-report')
def project_monthly_report(project_id):
    """Generates a monthly report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        month = request.args.get('month')
        year = request.args.get('year')

        # Prepare data for rendering in the HTML template
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
            },
            'month': month,
            'year': year
        }

        return render_template('reports/monthly_report.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the monthly report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/project-status-report')
def project_status_report(project_id):
    """Generates a project status report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        # Prepare data for rendering in the HTML template
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
                'status': escape(project.status.value if project.status else 'N/A'),
                'start_date': project.start_date.isoformat() if project.start_date else 'N/A',
                'end_date': project.end_date.isoformat() if project.end_date else 'N/A'
            },
            'project_status_options': [e.value for e in ProjectStatusEnum]
        }

        return render_template('reports/project_status_report.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the project status report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/cost-report')
def project_cost_report(project_id):
    """Generates a cost report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        # Fetch change orders and invoices with optimized query
        change_orders = ChangeOrder.query.filter(ChangeOrder.project_id == project_id).all()
        invoices = Invoice.query.filter(Invoice.project_id == project_id).all()
        # Prepare data for rendering in the HTML template
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
            },
            'change_orders': [{ # Escape data to prevent XSS
                'number': escape(co.number),
                'title': escape(co.title),
                'amount': co.amount,
                'status': escape(co.status),
            } for co in change_orders],
            'invoices': [{ # Escape data to prevent XSS
                'invoice_number': escape(inv.invoice_number),
                'vendor': escape(inv.vendor),
                'amount': inv.amount,
                'status': escape(inv.status),
            } for inv in invoices],
        }

        return render_template('reports/cost_report.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the cost report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/safety-report')
def project_safety_report(project_id):
    """Generates a safety report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        # Fetch incidents and observations with optimized query
        incidents = SafetyIncident.query.filter(SafetyIncident.project_id == project_id).all()
        observations = SafetyObservation.query.filter(SafetyObservation.project_id == project_id).all()
        # Prepare data for rendering in the HTML template
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
            },
            'incidents': [{ # Escape data to prevent XSS
                'title': escape(incident.title),
                'type': escape(incident.type),
                'severity': escape(incident.severity),
                'incident_date': incident.incident_date.isoformat() if incident.incident_date else 'N/A',
            } for incident in incidents],
            'observations': [{ # Escape data to prevent XSS
                'title': escape(observation.title),
                'category': escape(observation.category),
                'severity': escape(observation.severity),
                'observation_date': observation.observation_date.isoformat() if observation.observation_date else 'N/A',
            } for observation in observations],
        }

        return render_template('reports/safety_report.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the safety report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/general-information-report')
def project_general_information_report(project_id):
    """Generates a general information report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        # Prepare data for rendering in the HTML template
        report_data = {
            'project': { # Escape data to prevent XSS
                'name': escape(project.name),
                'number': escape(project.number),
                'description': escape(project.description),
                'address': escape(project.address),
                'city': escape(project.city),
                'state': escape(project.state),
                'zip_code': escape(project.zip_code),
                'status': escape(project.status.value if project.status else 'N/A'),
                'start_date': project.start_date.isoformat() if project.start_date else 'N/A',
                'end_date': project.end_date.isoformat() if project.end_date else 'N/A',
                'owner': escape(project.owner),
            },
        }

        return render_template('reports/general_information_report.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the general information report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")

@reports_bp.route('/project/<int:project_id>/project-data-visualization')
def project_data_visualization(project_id):
    """Generates a data visualization report for a specified project."""
    try:
        project = Project.query.get(project_id)
        if not project:
            logger.warning(f"Project with ID {project_id} not found.")
            abort(404, description="Project not found")

        # Fetching related data for rendering in the HTML template
        daily_reports = DailyReport.query.filter(DailyReport.project_id == project_id).all()
        daily_reports_schema = DailyReportSchema(many=True)
        daily_reports_data = daily_reports_schema.dump(daily_reports)

        # Fetch change orders, invoices, incidents, and observations with optimized query
        change_orders = ChangeOrder.query.filter(ChangeOrder.project_id == project_id).all()
        invoices = Invoice.query.filter(Invoice.project_id == project_id).all()
        incidents = SafetyIncident.query.filter(SafetyIncident.project_id == project_id).all()
        observations = SafetyObservation.query.filter(SafetyObservation.project_id == project_id).all()

        # Prepare data for rendering
        report_data = {
            'project': {
                'name': escape(project.name),
                'number': escape(project.number),
            },
            'daily_reports': daily_reports_data,
            'change_orders': [{
                'number': escape(co.number),
                'amount': co.amount
            } for co in change_orders],
            'invoices': [{
                'invoice_number': escape(inv.invoice_number),
                'amount': inv.amount
            } for inv in invoices],
            'incidents': [{
                'title': escape(incident.title),
                'incident_date': incident.incident_date.isoformat() if incident.incident_date else 'N/A',
            } for incident in incidents],
            'observations': [{
                'title': escape(observation.title),
                'observation_date': observation.observation_date.isoformat() if observation.observation_date else 'N/A',
            } for observation in observations],
        }

        return render_template('reports/data_visualization.html', report_data=report_data)
    except Exception as error:
        logger.error(f"An error occurred while generating the data visualization report for project {project_id}: {error}")
        abort(500, description="An error occurred while generating the report.")