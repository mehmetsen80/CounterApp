from flask import request, g
import logging

logger = logging.getLogger(__name__)

def add_service_name_header(response):
    """Add X-Service-Name header to all responses"""
    response.headers['X-Service-Name'] = 'counter-app'
    return response

def register_interceptors(app):
    """Register all interceptors with the Flask app"""
    app.after_request(add_service_name_header) 