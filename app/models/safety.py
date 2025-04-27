# app/models/safety.py
from datetime import datetime
from app.extensions import db
from sqlalchemy.sql import func
from enum import Enum

class SafetySeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class SafetyStatus(str, Enum):
    DRAFT = "draft"
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    VERIFIED = "verified"

class IncidentType(str, Enum):
    NEAR_MISS = "near_miss"
    FIRST_AID = "first_aid"
    MEDICAL_TREATMENT = "medical_treatment"
    LOST_TIME = "lost_time"
    FATALITY = "fatality"
    PROPERTY_DAMAGE = "property_damage"
    ENVIRONMENTAL = "environmental"
    VEHICLE = "vehicle"
    OTHER = "other"

class ObservationType(str, Enum):
    UNSAFE_ACT = "unsafe_act"
    UNSAFE_CONDITION = "unsafe_condition"
    ENVIRONMENTAL = "environmental"
    NEAR_MISS = "near_miss"
    SAFETY_VIOLATION = "safety_violation"
    POSITIVE_OBSERVATION = "positive_observation"
    OTHER = "other"

class SafetyObservation(db.Model):
    """Safety observations recorded on site"""
    __tablename__ = 'safety_observations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    observation_date = db.Column(db.Date, default=datetime.utcnow().date)
    location = db.Column(db.String(100))
    category = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    status = db.Column(db.String(20), default='open')
    
    # Actions and follow up
    corrective_action = db.Column(db.Text)
    due_date = db.Column(db.Date)
    closed_date = db.Column(db.Date)
    closed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Meta information
    observed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('safety_observations', lazy='dynamic'))
    observer = db.relationship('User', foreign_keys=[observed_by], backref='observations')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_observations')
    closer = db.relationship('User', foreign_keys=[closed_by], backref='closed_observations')
    photos = db.relationship(
        'SafetyPhoto',
        primaryjoin="and_(SafetyPhoto.record_type=='observation', "
                "foreign(SafetyPhoto.record_id)==SafetyObservation.id)",
        backref='observation',
        lazy='dynamic'
    )
    
    def __repr__(self):
        return f'<SafetyObservation {self.id}: {self.title}>'

class IncidentReport(db.Model):
    """Safety incident reports"""
    __tablename__ = 'incident_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    incident_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    incident_date = db.Column(db.Date, default=datetime.utcnow().date)
    incident_time = db.Column(db.Time)
    location = db.Column(db.String(100))
    
    # Classification
    incident_type = db.Column(db.String(50))
    severity = db.Column(db.String(20))
    
    # Details
    injured_person = db.Column(db.String(100))
    injured_person_company = db.Column(db.String(100))
    body_part = db.Column(db.String(50))
    injury_type = db.Column(db.String(50))
    treatment = db.Column(db.String(100))
    work_related = db.Column(db.Boolean, default=True)
    spill_type = db.Column(db.String(100))
    spill_amount = db.Column(db.String(50))
    containment_measures = db.Column(db.Text)
    property_damaged = db.Column(db.String(100))
    damage_description = db.Column(db.Text)
    estimated_cost = db.Column(db.Float)
    
    # Recordability & reporting
    is_recordable = db.Column(db.Boolean, default=False)
    is_lost_time = db.Column(db.Boolean, default=False)
    days_restricted = db.Column(db.Integer, default=0)
    days_away = db.Column(db.Integer, default=0)
    
    # Root cause analysis
    immediate_causes = db.Column(db.Text)
    root_causes = db.Column(db.Text)
    corrective_actions = db.Column(db.Text)
    
    # Status
    status = db.Column(db.String(20), default='open')
    reported_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    investigated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    investigation_date = db.Column(db.Date)
    investigation_report = db.Column(db.Text)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('incidents', lazy='dynamic'))
    reporter = db.relationship('User', foreign_keys=[reported_by], backref='reported_incidents')
    investigator = db.relationship('User', foreign_keys=[investigated_by], backref='investigated_incidents')
    photos = db.relationship('IncidentPhoto', backref='incident', lazy='dynamic')
    
    def __repr__(self):
        return f'<IncidentReport {self.incident_number}: {self.title}>'

class IncidentPhoto(db.Model):
    """Photos attached to incident reports"""
    __tablename__ = 'incident_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    incident_id = db.Column(db.Integer, db.ForeignKey('incident_reports.id'), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    caption = db.Column(db.String(255))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_incident_photos')
    
    def __repr__(self):
        return f'<IncidentPhoto {self.id} for Incident {self.incident_id}>'

class SafetyPhoto(db.Model):
    """Photos attached to various safety records"""
    __tablename__ = 'safety_photos'
    
    id = db.Column(db.Integer, primary_key=True)
    record_type = db.Column(db.String(50), nullable=False)  # 'observation', 'jha', etc.
    record_id = db.Column(db.Integer, nullable=False)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(255), nullable=False)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploader = db.relationship('User', backref='uploaded_safety_photos')
    
    def __repr__(self):
        return f'<SafetyPhoto {self.id} for {self.record_type} {self.record_id}>'

