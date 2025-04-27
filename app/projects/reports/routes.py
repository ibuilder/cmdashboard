from flask import Blueprint, render_template, abort
from app.models.project import Project
from app.models.field import DailyReport

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/project/<int:project_id>/daily-report')
def project_daily_report(project_id):
    """
    Generates a basic HTML report with the project data and the daily reports for that project.

    Args:
        project_id: The ID of the project to generate the report for.

    Returns:
        An HTML response with the project report or an error if the project is not found.
    """
    project = Project.query.get(project_id)

    if not project:
        abort(404, description="Project not found")

    daily_reports = DailyReport.query.filter_by(project_id=project_id).order_by(DailyReport.report_date.asc()).all()

    # Prepare data for the template
    report_data = {
        'project': {
            'name': project.name,
            'number': project.number,
            'description': project.description,
            'start_date': project.start_date.isoformat() if project.start_date else 'N/A',
            'end_date': project.end_date.isoformat() if project.end_date else 'N/A'
        },
        'daily_reports': [{
            'report_number': report.report_number,
            'report_date': report.report_date.isoformat(),
            'weather_condition': report.weather_condition,
            'temperature_high': report.temperature_high,
            'temperature_low': report.temperature_low
        } for report in daily_reports]
    }

    return render_template('reports/daily_report.html', report_data=report_data)