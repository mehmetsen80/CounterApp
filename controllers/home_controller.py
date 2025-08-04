from flask import jsonify
from flask_restx import Resource, fields, Namespace
import os

# Create namespace for home API documentation
api = Namespace('home', description='Home page operations')

# Define response models
home_info_model = api.model('HomeInfo', {
    'message': fields.String(description='Application name'),
    'status': fields.String(description='Application status'),
    'version': fields.String(description='Application version'),
    'environment': fields.String(description='Current environment')
})

def get_home_info():
    """Get application home page information"""
    config_name = os.environ.get('FLASK_ENV', 'development')
    
    return {
        "message": "CounterApp API",
        "status": "running",
        "version": "1.0.0",
        "environment": config_name
    }, 200

@api.route('/')
@api.route('')
class HomeResource(Resource):
    @api.doc('get_home',
             description='Get application home page information',
             responses={
                 200: ('Application information retrieved successfully', home_info_model)
             })
    def get(self):
        """Get application home page information"""
        return get_home_info()

 