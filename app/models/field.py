# app/models/field.py

from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment
from enum import Enum
import json
import uuid
import os

class WeatherCondition(str, Enum):
    SUNNY = 'sunny'
    PARTLY_CLOUDY = 'partly_cloudy'
    CLOUDY = 'cloudy'
    RAINY = 'rainy'
    STORMY = 'stormy'
    SNOWY = 'snowy'
    FOGGY = 'foggy'
    WINDY = 'windy'

class WorkStatus(str, Enum):
    WORKING = 'working'
    DELAYED = 'delayed'
    HALTED = 'halted'

class DailyReport(db.Model):
    """Daily report model for field operations"""
    __tablename__ = 'daily_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    report_number = db.Column(db.String(50))
    report_date = db.Column(db.Date, default=datetime.utcnow().date)
    manpower_entries = db.relationship('ManpowerEntry', back_populates='daily_report', lazy='dynamic')
    # Weather information
    weather_condition = db.Column(db.String(20))
    temperature_low = db.Column(db.Float)
    temperature_high = db.Column(db.Float)
    precipitation = db.Column(db.Float)  # in inches
    wind_speed = db.Column(db.Float)  # in mph
    
    # Site conditions
    site_conditions = db.Column(db.Text)
    work_status = db.Column(db.String(20), default=WorkStatus.WORKING.value)
    delay_reason = db.Column(db.Text)
    
    # Labor and equipment
    labor_count = db.Column(db.Integer, default=0)
    labor_hours = db.Column(db.Float, default=0)
    equipment_count = db.Column(db.Integer, default=0)
    
    # Work performed
    work_performed = db.Column(db.Text)
    materials_received = db.Column(db.Text)
    
    # Issues and notes
    issues = db.Column(db.Text)
    notes = db.Column(db.Text)
    
    # Status
    is_submitted = db.Column(db.Boolean, default=False)
    submitted_at = db.Column(db.DateTime)
    
    # Meta information
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('daily_reports', lazy='dynamic'))
    author = db.relationship('User', foreign_keys=[created_by])
    
    photos = db.relationship('ProjectPhoto', backref='daily_report', lazy='dynamic')
    labor_entries = db.relationship('LaborEntry', backref='daily_report', lazy='dynamic')
    equipment_entries = db.relationship('EquipmentEntry', backref='daily_report', lazy='dynamic')
    project = db.relationship('Project', backref=db.backref('daily_reports', lazy='dynamic'))
    author = db.relationship('User', foreign_keys=[created_by])
    photos = db.relationship('ProjectPhoto', backref='daily_report', lazy='dynamic')
    labor_entries = db.relationship('LaborEntry', backref='daily_report', lazy='dynamic')
    equipment_entries = db.relationship('EquipmentEntry', backref='daily_report', lazy='dynamic')
    def __repr__(self):
        return f'<DailyReport {self.report_number} - {self.report_date}>'

class LaborEntry(db.Model):
    __tablename__ = 'labor_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=False)
    company = db.Column(db.String(100))
    work_description = db.Column(db.String(255))
    worker_count = db.Column(db.Integer)
    hours_worked = db.Column(db.Float)
    
    def __repr__(self):
        return f'<LaborEntry {self.company} - {self.worker_count} workers>'

class EquipmentEntry(db.Model):
    __tablename__ = 'equipment_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=False)
    equipment_type = db.Column(db.String(100))
    count = db.Column(db.Integer)
    hours_used = db.Column(db.Float)
    notes = db.Column(db.String(255))
    
    def __repr__(self):
        return f'<EquipmentEntry {self.equipment_type} - {self.count} units>'
class ProjectPhoto(db.Model):
    __tablename__ = 'project_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    location = db.Column(db.String(100))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    is_featured = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('project_photos', lazy='dynamic'))
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
   
    
    def __repr__(self):
        return f'<ProjectPhoto {self.id} - {self.title}>'

