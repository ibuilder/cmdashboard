import os
import click
from flask.cli import with_appcontext
from app.models.user import User, Role
from app.extensions import db, cache
from werkzeug.security import generate_password_hash
from datetime import datetime
from app.utils.backup import backup_database

def register_commands(app):
    """Register custom Flask CLI commands"""
    
    @app.cli.group()
    def user():
        """User management commands"""
        pass
    
    @user.command()
    @click.argument('email')
    @click.argument('password')
    @click.argument('name')
    @click.option('--admin', is_flag=True, help='Make the user an admin')
    @with_appcontext
    def create(email, password, name, admin=False):
        """Create a new user"""
        # Ensure roles exist
        Role.insert_roles()
        
        # Check if user exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            click.echo(f"User with email {email} already exists.")
            return
        
        # Create user
        user = User(email=email, name=name)
        user.password = password
        
        if admin:
            admin_role = Role.query.filter_by(name='Admin').first()
            user.role = admin_role
        
        from app.extensions import db
        db.session.add(user)
        db.session.commit()
        
        click.echo(f"User {name} ({email}) created successfully.")
        if admin:
            click.echo("User has admin privileges.")
    
    @user.command()
    @with_appcontext
    def list():
        """List all users"""
        users = User.query.all()
        if not users:
            click.echo("No users found.")
            return
        
        click.echo(f"{'ID':<5} {'Name':<30} {'Email':<30} {'Role':<15} {'Active':<8}")
        click.echo("-" * 88)
        
        for user in users:
            click.echo(f"{user.id:<5} {user.name:<30} {user.email:<30} "
                      f"{user.role.name:<15} {'✓' if user.is_active else '✗':<8}")
    
    @user.command()
    @click.argument('email')
    @with_appcontext
    def deactivate(email):
        """Deactivate a user"""
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f"User with email {email} not found.")
            return
        
        user.is_active = False
        db.session.commit()
        click.echo(f"User {email} has been deactivated.")
    
    @user.command()
    @click.argument('email')
    @with_appcontext
    def activate(email):
        """Activate a user"""
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f"User with email {email} not found.")
            return
        
        user.is_active = True
        db.session.commit()
        click.echo(f"User {email} has been activated.")
    
    @app.cli.group()
    def db_manage():
        """Database management commands"""
        pass
    
    @db_manage.command()
    def seed():
        """Seed the database with initial data"""
        from app.utils.seeder import seed_database
        seed_database()
        click.echo("Database seeded successfully")
    
    @app.cli.group()
    def setup():
        """Application setup commands"""
        pass
        
    @setup.command()
    @with_appcontext
    def directories():
        """Create required directories"""
        directories = [
            'logs',
            'backups',
            os.path.join(app.config['UPLOAD_FOLDER']),
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            click.echo(f"Created directory: {directory}")
    
    @app.cli.group()
    def maintenance():
        """Maintenance commands"""
        pass
    
    @maintenance.command()
    def clean_temp_files():
        """Clean temporary files older than 1 day"""
        import shutil
        from datetime import datetime, timedelta
        
        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if not os.path.exists(temp_dir):
            click.echo("Temp directory doesn't exist")
            return
        
        count = 0
        one_day_ago = datetime.now() - timedelta(days=1)
        
        for item in os.listdir(temp_dir):
            item_path = os.path.join(temp_dir, item)
            if os.path.isdir(item_path):
                # Check folder creation time
                created = datetime.fromtimestamp(os.path.getctime(item_path))
                if created < one_day_ago:
                    shutil.rmtree(item_path)
                    count += 1
            elif os.path.isfile(item_path):
                # Check file creation time
                created = datetime.fromtimestamp(os.path.getctime(item_path))
                if created < one_day_ago:
                    os.remove(item_path)
                    count += 1
        
        click.echo(f"Removed {count} old temporary files/directories")
    
    @app.cli.group()
    def backup():
        """Database backup commands"""
        pass
        
    @backup.command()
    def db():
        """Backup database to file"""
        with app.app_context():
            if backup_database():
                click.echo("Database backup completed successfully")
            else:
                click.echo("Database backup failed")
                exit(1)
    
    @app.cli.group()
    def project():
        """Project management commands"""
        pass
    
    @project.command()
    @click.argument('name')
    @click.argument('number')
    @click.option('--client', help='Client name')
    @click.option('--start-date', help='Project start date (YYYY-MM-DD)')
    @with_appcontext
    def create(name, number, client=None, start_date=None):
        """Create a new project"""
        from app.models.project import Project
        
        # Check if project exists
        existing_project = Project.query.filter_by(number=number).first()
        if existing_project:
            click.echo(f"Project with number {number} already exists.")
            return
        
        # Parse start date if provided
        start_date_obj = None
        if start_date:
            try:
                start_date_obj = datetime.strptime(start_date, '%Y-%m-%d').date()
            except ValueError:
                click.echo("Invalid date format. Please use YYYY-MM-DD.")
                return
        
        # Create project
        project = Project(
            name=name, 
            number=number,
            client_name=client,
            start_date=start_date_obj,
            status='planning'
        )
        
        db.session.add(project)
        db.session.commit()
        
        click.echo(f"Project '{name}' (#{number}) created successfully.")
    
    @project.command()
    @with_appcontext
    def list():
        """List all projects"""
        from app.models.project import Project
        
        projects = Project.query.all()
        if not projects:
            click.echo("No projects found.")
            return
        
        click.echo(f"{'ID':<5} {'Number':<10} {'Name':<30} {'Status':<15} {'Client':<20}")
        click.echo("-" * 80)
        
        for project in projects:
            click.echo(f"{project.id:<5} {project.number:<10} {project.name[:28]:<30} "
                      f"{project.status:<15} {(project.client_name or '')[:18]:<20}")
    
    @app.cli.group()
    def system():
        """System diagnostics and maintenance"""
        pass
    
    @system.command()
    def check():
        """Run system health checks"""
        issues_found = False
        
        # Check database connection
        click.echo("Checking database connection...")
        try:
            db.session.execute('SELECT 1')
            click.echo("✓ Database connection successful")
        except Exception as e:
            issues_found = True
            click.echo(f"✗ Database connection failed: {str(e)}")
        
        # Check upload directories
        click.echo("Checking upload directories...")
        directories = [
            os.path.join(app.config['UPLOAD_FOLDER']),
            os.path.join(app.config['UPLOAD_FOLDER'], 'documents'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'photos'),
            os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        ]
        
        for directory in directories:
            if os.path.exists(directory):
                if os.access(directory, os.W_OK):
                    click.echo(f"✓ Directory {directory} exists and is writable")
                else:
                    issues_found = True
                    click.echo(f"✗ Directory {directory} exists but is not writable")
            else:
                issues_found = True
                click.echo(f"✗ Directory {directory} does not exist")
        
        # Check logs directory
        log_dir = os.path.join(os.getcwd(), 'logs')
        if os.path.exists(log_dir):
            if os.access(log_dir, os.W_OK):
                click.echo(f"✓ Logs directory exists and is writable")
            else:
                issues_found = True
                click.echo(f"✗ Logs directory exists but is not writable")
        else:
            issues_found = True
            click.echo(f"✗ Logs directory does not exist")
        
        # Check required environment variables
        click.echo("Checking environment variables...")
        required_vars = ['SECRET_KEY', 'SQLALCHEMY_DATABASE_URI']
        for var in required_vars:
            if var in app.config and app.config[var]:
                click.echo(f"✓ Environment variable {var} is set")
            else:
                issues_found = True
                click.echo(f"✗ Environment variable {var} is not set")
        
        if issues_found:
            click.echo("\nSystem check completed with issues. Please resolve them before proceeding.")
        else:
            click.echo("\nSystem check completed successfully. All systems operational.")
    
    @system.command()
    def info():
        """Display system information"""
        import sys
        import platform
        
        click.echo("=== System Information ===")
        click.echo(f"Python version: {sys.version}")
        click.echo(f"Platform: {platform.platform()}")
        click.echo(f"Flask version: {app.version}")
        
        # Database info
        db_uri = app.config['SQLALCHEMY_DATABASE_URI']
        # Hide password in URI for security
        if '@' in db_uri:
            masked_uri = db_uri.replace('//', '//:***@')
        else:
            masked_uri = db_uri
        click.echo(f"Database: {masked_uri.split('://')[0]}")
        
        # App config info
        click.echo(f"\n=== Application Config ===")
        click.echo(f"Environment: {app.config.get('ENV', 'production')}")
        click.echo(f"Debug mode: {'Enabled' if app.debug else 'Disabled'}")
        click.echo(f"Testing mode: {'Enabled' if app.testing else 'Disabled'}")
        
        # Feature flags
        feature_flags = app.config.get('FEATURE_FLAGS', {})
        click.echo(f"\n=== Feature Flags ===")
        for feature, enabled in feature_flags.items():
            click.echo(f"{feature}: {'Enabled' if enabled else 'Disabled'}")
    
    @system.command()
    def clear_cache():
        """Clear the application cache"""
        try:
            cache.clear()
            click.echo("Cache cleared successfully")
        except Exception as e:
            click.echo(f"Error clearing cache: {str(e)}")
    
    @system.command()
    @click.option('--all', is_flag=True, help='Generate all test data')
    @click.option('--users', is_flag=True, help='Generate test users')
    @click.option('--projects', is_flag=True, help='Generate test projects')
    @click.option('--count', default=10, help='Number of records to generate')
    def generate_test_data(all, users, projects, count):
        """Generate test data for development"""
        if not (all or users or projects):
            click.echo("Please specify what data to generate (--all, --users, --projects)")
            return
        
        from app.utils.test_data import generate_test_data
        
        options = {
            'users': all or users,
            'projects': all or projects,
            'count': count
        }
        
        result = generate_test_data(options)
        
        for entity, count in result.items():
            click.echo(f"Generated {count} {entity}")
    
    @app.cli.group()
    def export():
        """Data export commands"""
        pass
    
    @export.command()
    @click.argument('output_file')
    @click.option('--type', default='json', type=click.Choice(['json', 'csv']), 
                help='Export format (json or csv)')
    def projects(output_file, type):
        """Export projects data to file"""
        from app.models.project import Project
        import json
        import csv
        
        projects = Project.query.all()
        if not projects:
            click.echo("No projects to export.")
            return
        
        if type == 'json':
            with open(output_file, 'w') as f:
                json_data = [project.to_dict() for project in projects]
                json.dump(json_data, f, indent=2)
        elif type == 'csv':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['id', 'number', 'name', 'description', 'status', 
                                'start_date', 'target_completion_date', 'client_name'])
                
                # Write data
                for project in projects:
                    writer.writerow([
                        project.id,
                        project.number,
                        project.name,
                        project.description,
                        project.status,
                        project.start_date,
                        project.target_completion_date,
                        project.client_name
                    ])
        
        click.echo(f"Exported {len(projects)} projects to {output_file}")
    
    @export.command()
    @click.argument('output_file')
    @click.option('--type', default='json', type=click.Choice(['json', 'csv']), 
                help='Export format (json or csv)')
    def users(output_file, type):
        """Export users data to file"""
        import json
        import csv
        
        users = User.query.all()
        if not users:
            click.echo("No users to export.")
            return
        
        if type == 'json':
            with open(output_file, 'w') as f:
                json_data = [user.to_dict() for user in users]
                json.dump(json_data, f, indent=2)
        elif type == 'csv':
            with open(output_file, 'w', newline='') as f:
                writer = csv.writer(f)
                # Write header
                writer.writerow(['id', 'email', 'name', 'role', 'is_active', 'last_seen'])
                
                # Write data
                for user in users:
                    writer.writerow([
                        user.id,
                        user.email,
                        user.name,
                        user.role.name if user.role else 'No Role',
                        user.is_active,
                        user.last_seen
                    ])
        
        click.echo(f"Exported {len(users)} users to {output_file}")