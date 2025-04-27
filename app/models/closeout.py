# app/models/closeout.py
from app.extensions import db
from datetime import datetime
from enum import Enum
from sqlalchemy.ext.declarative import declared_attr

class WarrantyType(str, Enum):
    STANDARD = 'standard'
    EXTENDED = 'extended'
    LIMITED = 'limited'
    SPECIAL = 'special'

class WarrantyStatus(str, Enum):
    ACTIVE = 'active'
    EXPIRED = 'expired'
    PENDING = 'pending'
    VOID = 'void'

class OperationAndMaintenanceManual(db.Model):
    __tablename__ = 'om_manuals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    submission_date = db.Column(db.Date)
    equipment_category = db.Column(db.String(100))
    manufacturer = db.Column(db.String(100))
    model_number = db.Column(db.String(100))
    location = db.Column(db.String(200))
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='om_manuals')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<OperationAndMaintenanceManual {self.id}: {self.title}>'

class Warranty(db.Model):
    __tablename__ = 'warranties'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    warranty_type = db.Column(db.String(50), default=WarrantyType.STANDARD.value)
    status = db.Column(db.String(50), default=WarrantyStatus.ACTIVE.value)
    
    # Company information
    manufacturer = db.Column(db.String(100))
    supplier = db.Column(db.String(100))
    contractor = db.Column(db.String(100))
    contact_name = db.Column(db.String(100))
    contact_phone = db.Column(db.String(50))
    contact_email = db.Column(db.String(100))
    
    # Equipment/system information
    equipment_category = db.Column(db.String(100))
    model_number = db.Column(db.String(100))
    serial_number = db.Column(db.String(100))
    location = db.Column(db.String(200))
    
    # Date information
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date)
    duration_months = db.Column(db.Integer)  # Duration in months
    
    # Document information
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    
    # Special warranty terms
    terms_conditions = db.Column(db.Text)
    exclusions = db.Column(db.Text)
    maintenance_requirements = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='warranties')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<Warranty {self.id}: {self.title}>'
    
    @property
    def is_expired(self):
        return self.end_date and self.end_date < datetime.utcnow().date()

class AtticStock(db.Model):
    __tablename__ = 'attic_stock'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    material_name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Float, nullable=False)
    unit_of_measure = db.Column(db.String(50))  # e.g., box, gallon, sq ft
    
    # Material details
    manufacturer = db.Column(db.String(100))
    product_number = db.Column(db.String(100))
    color = db.Column(db.String(100))
    spec_section = db.Column(db.String(50))  # specification section reference
    
    # Location and storage
    storage_location = db.Column(db.String(200))
    delivery_date = db.Column(db.Date)
    turnover_date = db.Column(db.Date)  # when given to owner
    
    # Related contacts
    supplier = db.Column(db.String(100))
    subcontractor = db.Column(db.String(100))
    contact_information = db.Column(db.Text)
    
    # Photos and documentation
    image_path = db.Column(db.String(255))
    file_path = db.Column(db.String(255))  # for submittal or product data
    
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='attic_stock')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<AtticStock {self.id}: {self.material_name} ({self.quantity} {self.unit_of_measure})>'

class FinalInspection(db.Model):
    __tablename__ = 'final_inspections'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    inspection_type = db.Column(db.String(100), nullable=False)  # Building, Electrical, Plumbing, etc.
    authority = db.Column(db.String(100))  # AHJ name
    inspector_name = db.Column(db.String(100))
    inspection_date = db.Column(db.Date)
    result = db.Column(db.String(50))  # Pass, Fail, Conditional Pass
    certificate_number = db.Column(db.String(100))
    expiration_date = db.Column(db.Date)
    
    # Certificate details
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    
    description = db.Column(db.Text)
    comments = db.Column(db.Text)
    follow_up_required = db.Column(db.Boolean, default=False)
    follow_up_notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='final_inspections')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<FinalInspection {self.id}: {self.inspection_type} ({self.result})>'

class AsBuiltDrawing(db.Model):
    __tablename__ = 'as_built_drawings'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    drawing_number = db.Column(db.String(100))
    revision = db.Column(db.String(20))
    discipline = db.Column(db.String(50))  # Architectural, Structural, MEP, etc.
    
    description = db.Column(db.Text)
    date_received = db.Column(db.Date)
    
    # File information
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    file_format = db.Column(db.String(20))  # PDF, DWG, RVT, etc.
    
    # Source information
    prepared_by = db.Column(db.String(100))
    company = db.Column(db.String(100))
    contact_information = db.Column(db.Text)
    
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='as_built_drawings')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<AsBuiltDrawing {self.id}: {self.title}>'

class CloseoutDocument(db.Model):
    __tablename__ = 'closeout_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    document_type = db.Column(db.String(100))  # Substantial Completion, Final Completion, Lien Waiver, etc.
    description = db.Column(db.Text)
    
    # Document details
    document_number = db.Column(db.String(100))
    date_issued = db.Column(db.Date)
    date_received = db.Column(db.Date)
    issued_by = db.Column(db.String(100))
    received_from = db.Column(db.String(100))
    
    # File information
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    
    notes = db.Column(db.Text)
    
    # Tracking
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', back_populates='closeout_documents')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<CloseoutDocument {self.id}: {self.title}>'