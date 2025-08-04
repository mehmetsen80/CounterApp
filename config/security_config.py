import os
import logging
import ssl
from functools import wraps
from flask import request, jsonify, current_app
from flask_jwt_extended import JWTManager, verify_jwt_in_request, get_jwt
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa, padding
import ssl
import re
from config.keycloak_config import keycloak_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityConfig:
    """Security configuration for JWT and X.509 certificate validation"""
    
    def __init__(self, app=None):
        self.app = app
        self.jwt = JWTManager()
        
        # Keycloak configuration (matching Spring Security)
        self.keycloak_gateway_url = os.environ.get('KEYCLOAK_GATEWAY_URL', 'localhost')
        self.keycloak_gateway_port = os.environ.get('KEYCLOAK_GATEWAY_PORT', '8281')
        self.jwt_issuer_uri = os.environ.get('JWT_ISSUER_URI', 
            f"http://{self.keycloak_gateway_url}:{self.keycloak_gateway_port}/realms/Linqra")
        self.jwt_jwk_set_uri = os.environ.get('JWT_JWK_SET_URI',
            f"http://{self.keycloak_gateway_url}:{self.keycloak_gateway_port}/realms/Linqra/protocol/openid-connect/certs")
        
        # Allowed issuers (matching Spring Security configuration)
        self.allowed_issuers = [
            f"http://{self.keycloak_gateway_url}:{self.keycloak_gateway_port}/realms/Linqra",
            "http://localhost:8281/realms/Linqra"
        ]
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize security configuration with Flask app"""
        # Configure JWT (using Keycloak JWK set, not local secret)
        app.config['JWT_ACCESS_TOKEN_EXPIRES'] = False  # No expiration for now
        app.config['JWT_TOKEN_LOCATION'] = ['headers']
        app.config['JWT_HEADER_NAME'] = 'Authorization'
        app.config['JWT_HEADER_TYPE'] = 'Bearer'
        
        # Initialize JWT manager
        self.jwt.init_app(app)
        
        # Register security decorators
        # self._register_security_decorators(app) # This line is removed
        
        logger.info("Security configuration initialized")
    
    def create_ssl_context(self, app):
        """Create SSL context with mutual TLS support"""
        if not app.config.get('SSL_ENABLED', True):
            print("❌ SSL disabled in config")
            return None
        
        cert_path = app.config.get('SSL_CERT_PATH')
        key_path = app.config.get('SSL_KEY_PATH')
        ca_bundle_path = app.config.get('CA_BUNDLE_PATH')
        mutual_tls_enabled = app.config.get('MUTUAL_TLS_ENABLED', False)
        
        # Check if SSL files exist
        if not (cert_path and key_path and os.path.exists(cert_path) and os.path.exists(key_path)):
            print(f"❌ SSL files not found. Certificate: {cert_path}, Key: {key_path}")
            return None
        
        print("✅ Creating SSL context...")
        
        # Create SSL context for server (CLIENT_AUTH is correct for servers)
        ssl_context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        ssl_context.load_cert_chain(cert_path, key_path)
        
        # For servers, we don't need check_hostname
        ssl_context.check_hostname = False
        
        if mutual_tls_enabled and ca_bundle_path and os.path.exists(ca_bundle_path):
            ssl_context.verify_mode = ssl.CERT_REQUIRED
            ssl_context.load_verify_locations(ca_bundle_path)
            print(f"✅ Mutual TLS enabled with CA bundle")
        else:
            ssl_context.verify_mode = ssl.CERT_NONE
            print("ℹ️  Standard HTTPS (mTLS disabled)")
        
        print("✅ SSL context created successfully")
        return ssl_context
    
    def _has_jwt_token(self):
        """Check if request has JWT token with required Keycloak roles"""
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            logger.debug(f"✅ JWT token found: {auth_header[:50]}...")
            # Now validate Keycloak roles by default using keycloak_config
            return keycloak_config.validate_jwt_roles(auth_header[7:])  # Remove 'Bearer ' prefix
        else:
            logger.debug("❌ No JWT token found in Authorization header")
            return False
    
    def validate_jwt_token(self, token):
        """Validate JWT token against Keycloak (matching Spring Security)"""
        try:
            import jwt
            import requests
            
            # Decode JWT header to get key ID
            header = jwt.get_unverified_header(token)
            kid = header.get('kid')
            
            if not kid:
                logger.error("No key ID (kid) found in JWT header")
                return False
            
            # Fetch JWK set from Keycloak
            response = requests.get(self.jwt_jwk_set_uri, timeout=10)
            response.raise_for_status()
            jwk_set = response.json()
            
            # Find the key with matching kid
            key = None
            for jwk in jwk_set.get('keys', []):
                if jwk.get('kid') == kid:
                    key = jwk
                    break
            
            if not key:
                logger.error(f"No key found for kid: {kid}")
                return False
            
            # Decode and validate JWT
            decoded = jwt.decode(
                token,
                key,
                algorithms=['RS256'],
                audience='account',  # Keycloak default audience
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_aud': False,  # Skip audience validation for now
                    'verify_iss': True
                }
            )
            
            # Validate issuer against allowed issuers
            issuer = decoded.get('iss')
            if issuer not in self.allowed_issuers:
                logger.error(f"Invalid issuer: {issuer}. Allowed: {self.allowed_issuers}")
                return False
            
            # Validate scope (Keycloak client scope)
            scope = decoded.get('scope', '')
            if 'counter-app.read' not in scope:
                logger.error(f"Missing required scope 'counter-app.read'. Available scopes: {scope}")
                return False
            
            logger.info(f"JWT validated successfully. Issuer: {issuer}, Scope: {scope}")
            return True
            
        except Exception as e:
            logger.error(f"JWT validation error: {e}")
            return False

# Global security config instance
security_config = SecurityConfig() 