class SafetyIncident(db.Model):
    __tablename__ = 'safety_incidents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    incident_date = db.Column(db.Date, default=datetime.utcnow().date)
    incident_time = db.Column(db.Time)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    severity = db.Column(db.String(20))  # minor, serious, critical
    type = db.Column(db.String(50))  # near miss, first aid, injury, property damage
    involved_parties = db.Column(db.Text)
    witnesses = db.Column(db.Text)
    actions_taken = db.Column(db.Text)
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reported_at = db.Column(db.DateTime, default=func.now())
    
    # Status fields
    is_reviewed = db.Column(db.Boolean, default=False)
    reviewed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    reviewed_at = db.Column(db.DateTime)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('safety_incidents', lazy='dynamic'))
    reporter = db.relationship('User', foreign_keys=[reported_by])
    reviewer = db.relationship('User', foreign_keys=[reviewed_by])
    
    
    def __repr__(self):
        return f'<SafetyIncident {self.id} - {self.title}>'

class DailyReportPhoto(db.Model):
    """Photos attached to daily reports"""
    __tablename__ = 'daily_report_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_photos')
    
    def __repr__(self):
        return f"<DailyReportPhoto {self.id}>"
    
    @property
    def url(self):
        from flask import url_for
        return url_for('static', filename=f'uploads/{self.file_path}')




class WorkActivity(db.Model):
    """Work activities tracked on the project"""
    __tablename__ = 'work_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    percentage_complete = db.Column(db.Integer, default=0)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='work_activities')
    creator = db.relationship('User', backref='created_activities')
    
    def __repr__(self):
        return f"<WorkActivity {self.activity_type}>"


class Photo(db.Model):
    """Photo model for field documentation"""
    __tablename__ = 'photos'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=True)
    filename = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='photos')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'daily_report_id': self.daily_report_id,
            'filename': self.filename,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'created_by': self.created_by
        }

class Punchlist(db.Model):
    """Punchlist model for tracking outstanding items"""
    __tablename__ = 'punchlists'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    punchlist_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    area = db.Column(db.String(100))
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='punchlists')
    creator = db.relationship('User', foreign_keys=[created_by])
    items = db.relationship('PunchlistItem', backref='punchlist', cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Punchlist, self).__init__(**kwargs)
        if not self.punchlist_number:
            # Generate a unique punchlist number
            import uuid
            self.punchlist_number = f"PL-{uuid.uuid4().hex[:8].upper()}"

class PunchlistItem(db.Model):
    """Individual item in a punchlist"""
    __tablename__ = 'punchlist_items'
    
    id = db.Column(db.Integer, primary_key=True)
    punchlist_id = db.Column(db.Integer, db.ForeignKey('punchlists.id'), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    responsible_party = db.Column(db.String(100))
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    due_date = db.Column(db.Date)
    photo = db.Column(db.String(255))
    status = db.Column(db.String(20), default='open')  # open, closed
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    closed_at = db.Column(db.DateTime)
    closed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])
    closer = db.relationship('User', foreign_keys=[closed_by])

    def __repr__(self):
        return f"<PunchlistItem {self.id}: {self.title}>"
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'title': self.title,
            'description': self.description,
            'location': self.location,
            'responsible_party': self.responsible_party,
            'due_date': self.due_date.isoformat() if self.due_date else None,
            'priority': self.priority,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'created_by': self.created_by
        }

class Checklist(db.Model):
    """Checklist model for inspections and quality control"""
    __tablename__ = 'checklists'
    
    id = db.Column(db.Integer, primary_key=True)  # Fixed 'primary key=' to 'primary_key='
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    checklist_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    location = db.Column(db.String(100))
    items = db.Column(db.Text)  # JSON list of items
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='checklists')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __init__(self, **kwargs):
        super(Checklist, self).__init__(**kwargs)
        if not self.checklist_number:
            # Generate a unique checklist number
            import uuid
            self.checklist_number = f"CL-{uuid.uuid4().hex[:8].upper()}"
        
        # Convert items from text to JSON if needed
        if 'items' in kwargs and isinstance(kwargs['items'], str):
            import json
            try:
                self.items = json.dumps(json.loads(kwargs['items']))
            except:
                self.items = json.dumps([])

