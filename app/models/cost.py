# app/models/cost.py
from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func

class Budget(db.Model):
    __tablename__ = 'budgets'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    total_amount = db.Column(db.Numeric(15, 2), nullable=False)
    approved = db.Column(db.Boolean, default=False)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_date = db.Column(db.DateTime)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('budgets', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    approver = db.relationship('User', foreign_keys=[approved_by])
    line_items = db.relationship('BudgetItem', backref='budget', lazy='dynamic',
                           cascade='all, delete-orphan')

# Renamed from BudgetLineItem to BudgetItem to match import
class BudgetItem(db.Model):
    __tablename__ = 'budget_line_items'
    
    id = db.Column(db.Integer, primary_key=True)
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'), nullable=False)
    cost_code = db.Column(db.String(50))
    description = db.Column(db.String(255), nullable=False)
    estimated_amount = db.Column(db.Numeric(15, 2), nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Invoice(db.Model):
    __tablename__ = 'invoices'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    invoice_number = db.Column(db.String(50), nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    date_issued = db.Column(db.Date, nullable=False)
    date_due = db.Column(db.Date)
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid, rejected
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_date = db.Column(db.DateTime)
    paid_date = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('invoices', lazy='dynamic'))
    vendor = db.relationship('Company', backref=db.backref('invoices', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    approver = db.relationship('User', foreign_keys=[approved_by])

class PotentialChangeOrder(db.Model):
    __tablename__ = 'potential_change_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    pco_number = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(15, 2))
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, rejected
    date_submitted = db.Column(db.Date)
    date_required = db.Column(db.Date)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('potential_change_orders', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])

class ChangeOrder(db.Model):
    __tablename__ = 'change_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    change_order_number = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    status = db.Column(db.String(20), default='draft')  # draft, submitted, approved, executed, rejected
    date_submitted = db.Column(db.Date)
    date_approved = db.Column(db.Date)
    date_executed = db.Column(db.Date)
    time_extension_days = db.Column(db.Integer, default=0)
    submitted_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('cost_change_orders', lazy='dynamic'))
    submitter = db.relationship('User', foreign_keys=[submitted_by])
    approver = db.relationship('User', foreign_keys=[approved_by])

# Added DirectCost class which was missing but referenced in the import error
class DirectCost(db.Model):
    __tablename__ = 'direct_costs'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    cost_code = db.Column(db.String(50))
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(15, 2), nullable=False)
    date_incurred = db.Column(db.Date, nullable=False)
    vendor_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, approved, paid
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('direct_costs', lazy='dynamic'))
    vendor = db.relationship('Company', backref=db.backref('direct_costs', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])

# Added ApprovalLetter class which was missing but referenced in the import error
class ApprovalLetter(db.Model):
    __tablename__ = 'approval_letters'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    letter_number = db.Column(db.String(50), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    related_to_type = db.Column(db.String(50))  # change_order, invoice, etc.
    related_to_id = db.Column(db.Integer)
    amount = db.Column(db.Numeric(15, 2))
    date_issued = db.Column(db.Date, nullable=False)
    issued_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    file_path = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('approval_letters', lazy='dynamic'))
    issuer = db.relationship('User', foreign_keys=[issued_by])
    approver = db.relationship('User', foreign_keys=[approved_by])