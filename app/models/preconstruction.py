# app/models/preconstruction.py
from app.extensions import db
from datetime import datetime
from sqlalchemy.sql import func
from app.models.base import Comment, Attachment

class QualifiedBidder(db.Model):
    __tablename__ = 'qualified_bidders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    qualification_date = db.Column(db.Date)
    qualification_status = db.Column(db.String(20), default='pending')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    company = db.relationship('Company', backref='bidder_qualifications')
    project = db.relationship('Project', backref='qualified_bidders')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_qualified_bidders')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_qualified_bidders')
    bid_packages = db.relationship('BidPackage', secondary='bidders_packages',
                             back_populates='bidders')
    
    # Fixed relationship - use back_populates instead of backref to avoid conflicts
    bids = db.relationship('Bid', back_populates='bidder')


class BidPackage(db.Model):
    __tablename__ = 'bid_packages'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    package_number = db.Column(db.String(30))
    description = db.Column(db.Text)
    issue_date = db.Column(db.Date)
    due_date = db.Column(db.Date)
    estimated_value = db.Column(db.Numeric(precision=12, scale=2))
    scope_of_work = db.Column(db.Text)
    status = db.Column(db.String(20), default='draft')
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='bid_packages')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_bid_packages')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_bid_packages')
    bidders = db.relationship('QualifiedBidder', secondary='bidders_packages',
                            back_populates='bid_packages')
    
    # Uncommented and fixed to use back_populates instead of backref
    bids = db.relationship('Bid', back_populates='package')


# Association table for bidders and packages
bidders_packages = db.Table('bidders_packages',
    db.Column('bidder_id', db.Integer, db.ForeignKey('qualified_bidders.id'), primary_key=True),
    db.Column('package_id', db.Integer, db.ForeignKey('bid_packages.id'), primary_key=True),
    db.Column('invited_date', db.DateTime, default=func.now()),
    db.Column('response', db.String(20)),  # accepted, declined, no_response
)


class Bid(db.Model):
    __tablename__ = 'bids'
    
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('bid_packages.id'), nullable=False)
    bidder_id = db.Column(db.Integer, db.ForeignKey('qualified_bidders.id'), nullable=False)
    bid_amount = db.Column(db.Numeric(precision=12, scale=2))
    bid_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='received')  # received, under_review, accepted, rejected
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Fixed relationships to use back_populates instead of backref
    bidder = db.relationship('QualifiedBidder', back_populates='bids')
    package = db.relationship('BidPackage', back_populates='bids')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_bids')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_bids')


# BidManual class is fine as is
class BidManual(db.Model):
    __tablename__ = 'bid_manuals'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    version = db.Column(db.String(20))
    issue_date = db.Column(db.Date)
    description = db.Column(db.Text)
    file_path = db.Column(db.String(255))
    file_name = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # Size in bytes
    status = db.Column(db.String(20), default='draft')  # draft, published, archived
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    updated_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    project = db.relationship('Project', backref='bid_manuals')
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_bid_manuals')
    updater = db.relationship('User', foreign_keys=[updated_by], backref='updated_bid_manuals')