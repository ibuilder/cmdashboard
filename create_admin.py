# create_admin.py
from app import create_app
from app.models.user import User, Role
from app.extensions import db

app = create_app()

with app.app_context():
    # Ensure roles exist
    Role.insert_roles()
    
    # Check if admin user already exists
    admin_email = 'admin@example.com'
    existing_user = User.query.filter_by(email=admin_email).first()
    
    if existing_user:
        print(f"User {admin_email} already exists.")
    else:
        # Create admin user
        admin_role = Role.query.filter_by(name='Admin').first()
        if not admin_role:
            print("Admin role not found!")
            exit(1)
            
        admin_user = User(
            email=admin_email,
            name='Admin User',
            is_active=True,
            role=admin_role
        )
        admin_user.password = 'adminpassword'
        
        db.session.add(admin_user)
        db.session.commit()
        
        print(f"Admin user created: {admin_email}")
        print("Password: adminpassword")