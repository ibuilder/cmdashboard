# app/models/base.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy.ext.declarative import declared_attr
from app.extensions import db

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())


class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    module_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Define relationship directly, not in abstract form
    
    def get_user(self):
        """Get the user who created this comment"""
        from app.models.user import User
        return User.query.get(self.user_id)
    
    def get_record(self):
        """Get the associated record based on module_name"""
        if self.module_name == 'rfi':
            from app.models.engineering import RFI
            return RFI.query.get(self.record_id)
        elif self.module_name == 'submittal':
            from app.models.engineering import Submittal
            return Submittal.query.get(self.record_id)
        # Add other module types here...
        return None

class Attachment(db.Model):
    __tablename__ = 'attachments'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer)  # Size in bytes
    file_type = db.Column(db.String(50))  # MIME type
    record_id = db.Column(db.Integer, nullable=False)
    module_name = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    def get_user(self):
        """Get the user who uploaded this attachment"""
        from app.models.user import User
        return User.query.get(self.user_id)
        
    def __repr__(self):
        return f'<Attachment {self.id}: {self.filename}>'