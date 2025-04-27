# app/models/bim.py
from app.extensions import db
from datetime import datetime
import os
from sqlalchemy.ext.declarative import declared_attr

class BIMModel(db.Model):
    __tablename__ = 'bim_models'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    model_type = db.Column(db.String(50), nullable=False)  # architectural, structural, MEP
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    current_version_id = db.Column(db.Integer, db.ForeignKey('bim_model_versions.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='bim_models')
    user = db.relationship('User')
    versions = db.relationship('BIMModelVersion', back_populates='model', 
                               foreign_keys='BIMModelVersion.model_id',
                               cascade='all, delete-orphan')
    current_version = db.relationship('BIMModelVersion', 
                                      foreign_keys=[current_version_id], 
                                      post_update=True)
    issues = db.relationship('BIMIssue', back_populates='model', cascade='all, delete-orphan')
    
    @property
    def open_issues_count(self):
        """Count open issues for this model"""
        from app.models.bim import BIMIssue
        return BIMIssue.query.filter_by(model_id=self.id, status='open').count()
    
    def get_current_version(self):
        """Get the current version or the latest if current is not set"""
        if self.current_version:
            return self.current_version
        
        # Get latest version
        latest = BIMModelVersion.query.filter_by(model_id=self.id).order_by(
            BIMModelVersion.version_number.desc()).first()
        return latest
    
    def calculate_storage_size(self):
        """Calculate total storage size of all versions in bytes"""
        total_size = 0
        for version in self.versions:
            try:
                if os.path.exists(version.file_path):
                    total_size += os.path.getsize(version.file_path)
            except:
                pass
        return total_size

class BIMModelVersion(db.Model):
    __tablename__ = 'bim_model_versions'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('bim_models.id'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    notes = db.Column(db.Text, nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    model = db.relationship('BIMModel', foreign_keys=[model_id], back_populates='versions')
    user = db.relationship('User')
    
    def __init__(self, **kwargs):
        super(BIMModelVersion, self).__init__(**kwargs)

class BIMIssue(db.Model):
    __tablename__ = 'bim_issues'
    
    id = db.Column(db.Integer, primary_key=True)
    model_id = db.Column(db.Integer, db.ForeignKey('bim_models.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='open', nullable=False)  # open, in_progress, resolved
    priority = db.Column(db.String(20), default='medium', nullable=False)  # low, medium, high
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    position_x = db.Column(db.Float, nullable=True)
    position_y = db.Column(db.Float, nullable=True)
    position_z = db.Column(db.Float, nullable=True)
    element_id = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    model = db.relationship('BIMModel', back_populates='issues')
    creator = db.relationship('User', foreign_keys=[created_by])
    assignee = db.relationship('User', foreign_keys=[assigned_to])
    comments = db.relationship('BIMIssueComment', back_populates='issue', cascade='all, delete-orphan')

# Add BIMIssueComment class since it's referenced in BIMIssue
class BIMIssueComment(db.Model):
    __tablename__ = 'bim_issue_comments'
    
    id = db.Column(db.Integer, primary_key=True)
    issue_id = db.Column(db.Integer, db.ForeignKey('bim_issues.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    issue = db.relationship('BIMIssue', back_populates='comments')
    user = db.relationship('User')
    
    def __repr__(self):
        return f'<BIMIssueComment {self.id}>'