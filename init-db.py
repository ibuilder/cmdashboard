import click
from flask.cli import with_appcontext
from app.extensions import db
from app.models.user import User, Role

def register_commands(app):
    """Register custom CLI commands"""
    
    @app.cli.command('init-db')
    @with_appcontext
    def init_db():
        """Initialize the database"""
        click.echo('Creating database tables...')
        
        try:
            # Create all tables
            db.create_all()
            
            # Insert default roles
            Role.insert_roles()
            
            click.echo('Database tables created successfully.')
            click.echo('Default roles inserted.')
        except Exception as e:
            click.echo(f'Error initializing database: {e}')
    
    @app.cli.command('create-admin')
    @with_appcontext
    def create_admin():
        """Create an admin user"""
        # Ensure roles exist first
        Role.insert_roles()
        
        # Check if admin already exists
        admin_email = 'admin@example.com'
        existing_admin = User.query.filter_by(email=admin_email).first()
        
        if existing_admin:
            click.echo(f'Admin user {admin_email} already exists.')
            return
        
        # Get admin password securely
        password = click.prompt('Enter admin password', hide_input=True, confirmation_prompt=True)
        
        # Create admin user
        admin_role = Role.query.filter_by(name='Admin').first()
        admin_user = User(
            email=admin_email,
            name='Admin User',
            role=admin_role,
            is_active=True
        )
        admin_user.password = password
        
        # Add and commit
        db.session.add(admin_user)
        db.session.commit()
        
        click.echo(f'Admin user {admin_email} created successfully.')
    
    @app.cli.command('reset-db')
    @with_appcontext
    def reset_db():
        """Reset the entire database"""
        click.confirm('Are you sure you want to reset the entire database? ALL DATA WILL BE LOST!', abort=True)
        
        click.echo('Dropping all tables...')
        db.drop_all()
        
        click.echo('Recreating tables...')
        db.create_all()
        
        # Reinsert default roles
        Role.insert_roles()
        
        click.echo('Database reset completed.')
    
    @app.cli.command('list-users')
    @with_appcontext
    def list_users():
        """List all users in the system"""
        users = User.query.all()
        
        if not users:
            click.echo('No users found.')
            return
        
        click.echo('Users in the system:')
        for user in users:
            click.echo(f'ID: {user.id}, Email: {user.email}, Role: {user.role.name if user.role else "No Role"}')