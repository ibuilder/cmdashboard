import os
from app.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig
from dotenv import load_dotenv

def get_config():
    """Return the appropriate configuration object based on environment variable"""
    # Load different .env files based on environment
    env = os.environ.get('FLASK_ENV', 'production').lower()
    
    # Load environment-specific .env file if it exists
    env_file = f".env.{env}"
    if os.path.exists(env_file):
        load_dotenv(env_file)
    
    # Always load default .env file as fallback
    load_dotenv()
    
    config_map = {
        'development': DevelopmentConfig,
        'testing': TestingConfig,
        'production': ProductionConfig,
        'default': Config
    }
    
    config_class = config_map.get(env, ProductionConfig)
    return config_class