# app/models/contracts.py
from app.extensions import db
from datetime import datetime
from sqlalchemy import func
from sqlalchemy.ext.declarative import declared_attr


class ContractStatus:
    DRAFT = 'draft'
    PENDING = 'pending'
    ACTIVE = 'active'
    COMPLETE = 'complete'
    TERMINATED = 'terminated'
    EXPIRED = 'expired'


class Contract(db.Model):
    __tablename__ = 'contracts'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default=ContractStatus.DRAFT)
    contract_type = db.Column(db.String(50))  # To identify the type of contract: prime, subcontract, agreement
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    project = db.relationship('Project', back_populates='contracts')
    creator = db.relationship('User', foreign_keys=[created_by])
    
    # Polymorphic identity
    __mapper_args__ = {
        'polymorphic_on': contract_type,
        'polymorphic_identity': 'contract'
    }

class ContractBase(db.Model):
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default=ContractStatus.DRAFT)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=func.now())
    updated_at = db.Column(db.DateTime, default=func.now(), onupdate=func.now())
    
    # Common relationships - use @declared_attr for relationships in abstract classes
    @declared_attr
    def creator(cls):
        return db.relationship('User', foreign_keys=[cls.created_by])
    
    # Files and documents
    document_path = db.Column(db.String(255))
    signed_document_path = db.Column(db.String(255))

class PrimeContract(ContractBase):
    __tablename__ = 'prime_contracts'
    id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True)
    contract_number = db.Column(db.String(50), unique=True)
    contract_type = db.Column(db.String(50))  # lump sum, cost plus, etc.
    contract_value = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Contract parties
    client_name = db.Column(db.String(100))
    client_contact = db.Column(db.String(100))
    client_email = db.Column(db.String(100))
    client_phone = db.Column(db.String(20))
    
    # Financial terms
    retainage_percent = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(100))
    
    # Contract execution
    executed_date = db.Column(db.Date)
    signed_by = db.Column(db.String(100))
    
    # Change order summary
    approved_changes = db.Column(db.Float, default=0.0)
    pending_changes = db.Column(db.Float, default=0.0)
    revised_value = db.Column(db.Float)
    
    # Relationships - these are fine in concrete classes
    project = db.relationship('Project', backref=db.backref('prime_contracts', lazy='dynamic'))
    change_orders = db.relationship(
        'ContractChangeOrder',
        primaryjoin="and_(ContractChangeOrder.contract_id==PrimeContract.id, "
                   "ContractChangeOrder.contract_type=='prime')",
        foreign_keys="[ContractChangeOrder.contract_id]",
        viewonly=True  # Important to avoid conflicts with other relationships
    )

    __mapper_args__ = {
        'polymorphic_identity': 'prime'
    }


    
    def __repr__(self):
        return f'<PrimeContract {self.id}: {self.title}>'
    
    def update_revised_value(self):
        self.revised_value = self.contract_value + self.approved_changes

class Subcontract(ContractBase):
    __tablename__ = 'subcontracts'
    id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True)
    subcontract_number = db.Column(db.String(50), unique=True)
    subcontract_type = db.Column(db.String(50))  # lump sum, unit price, etc.
    subcontract_value = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Subcontractor details
    company_name = db.Column(db.String(100))
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    
    # Scope
    scope_of_work = db.Column(db.Text)
    
    # Financial terms
    retainage_percent = db.Column(db.Float, default=0.0)
    payment_terms = db.Column(db.String(100))
    
    # Contract execution
    executed_date = db.Column(db.Date)
    signed_by = db.Column(db.String(100))
    
    # Change order summary
    approved_changes = db.Column(db.Float, default=0.0)
    pending_changes = db.Column(db.Float, default=0.0)
    revised_value = db.Column(db.Float)
    
    # Insurance and compliance
    insurance_expiration = db.Column(db.Date)
    bonded = db.Column(db.Boolean, default=False)
    bond_company = db.Column(db.String(100))
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('subcontracts', lazy='dynamic'))
    change_orders = db.relationship(
            'ContractChangeOrder',
            primaryjoin="and_(ContractChangeOrder.contract_id==Subcontract.id, "
                    "ContractChangeOrder.contract_type=='subcontract')",
            foreign_keys="[ContractChangeOrder.contract_id]",
            viewonly=True
        )
    __mapper_args__ = {
        'polymorphic_identity': 'subcontract'
    }
    def __repr__(self):
        return f'<Subcontract {self.id}: {self.title}>'
    
    def update_revised_value(self):
        self.revised_value = self.subcontract_value + self.approved_changes