class Schedule(db.Model):
    """Schedule model for field activities"""
    __tablename__ = 'schedules'
    
    id = db.Column(db.Integer, primary_key=True)  # Fixed syntax
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    scheduled_date = db.Column(db.Date, nullable=False, index=True)
    start_time = db.Column(db.Time)
    end_time = db.Column(db.Time)
    location = db.Column(db.String(100))
    category = db.Column(db.String(50))  # meeting, inspection, milestone, etc.
    priority = db.Column(db.String(20), default='medium')  # low, medium, high, critical
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='field_schedules')
    creator = db.relationship('User', foreign_keys=[created_by])

class PullPlan(db.Model):
    """Pull planning model for collaborative scheduling"""
    __tablename__ = 'pull_plans'
    
    id = db.Column(db.Integer, primary_key=True)  # Fixed syntax
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    location = db.Column(db.String(100))
    participants = db.Column(db.Text)  # JSON list of participants
    activities = db.Column(db.Text)  # JSON representation of activities
    
    # Metadata
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='pull_plans')
    creator = db.relationship('User', foreign_keys=[created_by])

class ManpowerEntry(db.Model):
    __tablename__ = 'manpower_entries'
    
    id = db.Column(db.Integer, primary_key=True)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    trade = db.Column(db.String(100))
    personnel_count = db.Column(db.Integer, default=0)
    hours_worked = db.Column(db.Float, default=0.0)
    work_description = db.Column(db.Text)
    
    # Relationships
    daily_report = db.relationship('DailyReport', back_populates='manpower_entries')
    
    def __repr__(self):
        return f'<ManpowerEntry {self.company_name} - {self.personnel_count} workers>'

class FieldPhoto(db.Model):
    __tablename__ = 'field_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    daily_report_id = db.Column(db.Integer, db.ForeignKey('daily_reports.id'))
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # in bytes
    file_type = db.Column(db.String(50))
    location = db.Column(db.String(255))
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    taken_at = db.Column(db.DateTime)
    uploaded_at = db.Column(db.DateTime, default=func.now())
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='field_photos')
    daily_report = db.relationship('DailyReport', backref='field_photos')
    uploader = db.relationship('User', foreign_keys=[uploaded_by])
    
    def __repr__(self):
        return f'<FieldPhoto {self.id} - {self.title}>'
    
    def to_dict(self):
        return {
            'id': self.id,
            'project_id': self.project_id,
            'daily_report_id': self.daily_report_id,
            'title': self.title,
            'description': self.description,
            'file_path': self.file_path,
            'file_name': self.file_name,
            'location': self.location,
            'uploaded_at': self.uploaded_at.isoformat() if self.uploaded_at else None,
            'uploaded_by': self.uploaded_by
        }
    
    @property
    def url(self):
        from flask import url_for
        return url_for('static', filename=f'uploads/photos/{self.file_name}')

# Association table for punchlist items and photos
punchlist_photos = db.Table('punchlist_photos',
    db.Column('punchlist_item_id', db.Integer, db.ForeignKey('punchlist_items.id'), primary_key=True),
    db.Column('field_photo_id', db.Integer, db.ForeignKey('field_photos.id'), primary_key=True)
)

class FieldInspection(db.Model):
    __tablename__ = 'field_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    inspection_date = db.Column(db.Date, nullable=False)
    inspection_type = db.Column(db.String(100), nullable=False)
    inspector = db.Column(db.String(100))
    agency = db.Column(db.String(100))
    result = db.Column(db.String(20))  # pass, pass_with_comments, fail
    notes = db.Column(db.Text)
    followup_required = db.Column(db.Boolean, default=False)
    followup_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='inspections')
    creator = db.relationship('User', foreign_keys=[created_by])
   
    def __repr__(self):
        return f'<FieldInspection {self.inspection_type} - {self.inspection_date}>'