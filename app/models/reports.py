# app/models/reports.py
from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func

class ReportTemplate(db.Model):
    __tablename__ = 'report_templates'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50), nullable=False)  # preconstruction, engineering, safety, etc.
    query = db.Column(db.Text)
    parameters = db.Column(db.Text)  # JSON string of parameter definitions
    layout = db.Column(db.Text)  # JSON string of layout configuration
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    creator = db.relationship('User', foreign_keys=[created_by])

class SavedReport(db.Model):
    __tablename__ = 'saved_reports'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    template_id = db.Column(db.Integer, db.ForeignKey('report_templates.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    parameter_values = db.Column(db.Text)  # JSON string of parameter values
    schedule_type = db.Column(db.String(20))  # None, Daily, Weekly, Monthly
    schedule_day = db.Column(db.String(20))  # For weekly: Monday, Tuesday, etc. For monthly: 1-31
    schedule_time = db.Column(db.Time)
    recipients = db.Column(db.Text)  # JSON string of email recipients
    last_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    template = db.relationship('ReportTemplate')
    project = db.relationship('Project', backref='saved_reports')
    creator = db.relationship('User', foreign_keys=[created_by])

class ReportExecution(db.Model):
    __tablename__ = 'report_executions'
    
    id = db.Column(db.Integer, primary_key=True)
    saved_report_id = db.Column(db.Integer, db.ForeignKey('saved_reports.id'))
    execution_time = db.Column(db.DateTime, default=func.now())
    parameter_values = db.Column(db.Text)  # JSON string of parameter values used
    result_file_path = db.Column(db.String(255))
    status = db.Column(db.String(20))  # Success, Failed
    error_message = db.Column(db.Text)
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    saved_report = db.relationship('SavedReport', backref='executions')
    executor = db.relationship('User', foreign_keys=[executed_by])