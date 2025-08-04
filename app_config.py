import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration class"""
    DEBUG = False
    TESTING = False
    
    # SSL Configuration
    SSL_CERT_PATH = os.path.join(os.path.dirname(__file__), 'keys', 'certs', 'server-cert.pem')
    SSL_KEY_PATH = os.path.join(os.path.dirname(__file__), 'keys', 'certs', 'server-key.pem')
    SSL_ENABLED = os.environ.get('SSL_ENABLED', 'true').lower() == 'true'
    
    # Mutual TLS Configuration
    MUTUAL_TLS_ENABLED = os.environ.get('MUTUAL_TLS_ENABLED', 'false').lower() == 'true'
    CA_BUNDLE_PATH = os.path.join(os.path.dirname(__file__), 'keys', 'certs', 'ca-bundle.pem')
    
    # HTTP Configuration (for development)
    HTTP_ENABLED = os.environ.get('HTTP_ENABLED', 'false').lower() == 'true'

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    FLASK_ENV = 'development'
    HTTP_ENABLED = True  # Enable HTTP in development

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    FLASK_ENV = 'production'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    DEBUG = True

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
} 