class JobHazardAnalysis(db.Model):
    """Job hazard analysis (JHA)"""
    __tablename__ = 'job_hazard_analyses'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    jha_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    job_description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))
    required_ppe = db.Column(db.Text)
    required_training = db.Column(db.Text)
    required_permits = db.Column(db.Text)
    special_equipment = db.Column(db.Text)
    
    # Approval
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approval_date = db.Column(db.Date)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('job_hazard_analyses', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_jhas')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_jhas')
    steps = db.relationship('JHAStep', backref='jha', order_by='JHAStep.step_number', lazy='dynamic')
    
    def __repr__(self):
        return f'<JobHazardAnalysis {self.jha_number}: {self.title}>'

class JHAStep(db.Model):
    """Individual steps in a job hazard analysis"""
    __tablename__ = 'jha_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    jha_id = db.Column(db.Integer, db.ForeignKey('job_hazard_analyses.id'), nullable=False)
    step_number = db.Column(db.Integer)
    job_step = db.Column(db.Text, nullable=False)
    hazards = db.Column(db.Text, nullable=False)
    controls = db.Column(db.Text, nullable=False)
    
    def __repr__(self):
        return f'<JHAStep {self.step_number} for JHA {self.jha_id}>'

class PreTaskPlan(db.Model):
    """Pre-task safety planning"""
    __tablename__ = 'pretask_plans'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    plan_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    task_description = db.Column(db.Text, nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    location = db.Column(db.String(100))
    company = db.Column(db.String(100))
    
    hazards_identified = db.Column(db.Text)
    safety_concerns = db.Column(db.Text)
    required_ppe = db.Column(db.Text)
    tools_equipment = db.Column(db.Text)
    emergency_procedures = db.Column(db.Text)
    
    supervisor_name = db.Column(db.String(100))
    supervisor_signature = db.Column(db.Boolean, default=False)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('pretask_plans', lazy='dynamic'))
    creator = db.relationship('User', backref='created_pretask_plans')
    attendees = db.relationship('PreTaskAttendee', backref='plan', lazy='dynamic')
    
    def __repr__(self):
        return f'<PreTaskPlan {self.plan_number}: {self.title}>'

class PreTaskAttendee(db.Model):
    """Attendees of pre-task safety planning meetings"""
    __tablename__ = 'pretask_attendees'
    
    id = db.Column(db.Integer, primary_key=True)
    pre_task_plan_id = db.Column(db.Integer, db.ForeignKey('pretask_plans.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    signature = db.Column(db.Boolean, default=False)
    
    def __repr__(self):
        return f'<PreTaskAttendee {self.name} for Plan {self.pre_task_plan_id}>'

class SafetyOrientation(db.Model):
    """Safety orientation sessions"""
    __tablename__ = 'safety_orientations'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    orientation_number = db.Column(db.String(50), unique=True)
    title = db.Column(db.String(100), nullable=False)
    date = db.Column(db.Date, default=datetime.utcnow().date)
    location = db.Column(db.String(100))
    topics = db.Column(db.Text)
    presenter = db.Column(db.String(100))
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('safety_orientations', lazy='dynamic'))
    creator = db.relationship('User', backref='created_orientations')
    attendees = db.relationship('OrientationAttendee', backref='orientation', lazy='dynamic')
    
    def __repr__(self):
        return f'<SafetyOrientation {self.orientation_number}: {self.title}>'

class OrientationAttendee(db.Model):
    """Attendees of safety orientation sessions"""
    __tablename__ = 'orientation_attendees'
    
    id = db.Column(db.Integer, primary_key=True)
    orientation_id = db.Column(db.Integer, db.ForeignKey('safety_orientations.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    company = db.Column(db.String(100))
    trade = db.Column(db.String(100))
    
    def __repr__(self):
        return f'<OrientationAttendee {self.name} for Orientation {self.orientation_id}>'

class SafetyMetrics(db.Model):
    """Monthly safety metrics"""
    __tablename__ = 'safety_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    date = db.Column(db.Date)  # First day of month
    
    # Monthly stats
    man_hours = db.Column(db.Integer, default=0)
    recordable_incidents = db.Column(db.Integer, default=0)
    lost_time_incidents = db.Column(db.Integer, default=0)
    first_aid_incidents = db.Column(db.Integer, default=0)
    near_miss_incidents = db.Column(db.Integer, default=0)
    
    # Calculated rates
    trir = db.Column(db.Float, default=0.0)  # Total Recordable Incident Rate
    ltir = db.Column(db.Float, default=0.0)  # Lost Time Incident Rate
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('safety_metrics', lazy='dynamic'))
    creator = db.relationship('User', backref='created_safety_metrics')
    
    def __repr__(self):
        return f'<SafetyMetrics for {self.project_id} - {self.date}>'