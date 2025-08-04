import os
import logging
import jwt
from functools import wraps
from flask import request, jsonify, current_app
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class KeycloakConfig:
    """Keycloak JWT role validation configuration"""
    
    def __init__(self):
        self.required_realm_role = "gateway_admin_realm"
        self.required_client_id = "linqra-gateway-client"
        self.required_client_role = "gateway_admin"
    
    def validate_jwt_roles(self, token: str) -> bool:
        """
        Validate JWT token has required realm and client roles
        
        Args:
            token: JWT token string
            
        Returns:
            bool: True if token has required roles, False otherwise
        """
        try:
            # Decode JWT without verification (we trust the gateway)
            # In production, you might want to verify the token signature
            decoded_token = jwt.decode(token, options={"verify_signature": False})
            
            logger.info(f"JWT Token: {token[:50]}...")
            
            # Check realm roles
            has_realm_role = self._check_realm_roles(decoded_token)
            
            # Check client roles
            has_client_role = self._check_client_roles(decoded_token)
            
            # Both roles must be present
            is_valid = has_realm_role and has_client_role
            
            if is_valid:
                logger.info("Required roles found in JWT token")
            else:
                logger.warning("Required roles not found in JWT token")
                if not has_realm_role:
                    logger.warning(f"Missing required realm role: {self.required_realm_role}")
                if not has_client_role:
                    logger.warning(f"Missing required client role: {self.required_client_role} for client: {self.required_client_id}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating JWT roles: {e}")
            return False
    
    def _check_realm_roles(self, decoded_token: Dict[str, Any]) -> bool:
        """
        Check if token has required realm role
        
        Args:
            decoded_token: Decoded JWT token
            
        Returns:
            bool: True if required realm role is present
        """
        try:
            realm_access = decoded_token.get("realm_access", {})
            realm_roles = realm_access.get("roles", [])
            
            logger.info(f"Realm Roles: {realm_roles}")
            
            return self.required_realm_role in realm_roles
            
        except Exception as e:
            logger.error(f"Error checking realm roles: {e}")
            return False
    
    def _check_client_roles(self, decoded_token: Dict[str, Any]) -> bool:
        """
        Check if token has required client role
        
        Args:
            decoded_token: Decoded JWT token
            
        Returns:
            bool: True if required client role is present
        """
        try:
            resource_access = decoded_token.get("resource_access", {})
            
            if self.required_client_id not in resource_access:
                logger.warning(f"Client {self.required_client_id} not found in resource_access")
                return False
            
            client_roles = resource_access[self.required_client_id].get("roles", [])
            logger.info(f"Client Roles for {self.required_client_id}: {client_roles}")
            
            return self.required_client_role in client_roles
            
        except Exception as e:
            logger.error(f"Error checking client roles: {e}")
            return False
    
    def extract_token_from_header(self) -> Optional[str]:
        """
        Extract JWT token from Authorization header
        
        Returns:
            str: JWT token if found, None otherwise
        """
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            return auth_header[7:]  # Remove 'Bearer ' prefix
        
        return None

# Global instance
keycloak_config = KeycloakConfig()

def require_keycloak_roles(f):
    """
    Decorator to require Keycloak JWT roles for protected endpoints
    
    Usage:
        @app.route('/protected')
        @require_keycloak_roles
        def protected_endpoint():
            return "Access granted"
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extract JWT token
        token = keycloak_config.extract_token_from_header()
        
        if not token:
            logger.warning("No JWT token found in request")
            return jsonify({"error": "No JWT token provided"}), 401
        
        # Validate roles
        if not keycloak_config.validate_jwt_roles(token):
            logger.warning("JWT token does not have required roles")
            return jsonify({"error": "Insufficient permissions"}), 403
        
        logger.info(f"JWT role validation passed for request to: {request.path}")
        
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error during endpoint execution: {e}")
            raise e
    
    return decorated_function

def validate_keycloak_jwt():
    """
    Function to validate JWT token with Keycloak roles
    Can be used in existing authentication flows
    
    Returns:
        bool: True if token is valid and has required roles
    """
    token = keycloak_config.extract_token_from_header()
    
    if not token:
        logger.warning("No JWT token found in request")
        return False
    
    return keycloak_config.validate_jwt_roles(token) 