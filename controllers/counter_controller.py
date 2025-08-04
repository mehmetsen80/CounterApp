from flask import jsonify, request, current_app
from flask_restx import Resource, fields, Namespace
from services.counter_service import CounterService
from enums.status_enum import StatusEnum
from config.security_config import security_config

counter_service = CounterService()

# Create namespace for API documentation
api = Namespace('counter', description='Counter operations')

# Define response models
counter_model = api.model('Counter', {
    'count': fields.Integer(description='Current counter value'),
    'status': fields.String(description='Operation status'),
    'metadata': fields.Raw(description='Counter metadata')
})

counter_details_model = api.model('CounterDetails', {
    'status': fields.String(description='Operation status'),
    'counter': fields.Raw(description='Detailed counter information')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

protected_response_model = api.model('ProtectedResponse', {
    'count': fields.Integer(description='Current counter value'),
    'status': fields.String(description='Operation status'),
    'metadata': fields.Raw(description='Counter metadata'),
    'auth_type': fields.String(description='Authentication type used')
})

@api.route('/api/v1/count')
@api.route('/api/v1/count/')
class CountResource(Resource):
    @api.doc('get_count',
              description='Get the current count with metadata (requires authentication)',
              security=['Bearer', 'X509Certificate'],
              responses={
                  200: ('Successfully retrieved count', counter_model),
                  401: ('Authentication required', error_model)
              })
    def get(self):
        """Get the current count with metadata"""
        counter_data = counter_service.get_counter_dict()
        return {
            "count": counter_service.get_count(),
            "status": StatusEnum.SUCCESS.value,
            "metadata": counter_data
        }

@api.route('/api/v1/count/increment')
@api.route('/api/v1/count/increment/')
class IncrementResource(Resource):
    @api.doc('increment_count',
              description='Increment the counter by 1 and return the new value',
              responses={
                  200: ('Counter incremented successfully', counter_model)
              })
    def get(self):
        """Increment the counter by 1 and return the new value"""
        count = counter_service.increment_count()
        counter_data = counter_service.get_counter_dict()
        return {
            "count": count,
            "status": StatusEnum.INCREMENTED.value,
            "metadata": counter_data
        }

@api.route('/api/v1/count/reset')
@api.route('/api/v1/count/reset/')
class ResetResource(Resource):
    @api.doc('reset_count',
              description='Reset the counter to 0 and return the reset value',
              responses={
                  200: ('Counter reset successfully', counter_model)
              })
    def get(self):
        """Reset the counter to 0 and return the reset value"""
        count = counter_service.reset_count()
        counter_data = counter_service.get_counter_dict()
        return {
            "count": count,
            "status": StatusEnum.RESET.value,
            "metadata": counter_data
        }

@api.route('/api/v1/count/details')
@api.route('/api/v1/count/details/')
class DetailsResource(Resource):
    @api.doc('get_counter_details',
              description='Get detailed counter information including metadata',
              responses={
                  200: ('Successfully retrieved counter details', counter_details_model)
              })
    def get(self):
        """Get detailed counter information including metadata"""
        counter_data = counter_service.get_counter_dict()
        return {
            "status": StatusEnum.SUCCESS.value,
            "counter": counter_data
        }

@api.route('/api/v1/count/protected')
@api.route('/api/v1/count/protected/')
class ProtectedResource(Resource):
    @api.doc('get_protected_count',
              description='Get count with JWT authentication and Keycloak role validation',
              security=['Bearer'],
              responses={
                  200: ('Successfully retrieved count with JWT authentication', protected_response_model),
                  401: ('JWT token required or invalid', error_model),
                  403: ('Insufficient permissions - missing required Keycloak roles', error_model)
              })
    def get(self):
        """Get count with JWT authentication and Keycloak role validation"""
        if not security_config._has_jwt_token():
            api.abort(401, "JWT token required")
        
        counter_data = counter_service.get_counter_dict()
        return {
            "count": counter_service.get_count(),
            "status": StatusEnum.SUCCESS.value,
            "metadata": counter_data,
            "auth_type": "JWT with Keycloak roles"
        }