class ProfessionalServiceAgreement(ContractBase):
    __tablename__ = 'professional_service_agreements'
    id = db.Column(db.Integer, db.ForeignKey('contracts.id'), primary_key=True)
    agreement_number = db.Column(db.String(50), unique=True)
    agreement_type = db.Column(db.String(50))  # hourly, fixed fee, etc.
    agreement_value = db.Column(db.Float)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    
    # Service provider details
    company_name = db.Column(db.String(100))
    contact_name = db.Column(db.String(100))
    contact_email = db.Column(db.String(100))
    contact_phone = db.Column(db.String(20))
    
    # Scope
    scope_of_services = db.Column(db.Text)
    
    # Financial terms
    rate_schedule = db.Column(db.Text)
    payment_terms = db.Column(db.String(100))
    
    # Contract execution
    executed_date = db.Column(db.Date)
    signed_by = db.Column(db.String(100))
    
    # Change order summary
    approved_changes = db.Column(db.Float, default=0.0)
    pending_changes = db.Column(db.Float, default=0.0)
    revised_value = db.Column(db.Float)
    
    # Insurance
    insurance_requirements = db.Column(db.Text)
    insurance_expiration = db.Column(db.Date)
    
    # Relationships
    project = db.relationship('Project', backref=db.backref('professional_service_agreements', lazy='dynamic'))
    change_orders = db.relationship(
        'ContractChangeOrder',
        primaryjoin="and_(ContractChangeOrder.contract_id==ProfessionalServiceAgreement.id, "
                   "ContractChangeOrder.contract_type=='agreement')",
        foreign_keys="[ContractChangeOrder.contract_id]",
        viewonly=True
    )
    __mapper_args__ = {
        'polymorphic_identity': 'agreement'
    }
    
    def __repr__(self):
        return f'<ProfessionalServiceAgreement {self.id}: {self.title}>'
    
    def update_revised_value(self):
        self.revised_value = self.agreement_value + self.approved_changes

class LienWaiver(db.Model):
    __tablename__ = 'lien_waivers'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    contractor_name = db.Column(db.String(100), nullable=False)
    waiver_type = db.Column(db.String(50))  # partial, final, conditional, unconditional
    waiver_date = db.Column(db.Date, nullable=False)
    amount = db.Column(db.Float)
    through_date = db.Column(db.Date)  # For partial waivers, work completed through date
    document_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    project = db.relationship('Project', backref=db.backref('lien_waivers', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<LienWaiver {self.id}: {self.contractor_name} - {self.waiver_type}>'

class CertificateOfInsurance(db.Model):
    __tablename__ = 'certificates_of_insurance'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    provider_name = db.Column(db.String(100), nullable=False)
    insured_party = db.Column(db.String(100), nullable=False)
    policy_number = db.Column(db.String(50), nullable=False)
    policy_type = db.Column(db.String(50))  # general liability, workers comp, etc.
    effective_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date, nullable=False)
    coverage_amount = db.Column(db.Float)
    additional_insured = db.Column(db.Boolean, default=False)
    document_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    project = db.relationship('Project', backref=db.backref('certificates_of_insurance', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<CertificateOfInsurance {self.id}: {self.insured_party} - {self.policy_type}>'

class LetterOfIntent(db.Model):
    __tablename__ = 'letters_of_intent'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    recipient_name = db.Column(db.String(100), nullable=False)
    recipient_company = db.Column(db.String(100))
    work_description = db.Column(db.Text, nullable=False)
    estimated_value = db.Column(db.Float)
    issue_date = db.Column(db.Date, nullable=False)
    expiration_date = db.Column(db.Date)
    executed = db.Column(db.Boolean, default=False)
    executed_date = db.Column(db.Date)
    converted_to_contract = db.Column(db.Boolean, default=False)
    contract_id = db.Column(db.Integer)  # ID of the resulting contract
    document_path = db.Column(db.String(255))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    project = db.relationship('Project', backref=db.backref('letters_of_intent', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by])
    
    def __repr__(self):
        return f'<LetterOfIntent {self.id}: {self.recipient_name}>'

class ContractChangeOrder(db.Model):
    __tablename__ = 'contract_change_orders'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    contract_id = db.Column(db.Integer, nullable=False)  # Not a direct foreign key
    contract_type = db.Column(db.String(20), nullable=False)  # 'prime', 'subcontract', 'agreement'
    change_order_number = db.Column(db.String(50))
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    requested_date = db.Column(db.Date)
    approved_date = db.Column(db.Date)
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    time_extension_days = db.Column(db.Integer, default=0)
    reason_code = db.Column(db.String(50))  # code for change reason
    document_path = db.Column(db.String(255))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    # Relationships
    project = db.relationship('Project', backref=db.backref('contract_change_orders', lazy='dynamic'))
    creator = db.relationship('User', foreign_keys=[created_by], backref='created_change_orders')
    approver = db.relationship('User', foreign_keys=[approved_by], backref='approved_change_orders')
    
    def __repr__(self):
        return f'<ChangeOrder {self.id}: {self.title} (${self.amount})>'

class ContractDocument(db.Model):
    __tablename__ = 'contract_documents'
    
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    contract_id = db.Column(db.Integer, nullable=False)
    contract_type = db.Column(db.String(20), nullable=False)  # 'prime', 'subcontract', 'agreement', etc.
    document_type = db.Column(db.String(50), nullable=False)  # 'contract', 'amendment', 'exhibit', etc.
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    file_name = db.Column(db.String(255))
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)  # in bytes
    file_type = db.Column(db.String(50))  # mime type
    version = db.Column(db.String(20))
    uploaded_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    uploaded_at = db.Column(db.DateTime, default=func.now())

    # Relationships
    project = db.relationship('Project', backref=db.backref('contract_documents', lazy='dynamic'))
    uploader = db.relationship('User', backref='uploaded_contract_documents')
    
    def __repr__(self):
        return f'<ContractDocument {self.id}: {self.title}>'