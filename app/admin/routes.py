from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from app.models.user import User
from app.models.settings import Company
from app.extensions import db
from app.utils.access_control import role_required
from app.admin.forms import UserForm, CompanyForm
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# User Management
@admin_bp.route('/users')
@login_required
@role_required(['Admin'])
def users():
    """List all users"""
    users = User.query.order_by(User.name).all()
    return render_template('admin/users/list.html', users=users)

@admin_bp.route('/users/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def create_user():
    """Create a new user"""
    form = UserForm()
    
    if form.validate_on_submit():
        # Check if email already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('A user with that email already exists', 'danger')
            return render_template('admin/users/create.html', form=form)
        
        user = User(
            name=form.name.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            role=form.role.data,
            status=form.status.data,
            job_title=form.job_title.data,
            phone=form.phone.data,
            company_id=form.company.data.id if form.company.data else None
        )
        db.session.add(user)
        db.session.commit()
        
        flash('User created successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/users/create.html', form=form)

@admin_bp.route('/users/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit_user(id):
    """Edit a user"""
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    
    # Don't require password for edits
    form.password.validators = []
    form.password.flags.required = False
    
    if form.validate_on_submit():
        user.name = form.name.data
        user.email = form.email.data
        user.role = form.role.data
        user.status = form.status.data
        user.job_title = form.job_title.data
        user.phone = form.phone.data
        user.company_id = form.company.data.id if form.company.data else None
        
        # Update password only if provided
        if form.password.data:
            user.password = generate_password_hash(form.password.data)
        
        db.session.commit()
        flash('User updated successfully!', 'success')
        return redirect(url_for('admin.users'))
    
    return render_template('admin/users/edit.html', form=form, user=user)

@admin_bp.route('/users/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete_user(id):
    """Delete a user"""
    user = User.query.get_or_404(id)
    
    # Prevent deleting your own account
    if user.id == current_user.id:
        flash('You cannot delete your own account', 'danger')
        return redirect(url_for('admin.users'))
    
    db.session.delete(user)
    db.session.commit()
    
    flash('User deleted successfully!', 'success')
    return redirect(url_for('admin.users'))

# Company Management
@admin_bp.route('/companies')
@login_required
@role_required(['Admin'])
def companies():
    """List all companies"""
    companies = Company.query.order_by(Company.name).all()
    return render_template('admin/companies/list.html', companies=companies)

@admin_bp.route('/companies/create', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def create_company():
    """Create a new company"""
    form = CompanyForm()
    
    if form.validate_on_submit():
        company = Company(
            name=form.name.data,
            company_type=form.company_type.data,
            address_line1=form.address_line1.data,
            address_line2=form.address_line2.data,
            city=form.city.data,
            state_province=form.state_province.data,
            postal_code=form.postal_code.data,
            country=form.country.data,
            phone=form.phone.data,
            fax=form.fax.data,
            website=form.website.data,
            tax_id=form.tax_id.data,
            notes=form.notes.data,
            status=form.status.data
        )
        db.session.add(company)
        db.session.commit()
        
        flash('Company created successfully!', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/companies/create.html', form=form)

@admin_bp.route('/companies/<int:id>/edit', methods=['GET', 'POST'])
@login_required
@role_required(['Admin'])
def edit_company(id):
    """Edit a company"""
    company = Company.query.get_or_404(id)
    form = CompanyForm(obj=company)
    
    if form.validate_on_submit():
        form.populate_obj(company)
        company.updated_at = datetime.now()
        db.session.commit()
        
        flash('Company updated successfully!', 'success')
        return redirect(url_for('admin.companies'))
    
    return render_template('admin/companies/edit.html', form=form, company=company)

@admin_bp.route('/companies/<int:id>/delete', methods=['POST'])
@login_required
@role_required(['Admin'])
def delete_company(id):
    """Delete a company"""
    company = Company.query.get_or_404(id)
    
    # Check if company is associated with users
    if company.users:
        flash('Cannot delete company that has associated users', 'danger')
        return redirect(url_for('admin.companies'))
    
    db.session.delete(company)
    db.session.commit()
    
    flash('Company deleted successfully!', 'success')
    return redirect(url_for('admin.companies'))

# System Settings
@admin_bp.route('/settings')
@login_required
@role_required(['Admin'])
def settings():
    """System settings management"""
    from app.models.settings import DatabaseSettings
    
    settings = DatabaseSettings.query.all()
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/update', methods=['POST'])
@login_required
@role_required(['Admin'])
def update_settings():
    """Update system settings"""
    from app.models.settings import DatabaseSettings
    
    setting_id = request.form.get('id')
    setting_value = request.form.get('value')
    
    setting = DatabaseSettings.query.get_or_404(setting_id)
    setting.setting_value = setting_value
    setting.updated_at = datetime.now()
    
    db.session.commit()
    
    return jsonify({'success': True})