# app/models/project.py
from sqlalchemy import Column, Integer, String, Text, Numeric, DateTime, Date, ForeignKey
from app.extensions import db
from datetime import datetime
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import select, func
from app.models.preconstruction import BidPackage
from app.models.bim import BIMModel
from app.models.contracts import PrimeContract, Subcontract, ProfessionalServiceAgreement
from app.models.closeout import OperationAndMaintenanceManual, Warranty, AtticStock, FinalInspection, AsBuiltDrawing
from enum import Enum

# Updated ProjectStatus class to match what's used in forms.py
class ProjectStatus(str, Enum):
    PLANNING = 'planning'
    ACTIVE = 'active'
    ON_HOLD = 'on_hold'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'
    DELAYED = 'delayed'

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = db.Column(db.Integer, primary_key=True)
    # Basic information
    name = db.Column(db.String(100), nullable=False)
    number = db.Column(db.String(64), nullable=False)  # Added to match form
    description = db.Column(db.Text)
    
    # Dates
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)  # This is in the original model
    target_completion_date = db.Column(db.Date)  # Added to match form
    actual_completion_date = db.Column(db.Date)  # Added to match form
    
    # Financial
    budget = db.Column(db.Numeric(15, 2))
    actual_cost = db.Column(db.Numeric(15, 2))
    contract_amount = db.Column(db.Numeric(15, 2))  # Added to match form
    
    # Status and client
    status = db.Column(db.String(20), default=ProjectStatus.PLANNING)
    client_id = db.Column(db.Integer, db.ForeignKey('clients.id'))
    client_name = db.Column(db.String(255))  # Added to match form
    client_contact_info = db.Column(db.Text)  # Added to match form
    
    # Classification
    project_type = db.Column(db.String(50))  # Added to match form
    category = db.Column(db.String(50))  # Added to match form
    
    # Location
    address = db.Column(db.String(255))  # Added to match form
    city = db.Column(db.String(100))  # Added to match form
    state = db.Column(db.String(100))  # Added to match form
    zip_code = db.Column(db.String(20))  # Added to match form
    country = db.Column(db.String(100))  # Added to match form
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - keep all existing relationships
    client = relationship('Client', back_populates='projects')
    team_members = relationship('ProjectTeamMember', back_populates='project', cascade='all, delete-orphan')
    tasks = relationship('Task', back_populates='project', cascade='all, delete-orphan')
    documents = relationship('Document', back_populates='project', cascade='all, delete-orphan')
    bim_models = relationship('BIMModel', back_populates='project', cascade='all, delete-orphan')
    schedules = relationship('Schedule', back_populates='project', cascade='all, delete-orphan')
    contracts = relationship('Contract', back_populates='project', cascade='all, delete-orphan')
    om_manuals = db.relationship('OperationAndMaintenanceManual', back_populates='project', cascade='all, delete-orphan')
    warranties = db.relationship('Warranty', back_populates='project', cascade='all, delete-orphan')
    attic_stock = db.relationship('AtticStock', back_populates='project', cascade='all, delete-orphan')
    final_inspections = db.relationship('FinalInspection', back_populates='project', cascade='all, delete-orphan')
    as_built_drawings = db.relationship('AsBuiltDrawing', back_populates='project', cascade='all, delete-orphan')
    closeout_documents = db.relationship('CloseoutDocument', back_populates='project', cascade='all, delete-orphan')
    project_users = db.relationship('UserProject', back_populates='project', cascade='all, delete-orphan')
    images = relationship('ProjectImage', back_populates='project', cascade='all, delete-orphan')
    notes = relationship('ProjectNote', back_populates='project', cascade='all, delete-orphan')
    project_users_alt = relationship('ProjectUser', back_populates='project', cascade='all, delete-orphan')
    
    # Keep all existing properties
    @property
    def percent_complete(self):
        """Calculate the project completion percentage based on tasks"""
        if not self.tasks:
            return 0
            
        completed_tasks = sum(1 for task in self.tasks if task.status == 'completed')
        return int((completed_tasks / len(self.tasks)) * 100)
    
    @property
    def duration_days(self):
        """Calculate project duration in days"""
        if not self.start_date:
            return 0
            
        end = self.end_date or datetime.utcnow().date()
        return (end - self.start_date).days
    
    @property
    def budget_status(self):
        """Calculate budget status"""
        if not self.budget or self.budget <= 0:
            return 'not_set'
            
        if not self.actual_cost:
            return 'within_budget'
            
        variance = float(self.budget) - float(self.actual_cost)
        variance_percent = (variance / float(self.budget)) * 100
        
        if variance_percent >= 5:
            return 'under_budget'
        elif variance_percent <= -5:
            return 'over_budget'
        else:
            return 'within_budget'
    
    @property
    def days_remaining(self):
        """Calculate remaining days until project end date"""
        if not self.end_date:
            return None
            
        today = datetime.utcnow().date()
        remaining = (self.end_date - today).days
        return remaining if remaining >= 0 else 0
    
    @property
    def is_overdue(self):
        """Check if project is overdue"""
        if not self.end_date:
            return False
            
        today = datetime.utcnow().date()
        return today > self.end_date and self.status != ProjectStatus.COMPLETED
    
    @hybrid_property
    def active_team_count(self):
        """Count active team members"""
        return len([m for m in self.team_members if m.is_active])
    
    @active_team_count.expression
    def active_team_count(cls):
        """SQL expression for active team count"""
        return select(func.count(ProjectTeamMember.id)).\
            where(ProjectTeamMember.project_id == cls.id).\
            where(ProjectTeamMember.is_active == True).\
            label("active_team_count")

class ProjectTeamMember(db.Model):
    __tablename__ = 'project_team_members'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # project_manager, engineer, architect, etc.
    is_active = db.Column(db.Boolean, default=True)
    added_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='team_members')
    user = db.relationship('User', foreign_keys=[user_id], backref='project_memberships')
    added_by_user = db.relationship('User', foreign_keys=[added_by])
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='uix_project_user'),
    )

# Add the missing ProjectUser class
class ProjectUser(db.Model):
    __tablename__ = 'project_users'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # owner, manager, contributor, viewer
    permissions = db.Column(db.Text)  # JSON string of permissions
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='project_users_alt')
    user = db.relationship('User', backref='project_users')
    
    __table_args__ = (
        db.UniqueConstraint('project_id', 'user_id', name='uix_project_user_role'),
    )

# Add the missing ProjectImage class
class ProjectImage(db.Model):
    __tablename__ = 'project_images'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_featured = db.Column(db.Boolean, default=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', back_populates='images')
    uploader = db.relationship('User', backref='uploaded_images')

# Add the missing ProjectNote class
class ProjectNote(db.Model):
    __tablename__ = 'project_notes'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='notes')
    author = db.relationship('User', backref='project_notes')