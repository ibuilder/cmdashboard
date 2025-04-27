# app/models/task.py
from sqlalchemy import Column, Integer, String, ForeignKey, Text, Date, Boolean, DateTime
from sqlalchemy.orm import relationship, backref
from app.extensions import db
from datetime import datetime
import json

class Task(db.Model):
    __tablename__ = 'tasks'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    status = db.Column(db.String(20), default='not_started')  # not_started, in_progress, completed, on_hold, cancelled
    priority = db.Column(db.String(10), default='medium')  # low, medium, high, urgent
    start_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    completed_date = db.Column(db.Date)
    is_milestone = db.Column(db.Boolean, default=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    assigned_to = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='tasks')
    children = db.relationship('Task', 
                               backref=db.backref('parent', remote_side=[id]),
                               cascade='all, delete-orphan')
    assignee = db.relationship('User', foreign_keys=[assigned_to], backref='assigned_tasks')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_tasks')
    activities = db.relationship('TaskActivity', back_populates='task', cascade='all, delete-orphan')
    
    @property
    def is_overdue(self):
        """Check if task is overdue"""
        if not self.due_date:
            return False
            
        return (self.due_date < datetime.utcnow().date() and 
                self.status not in ['completed', 'cancelled'])
    
    @property
    def days_remaining(self):
        """Calculate days until due date"""
        if not self.due_date:
            return None
            
        if self.status in ['completed', 'cancelled']:
            return 0
            
        today = datetime.utcnow().date()
        remaining = (self.due_date - today).days
        return remaining
    
    def log_activity(self, user_id, action, description=None, data=None):
        """Log an activity for this task"""
        activity = TaskActivity(
            task_id=self.id,
            user_id=user_id,
            action=action,
            description=description,
            data=json.dumps(data) if data else None
        )
        db.session.add(activity)

class TaskActivity(db.Model):
    __tablename__ = 'task_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    action = db.Column(db.String(50), nullable=False)  # created, updated, status_changed, comment, etc.
    description = db.Column(db.Text)
    data = db.Column(db.Text)  # JSON data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    task = db.relationship('Task', back_populates='activities')
    user = db.relationship('User')
    
    @property
    def data_json(self):
        """Parse the JSON data"""
        if not self.data:
            return {}
        try:
            return json.loads(self.data)
        except:
            return {}