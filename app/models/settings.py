# app.models.settings.py
from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func

class CSIDivision(db.Model):
    __tablename__ = 'csi_divisions'
    
    id = db.Column(db.Integer, primary_key=True)
    division_number = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    subdivisions = db.relationship('CSISubdivision', backref='division', cascade='all, delete-orphan')

class CSISubdivision(db.Model):
    __tablename__ = 'csi_subdivisions'
    
    id = db.Column(db.Integer, primary_key=True)
    division_id = db.Column(db.Integer, db.ForeignKey('csi_divisions.id'), nullable=False)
    subdivision_number = db.Column(db.String(10), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)

class CostCode(db.Model):
    __tablename__ = 'cost_codes'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Null means global
    code = db.Column(db.String(20), nullable=False)
    description = db.Column(db.String(100), nullable=False)
    csi_subdivision_id = db.Column(db.Integer, db.ForeignKey('csi_subdivisions.id'))
    parent_code_id = db.Column(db.Integer, db.ForeignKey('cost_codes.id'))
    
    # Relationships
    project = db.relationship('Project', backref='cost_codes')
    csi_subdivision = db.relationship('CSISubdivision', backref='cost_codes')
    parent_code = db.relationship('CostCode', remote_side=[id], backref='child_codes')

class LaborRate(db.Model):
    __tablename__ = 'labor_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Null means global
    name = db.Column(db.String(100), nullable=False)
    trade = db.Column(db.String(50))
    description = db.Column(db.Text)
    rate_regular = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    rate_overtime = db.Column(db.Numeric(precision=10, scale=2))
    rate_doubletime = db.Column(db.Numeric(precision=10, scale=2))
    unit = db.Column(db.String(20), default='hour')
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='labor_rates')
    creator = db.relationship('User', foreign_keys=[created_by])

class MaterialRate(db.Model):
    __tablename__ = 'material_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Null means global
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), nullable=False)  # EA, LF, SF, etc.
    rate = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    default_markup = db.Column(db.Numeric(precision=5, scale=2))
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='material_rates')
    creator = db.relationship('User', foreign_keys=[created_by])

class EquipmentRate(db.Model):
    __tablename__ = 'equipment_rates'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))  # Null means global
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    unit = db.Column(db.String(20), default='hour')  # hour, day, week, month
    rate = db.Column(db.Numeric(precision=10, scale=2), nullable=False)
    default_markup = db.Column(db.Numeric(precision=5, scale=2))
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='equipment_rates')
    creator = db.relationship('User', foreign_keys=[created_by])

class Company(db.Model):
    __tablename__ = 'companies'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    company_type = db.Column(db.String(50))  # Owner, GC, Subcontractor, Vendor, etc.
    address_line1 = db.Column(db.String(100))
    address_line2 = db.Column(db.String(100))
    city = db.Column(db.String(50))
    state_province = db.Column(db.String(50))
    postal_code = db.Column(db.String(20))
    country = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    fax = db.Column(db.String(20))
    website = db.Column(db.String(100))
    tax_id = db.Column(db.String(50))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    contacts = db.relationship('CompanyContact', backref='company', cascade='all, delete-orphan')
    users = db.relationship('User', back_populates='company')

class CompanyContact(db.Model):
    __tablename__ = 'company_contacts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))
    mobile = db.Column(db.String(20))
    is_primary = db.Column(db.Boolean, default=False)

class ProjectSettings(db.Model):
    __tablename__ = 'project_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    setting_key = db.Column(db.String(50), nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20))  # string, number, boolean, json
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', backref='settings')

class DatabaseSettings(db.Model):
    __tablename__ = 'database_settings'
    
    id = db.Column(db.Integer, primary_key=True)
    setting_key = db.Column(db.String(50), nullable=False, unique=True)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(20))  # string, number, boolean, json
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())