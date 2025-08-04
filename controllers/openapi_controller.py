from flask import jsonify
from flask_restx import Resource, fields, Namespace
import json
import os

# Create namespace for OpenAPI endpoints
api = Namespace('openapi', description='OpenAPI specification operations')

# Define response models
openapi_spec_model = api.model('OpenAPISpec', {
    'openapi': fields.String(description='OpenAPI version'),
    'info': fields.Raw(description='API information'),
    'paths': fields.Raw(description='API paths'),
    'components': fields.Raw(description='API components')
})

error_model = api.model('Error', {
    'error': fields.String(description='Error message')
})

@api.route('/openapi.json')
@api.route('/openapi.json/')
class OpenApiResource(Resource):
    @api.doc('get_openapi_spec',
             description='Get OpenAPI 3.1.0 specification',
             responses={
                 200: ('OpenAPI specification retrieved successfully', openapi_spec_model),
                 404: ('OpenAPI specification file not found', error_model),
                 500: ('Invalid JSON in OpenAPI specification file', error_model)
             })
    def get(self):
        """Serve OpenAPI 3.1.0 specification"""
        try:
            with open('openapi_3_1_0_spec.json', 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"error": "OpenAPI specification file not found"}, 404
        except json.JSONDecodeError:
            return {"error": "Invalid JSON in OpenAPI specification file"}, 500 