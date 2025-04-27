# app/dashboard/routes.py
from flask import Blueprint, render_template, redirect, url_for, current_app, jsonify
from flask_login import login_required, current_user
from app.models.project import Project
from app.models.user import User
from app.models.engineering import RFI, Submittal
from app.models.field import DailyReport, Punchlist
from app.models.safety import SafetyObservation, IncidentReport
from app.models.cost import Invoice, PotentialChangeOrder, ChangeOrder
from app.extensions import db, cache
from datetime import datetime, timedelta
from sqlalchemy import func

# Create dashboard blueprint with explicit name and url_prefix
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/', template_folder='templates')

@dashboard_bp.route('/', methods=['GET'])
@dashboard_bp.route('/index', methods=['GET'])
@login_required
def index():
    """Main dashboard page"""
    # Get user's projects (with fallback)
    print("Fetching user projects...")
    try:
        user_projects = [pu.project for pu in current_user.projects.all()] if hasattr(current_user, 'projects') else []
    except Exception as e:
        current_app.logger.error(f"Error fetching user projects: {e}")
        user_projects = []
    
    # Get recent activity (sample implementation)
    recent_activity = []
    try:
        # Fetch recent RFIs
        recent_rfis = RFI.query.filter(
            RFI.created_at > datetime.utcnow() - timedelta(days=7)
        ).limit(5).all()
        recent_activity.extend(recent_rfis)
        
        # Fetch recent daily reports
        recent_reports = DailyReport.query.filter(
            DailyReport.date > datetime.utcnow() - timedelta(days=7)
        ).limit(5).all()
        recent_activity.extend(recent_reports)
    except Exception as e:
        current_app.logger.error(f"Error fetching recent activity: {e}")
    
    # Get important notifications (sample implementation)
    notifications = []
    try:
        # Fetch overdue RFIs
        overdue_rfis = RFI.query.filter(
            RFI.due_date < datetime.utcnow(),
            RFI.status != 'closed'
        ).limit(3).all()
        notifications.extend(overdue_rfis)
        
        # Fetch safety observations requiring attention
        urgent_safety_obs = SafetyObservation.query.filter(
            SafetyObservation.severity == 'high',
            SafetyObservation.status != 'resolved'
        ).limit(3).all()
        notifications.extend(urgent_safety_obs)
    except Exception as e:
        current_app.logger.error(f"Error fetching notifications: {e}")
    
    # Get upcoming deadlines (sample implementation)
    upcoming_deadlines = []
    try:
        # Fetch upcoming RFI deadlines
        upcoming_rfi_deadlines = RFI.query.filter(
            RFI.due_date.between(
                datetime.utcnow(), 
                datetime.utcnow() + timedelta(days=30)
            ),
            RFI.status != 'closed'
        ).limit(5).all()
        upcoming_deadlines.extend(upcoming_rfi_deadlines)
        
        # Fetch upcoming submittal deadlines
        upcoming_submittal_deadlines = Submittal.query.filter(
            Submittal.due_date.between(
                datetime.utcnow(), 
                datetime.utcnow() + timedelta(days=30)
            ),
            Submittal.status != 'closed'
        ).limit(5).all()
        upcoming_deadlines.extend(upcoming_submittal_deadlines)
    except Exception as e:
        current_app.logger.error(f"Error fetching upcoming deadlines: {e}")
    
    # Calculate stats for dashboard
    stats = {}
    try:
        # Project stats
        stats['total_projects'] = Project.query.count()
        stats['active_projects'] = Project.query.filter_by(status='active').count()
        
        # RFI stats
        stats['rfis_open'] = RFI.query.filter_by(status='open').count()
        
        # Submittal stats
        stats['submittals_pending'] = Submittal.query.filter_by(status='pending').count()
        
        # Punchlist stats
        stats['punchlist_items'] = Punchlist.query.filter_by(status='open').count()
        
        # Change Order stats
        from sqlalchemy import func
        stats['change_order_value'] = db.session.query(
            func.sum(ChangeOrder.amount)
        ).filter_by(status='approved').scalar() or 0
    except Exception as e:
        current_app.logger.error(f"Error calculating stats: {e}")
        # Provide default values if error occurs
        stats = {
            'total_projects': 0,
            'active_projects': 0,
            'rfis_open': 0,
            'submittals_pending': 0,
            'punchlist_items': 0,
            'change_order_value': 0
        }
    
    # Data for charts
    try:
        # Project status chart data
        status_query = db.session.query(
            Project.status, 
            func.count(Project.id)
        ).group_by(Project.status).all()
        
        status_labels = [status.replace('_', ' ').title() for status, _ in status_query]
        status_data = [count for _, count in status_query]
        chart_colors = [
            'rgba(75, 192, 192, 0.8)',
            'rgba(54, 162, 235, 0.8)',
            'rgba(255, 206, 86, 0.8)',
            'rgba(255, 99, 132, 0.8)',
            'rgba(153, 102, 255, 0.8)'
        ]
        
        # Activity trend data (last 30 days)
        today = datetime.utcnow().date()
        date_range = [(today - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(30)]
        date_range.reverse()  # Oldest to newest
        
        # Sample activity data (in real app, you'd query from DB)
        activity_data = {
            'dates': date_range,
            'rfis': [0] * 30,  # Placeholder data
            'submittals': [0] * 30,  # Placeholder data
            'reports': [0] * 30   # Placeholder data
        }
        
        # Fill in with some random data for demonstration
        import random
        for i in range(30):
            activity_data['rfis'][i] = random.randint(0, 5)
            activity_data['submittals'][i] = random.randint(0, 4)
            activity_data['reports'][i] = random.randint(0, 8)
            
    except Exception as e:
        current_app.logger.error(f"Error preparing chart data: {e}")
        # Provide default empty data
        status_labels = []
        status_data = []
        chart_colors = []
        activity_data = {'dates': [], 'rfis': [], 'submittals': [], 'reports': []}
    
    # Recent items for tables
    try:
        recent_rfis = RFI.query.order_by(RFI.created_at.desc()).limit(5).all()
        recent_reports = DailyReport.query.order_by(DailyReport.date.desc()).limit(5).all()
    except Exception as e:
        current_app.logger.error(f"Error fetching recent items: {e}")
        recent_rfis = []
        recent_reports = []
    
    return render_template('dashboard/index.html',
                          projects=user_projects,
                          activity=recent_activity,
                          notifications=notifications,
                          deadlines=upcoming_deadlines,
                          stats=stats,
                          status_labels=status_labels,
                          status_data=status_data,
                          chart_colors=chart_colors,
                          activity_data=activity_data,
                          recent_rfis=recent_rfis,
                          recent_reports=recent_reports)

@dashboard_bp.route('/my-tasks')
@login_required
def my_tasks():
    """Dashboard showing tasks assigned to the current user"""
    # Use try-except to handle potential missing columns
    try:
        # First try with assigned_to field
        from app.models.engineering import RFI, Submittal
        from app.models.field import Punchlist
        
        assigned_rfis = RFI.query.filter_by(assigned_to=current_user.id, status='open').all()
    except Exception as e:
        # Fall back to using submitted_by if assigned_to doesn't exist
        try:
            from app.models.engineering import RFI
            assigned_rfis = RFI.query.filter_by(submitted_by=current_user.id, status='open').all()
        except Exception:
            assigned_rfis = []
    
    try:
        # First try with assigned_to field
        from app.models.engineering import Submittal
        assigned_submittals = Submittal.query.filter_by(assigned_to=current_user.id, status='pending').all()
    except Exception:
        # Fall back to using submitted_by if assigned_to doesn't exist
        try:
            from app.models.engineering import Submittal
            assigned_submittals = Submittal.query.filter_by(submitted_by=current_user.id, status='pending').all()
        except Exception:
            assigned_submittals = []
    
    # For punchlist, use a safer approach
    try:
        from app.models.field import Punchlist
        assigned_punchlists = Punchlist.query.filter_by(status='open').all()
    except Exception:
        assigned_punchlists = []
    
    return render_template('dashboard/my_tasks.html',
                           assigned_rfis=assigned_rfis,
                           assigned_submittals=assigned_submittals,
                           assigned_punchlists=assigned_punchlists)

@dashboard_bp.route('/check-schema')
@login_required
def check_schema():
    """Debug route to check database schema"""
    from sqlalchemy import inspect
    from flask import jsonify
    
    inspector = inspect(db.engine)
    
    # Check RFI table columns
    rfi_columns = [column['name'] for column in inspector.get_columns('rfis')]
    has_rfi_assigned_to = 'assigned_to' in rfi_columns
    
    # Check Submittal table columns
    submittal_columns = [column['name'] for column in inspector.get_columns('submittals')]
    has_submittal_assigned_to = 'assigned_to' in submittal_columns
    
    return jsonify({
        'rfis': {
            'columns': rfi_columns,
            'has_assigned_to': has_rfi_assigned_to
        },
        'submittals': {
            'columns': submittal_columns,
            'has_assigned_to': has_submittal_assigned_to
        }
    })
@dashboard_bp.route('/profile')
@login_required
def profile():
    """User profile page"""
    return render_template('dashboard/profile.html')