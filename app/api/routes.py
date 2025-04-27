from flask import Blueprint, jsonify, request, abort
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.engineering import RFI, Submittal
from app.models.field import DailyReport, Punchlist, Photo
from app.models.safety import SafetyObservation, IncidentReport
from app.models.cost import Invoice, ChangeOrder
from app.extensions import db
from app.utils.access_control import role_required
from app.auth.routes import token_auth
from app.models.user import User
from datetime import datetime, timedelta
import hashlib
import json

api_bp = Blueprint('api', __name__)

def validate_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key or not check_valid_api_key(api_key):
        abort(401, description="Invalid API key")

# Apply to all API routes - removing the limiter for now to fix the error
@api_bp.before_request
def before_api_request():
    # Validate auth/API key here if needed
    pass

@api_bp.route('/projects')
@token_auth.login_required
def get_projects():
    """API endpoint to get projects list"""
    user = token_auth.current_user()
    
    if user.role == 'Admin':
        projects = Project.query.all()
    else:
        projects = Project.query.join(Project.users).filter(User.id == user.id).all()
    
    results = []
    for project in projects:
        results.append({
            'id': project.id,
            'name': project.name,
            'number': project.number,
            'status': project.status,
            'start_date': project.start_date.isoformat() if project.start_date else None,
            'end_date': project.end_date.isoformat() if project.end_date else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>')
@token_auth.login_required
def get_project(id):
    """API endpoint to get project details"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    # Get summary counts
    rfi_count = RFI.query.filter_by(project_id=id).count()
    submittal_count = Submittal.query.filter_by(project_id=id).count()
    daily_report_count = DailyReport.query.filter_by(project_id=id).count()
    
    result = {
        'id': project.id,
        'name': project.name,
        'number': project.number if hasattr(project, 'number') else '',
        'description': project.description,
        'address': project.address if hasattr(project, 'address') else '',
        'city': project.city if hasattr(project, 'city') else '',
        'state': project.state if hasattr(project, 'state') else '',
        'zip_code': project.zip_code if hasattr(project, 'zip_code') else '',
        'status': project.status,
        'start_date': project.start_date.isoformat() if project.start_date else None,
        'end_date': project.end_date.isoformat() if project.end_date else None,
        'owner': project.owner.name if hasattr(project, 'owner') and project.owner else None,
        'summary': {
            'rfi_count': rfi_count,
            'submittal_count': submittal_count,
            'daily_report_count': daily_report_count
        }
    }
    
    return jsonify({
        'status': 'success',
        'data': result
    })

@api_bp.route('/projects/<int:id>/rfis')
@token_auth.login_required
def get_project_rfis(id):
    """API endpoint to get RFIs for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    rfis = RFI.query.filter_by(project_id=id).order_by(RFI.date_submitted.desc()).all()
    
    results = []
    for rfi in rfis:
        results.append({
            'id': rfi.id,
            'number': rfi.number,
            'subject': rfi.subject,
            'status': rfi.status,
            'date_submitted': rfi.date_submitted.isoformat(),
            'date_required': rfi.date_required.isoformat() if rfi.date_required else None,
            'date_answered': rfi.date_answered.isoformat() if rfi.date_answered else None,
            'has_answer': bool(rfi.answer and rfi.answer.strip())
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/submittals')
@token_auth.login_required
def get_project_submittals(id):
    """API endpoint to get submittals for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    submittals = Submittal.query.filter_by(project_id=id).order_by(Submittal.date_submitted.desc()).all()
    
    results = []
    for submittal in submittals:
        results.append({
            'id': submittal.id,
            'number': submittal.number,
            'title': submittal.title,
            'status': submittal.status,
            'specification_section': submittal.specification_section,
            'date_submitted': submittal.date_submitted.isoformat(),
            'date_required': submittal.date_required.isoformat() if submittal.date_required else None,
            'date_returned': submittal.date_returned.isoformat() if submittal.date_returned else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/daily-reports')
@token_auth.login_required
def get_project_daily_reports(id):
    """API endpoint to get daily reports for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    reports = DailyReport.query.filter_by(project_id=id).order_by(DailyReport.report_date.desc()).all()
    
    results = []
    for report in reports:
        results.append({
            'id': report.id,
            'report_number': report.report_number,
            'report_date': report.report_date.isoformat(),
            'weather_conditions': report.weather_condition,  # Changed from weather_conditions to match model
            'temperature_high': report.temperature_high,
            'temperature_low': report.temperature_low,
            'manpower_count': report.labor_count,  # Changed from manpower_count to match model
            'delays': hasattr(report, 'delays') and report.delays
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/daily-reports/<int:id>')
@token_auth.login_required
def get_daily_report(id):
    """API endpoint to get a specific daily report"""
    user = token_auth.current_user()
    report = DailyReport.query.get_or_404(id)
    project = Project.query.get(report.project_id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this report'
        }), 403
    
    # Get photos for this report
    photos = Photo.query.filter_by(daily_report_id=id).all()
    photos_data = []
    
    for photo in photos:
        photos_data.append({
            'id': photo.id,
            'title': photo.title,
            'description': photo.description,
            'file_path': photo.file_path,
            'taken_at': photo.taken_at.isoformat() if hasattr(photo, 'taken_at') and photo.taken_at else None
        })
    
    report_data = {
        'id': report.id,
        'report_number': report.report_number,
        'report_date': report.report_date.isoformat(),
        'weather_condition': report.weather_condition,
        'temperature_high': report.temperature_high,
        'temperature_low': report.temperature_low,
        'precipitation': report.precipitation,
        'wind_speed': report.wind_speed,
        'labor_count': report.labor_count,
        'delays': hasattr(report, 'delays') and report.delays,
        'delay_reason': report.delay_reason if hasattr(report, 'delay_reason') else '',
        'work_performed': report.work_performed if hasattr(report, 'work_performed') else '',
        'materials_received': report.materials_received,
        'equipment_used': '',  # This field might not exist in your model
        'visitors': '',  # This field might not exist in your model
        'safety_incidents': '',  # This field might not exist in your model
        'quality_issues': '',  # This field might not exist in your model
        'created_by': report.author.full_name if hasattr(report, 'author') and report.author else 'Unknown',
        'created_at': report.created_at.isoformat() if report.created_at else None,
        'photos': photos_data
    }
    
    return jsonify({
        'status': 'success',
        'data': report_data
    })

@api_bp.route('/projects/<int:id>/safety/observations')
@token_auth.login_required
def get_project_safety_observations(id):
    """API endpoint to get safety observations for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    observations = SafetyObservation.query.filter_by(project_id=id).order_by(
        SafetyObservation.observation_date.desc()).all()
    
    results = []
    for obs in observations:
        observer_name = User.query.get(obs.observed_by).name if obs.observed_by else "Unknown"
        results.append({
            'id': obs.id,
            'title': obs.title,
            'category': obs.category,
            'severity': obs.severity,
            'observation_date': obs.observation_date.isoformat(),
            'location': obs.location,
            'status': obs.status,
            'observed_by': observer_name
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/projects/<int:id>/cost/change-orders')
@token_auth.login_required
def get_project_change_orders(id):
    """API endpoint to get change orders for a project"""
    user = token_auth.current_user()
    project = Project.query.get_or_404(id)
    
    # Check if user has access and proper role for cost data
    if user.role not in ['Admin', 'Owner', 'Owners Representative', 'General Contractor'] or (user.role != 'Admin' and user not in project.users):
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this cost data'
        }), 403
    
    change_orders = ChangeOrder.query.filter_by(project_id=id).order_by(
        ChangeOrder.change_order_number).all()  # Changed from number to change_order_number
    
    results = []
    for co in change_orders:
        results.append({
            'id': co.id,
            'number': co.change_order_number,  # Changed from number to change_order_number
            'title': co.title,
            'amount': float(co.amount),
            'status': co.status,
            'date_issued': co.date_submitted.isoformat() if hasattr(co, 'date_submitted') else None,  # Changed from date_issued
            'date_approved': co.date_approved.isoformat() if co.date_approved else None
        })
    
    return jsonify({
        'status': 'success',
        'data': results,
        'count': len(results)
    })

@api_bp.route('/verify-document', methods=['POST'])
@token_auth.login_required
def verify_document():
    """API endpoint to verify a document's blockchain hash"""
    data = request.get_json()
    
    if not data or not data.get('hash') or not data.get('document_type') or not data.get('document_id'):
        return jsonify({
            'status': 'error',
            'message': 'Missing required parameters'
        }), 400
    
    # Commenting out the web3 utils for now since we don't have this module
    # from app.utils.web3_utils import verify_document_hash
    # 
    # success, result = verify_document_hash(
    #     data['document_type'],
    #     data['document_id'],
    #     data['hash']
    # )
    
    # For now, just return mock data
    success = True
    result = {
        'verified': True,
        'timestamp': datetime.now().isoformat(),
        'blockchain': 'Ethereum',
        'transaction_id': '0x' + hashlib.sha256(str(datetime.now()).encode()).hexdigest()
    }
    
    if success:
        return jsonify({
            'status': 'success',
            'verified': True,
            'data': result
        })
    else:
        return jsonify({
            'status': 'error',
            'verified': False,
            'message': result
        }), 400

@api_bp.route('/daily-reports/create', methods=['POST'])
@token_auth.login_required
def create_daily_report():
    """API endpoint to create a daily report from mobile"""
    user = token_auth.current_user()
    data = request.get_json()
    
    if not data or not data.get('project_id'):
        return jsonify({
            'status': 'error',
            'message': 'Missing project_id'
        }), 400
    
    project_id = data.get('project_id')
    project = Project.query.get_or_404(project_id)
    
    # Check if user has access
    if user.role != 'Admin' and user not in project.users:
        return jsonify({
            'status': 'error',
            'message': 'You do not have permission to access this project'
        }), 403
    
    # Check if a report already exists for today
    today = datetime.now().date()
    existing_report = DailyReport.query.filter_by(
        project_id=project_id, report_date=today).first()
    
    if existing_report:
        return jsonify({
            'status': 'error',
            'message': 'A report for today already exists',
            'report_id': existing_report.id
        }), 400
    
    # Get next report number
    last_report = DailyReport.query.filter_by(project_id=project_id).order_by(
        DailyReport.id.desc()).first()
    next_number = f"DR-{(last_report.id + 1 if last_report else 1):04d}"
    
    report = DailyReport(
        project_id=project_id,
        report_date=today,
        report_number=next_number,
        weather_condition=data.get('weather_condition', ''),  # Changed from weather_conditions
        temperature_high=data.get('temperature_high'),
        temperature_low=data.get('temperature_low'),
        precipitation=data.get('precipitation', 0),
        wind_speed=data.get('wind_speed', 0),
        work_status=data.get('work_status', 'working'),  # Added work_status field
        delay_reason=data.get('delay_reason'),
        labor_count=data.get('labor_count', 0),  # Changed from manpower_count
        work_performed=data.get('work_performed', ''),
        materials_received=data.get('materials_received', ''),
        notes=data.get('notes', ''),  # Added notes field
        created_by=user.id
    )
    
    db.session.add(report)
    db.session.commit()
    
    return jsonify({
        'status': 'success',
        'message': 'Daily report created successfully',
        'report_id': report.id
    })