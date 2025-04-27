from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, BooleanField
from wtforms.validators import DataRequired, Email, Length, Optional
from wtforms_sqlalchemy.fields import QuerySelectField
from app.models.settings import Company

def get_companies():
    return Company.query.filter_by(status='active').order_by(Company.name).all()

class UserForm(FlaskForm):
    name = StringField('Full Name', validators=[DataRequired(), Length(min=3, max=100)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    role = SelectField('Role', choices=[
        ('Admin', 'Administrator'),
        ('Owner', 'Owner'),
        ('Owners Representative', 'Owner\'s Representative'),
        ('General Contractor', 'General Contractor'),
        ('Subcontractor', 'Subcontractor'),
        ('Design Team', 'Design Team'),
        ('User', 'Standard User')
    ])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('pending', 'Pending'),
        ('inactive', 'Inactive')
    ])
    job_title = StringField('Job Title', validators=[Optional(), Length(max=100)])
    phone = StringField('Phone', validators=[Optional(), Length(max=20)])
    company = QuerySelectField('Company', query_factory=get_companies, 
                             get_label='name', allow_blank=True)

class CompanyForm(FlaskForm):
    name = StringField('Company Name', validators=[DataRequired(), Length(max=100)])
    company_type = SelectField('Company Type', choices=[
        ('Owner', 'Owner'),
        ('General Contractor', 'General Contractor'),
        ('Subcontractor', 'Subcontractor'),
        ('Vendor', 'Vendor'),
        ('Consultant', 'Consultant'),
        ('Architect', 'Architect'),
        ('Engineer', 'Engineer'),
        ('Other', 'Other')
    ])
    address_line1 = StringField('Address Line 1', validators=[Length(max=100)])
    address_line2 = StringField('Address Line 2', validators=[Optional(), Length(max=100)])
    city = StringField('City', validators=[Length(max=50)])
    state_province = StringField('State/Province', validators=[Length(max=50)])
    postal_code = StringField('Postal Code', validators=[Length(max=20)])
    country = StringField('Country', validators=[Length(max=50)])
    phone = StringField('Phone', validators=[Length(max=20)])
    fax = StringField('Fax', validators=[Optional(), Length(max=20)])
    website = StringField('Website', validators=[Optional(), Length(max=100)])
    tax_id = StringField('Tax ID', validators=[Optional(), Length(max=50)])
    notes = TextAreaField('Notes', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive')
    ])