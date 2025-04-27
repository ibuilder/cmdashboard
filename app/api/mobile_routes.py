from flask import Blueprint, jsonify, request, current_app
from app.extensions import db, limiter
from flask_login import current_user
from app.models.user import User
from app.models.project import Project
from datetime import datetime, timedelta
import jwt

mobile_bp = Blueprint('mobile_api', __name__)

# API Key Authentication
def verify_api_key():
    api_key = request.headers.get('X-API-Key')
    if not api_key:
        return None
    
    user = User.query.filter_by(api_key=api_key, is_active=True).first()
    return user

# JWT Authentication
def create_token(user_id):
    """Create a JWT token for a user"""
    expiration = datetime.utcnow() + current_app.config.get('JWT_TOKEN_EXPIRATION', timedelta(hours=1))
    payload = {
        'exp': expiration,
        'iat': datetime.utcnow(),
        'sub': user_id
    }
    token = jwt.encode(
        payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )
    return token

def verify_token(token):
    """Verify a JWT token and return the user ID"""
    try:
        payload = jwt.decode(
            token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )
        user_id = payload['sub']
        return User.query.get(user_id)
    except jwt.ExpiredSignatureError:
        return None  # Token expired
    except jwt.InvalidTokenError:
        return None  # Invalid token

@mobile_bp.route('/login', methods=['POST'])
@limiter.limit("10 per minute")
def login():
    """Mobile app login endpoint"""
    data = request.get_json() or {}
    
    if 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    if user is None or not user.verify_password(data['password']):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Account is disabled'}), 403
    
    # Update last seen
    user.last_seen = datetime.utcnow()
    db.session.commit()
    
    # Generate token
    token = create_token(user.id)
    
    return jsonify({
        'token': token,
        'user': user.to_dict(),
        'expires': (datetime.utcnow() + current_app.config.get('JWT_TOKEN_EXPIRATION', timedelta(hours=1))).isoformat()
    })

@mobile_bp.route('/projects', methods=['GET'])
def get_projects():
    """Get projects accessible to the user"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    # Get user's projects
    user_projects = [pu.project.to_dict() for pu in user.projects.all()]
    
    return jsonify({
        'projects': user_projects,
        'timestamp': datetime.utcnow().isoformat()
    })

@mobile_bp.route('/sync', methods=['POST'])
def sync_data():
    """Synchronize data between mobile app and server"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json() or {}
    
    # Process incoming sync data (implementation needed)
    
    # Return updated data
    max_days = current_app.config.get('MOBILE_SYNC_MAX_DAYS', 30)
    since_date = datetime.utcnow() - timedelta(days=max_days)
    
    # Get data to sync (implementation needed)
    sync_data = {
        'projects': [],
        'daily_reports': [],
        'safety_observations': [],
        'timestamp': datetime.utcnow().isoformat()
    }
    
    return jsonify(sync_data)

@mobile_bp.route('/upload-photo', methods=['POST'])
@limiter.limit("10 per minute")
def upload_photo():
    """Upload photo from mobile app"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('image') or not data.get('project_id'):
        return jsonify({
            'success': False,
            'error': 'Missing required parameters'
        }), 400
    
    result = save_mobile_photo(
        data.get('image'), 
        data.get('project_id'),
        data.get('record_type'),
        data.get('record_id')
    )
    
    return jsonify(result)

@mobile_bp.route('/sync-reports', methods=['POST'])
@limiter.limit("10 per minute")
def sync_reports():
    """Sync offline daily reports"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not isinstance(data.get('reports'), list):
        return jsonify({
            'success': False,
            'error': 'Invalid data format'
        }), 400
    
    results = process_offline_daily_reports(data.get('reports'), user.id)
    return jsonify(results)

@mobile_bp.route('/notification-preferences', methods=['GET'])
@limiter.limit("10 per minute")
def get_notifications():
    """Get user notification preferences"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    preferences = get_user_notification_preferences(user.id)
    return jsonify(preferences)

@mobile_bp.route('/notification-preferences', methods=['POST'])
@limiter.limit("10 per minute")
def update_notifications():
    """Update user notification preferences"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'error': 'Missing preferences data'
        }), 400
    
    result = update_user_notification_preferences(user.id, data)
    return jsonify(result)

@mobile_bp.route('/register-device', methods=['POST'])
@limiter.limit("10 per minute")
def register_device():
    """Register device for push notifications"""
    user = verify_api_key() or verify_token(request.headers.get('Authorization', '').replace('Bearer ', ''))
    
    if not user:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    
    if not data or not data.get('token') or not data.get('platform'):
        return jsonify({
            'success': False,
            'error': 'Missing required parameters'
        }), 400
    
    result = register_device_token(user.id, data.get('token'), data.get('platform'))
    return jsonify(result)