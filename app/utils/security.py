from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()

def configure_security(app):
    """Configure security middleware for the application."""
    app.config['BCRYPT_LOG_ROUNDS'] = 12