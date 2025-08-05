#!/usr/bin/env python3
"""
Script to convert Swagger 2.0 specification to OpenAPI 3.1.0
"""

import json
import requests
import urllib3

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def fetch_swagger_spec():
    """Fetch the current Swagger 2.0 specification from the running app"""
    try:
        # Try the gateway URL first
        response = requests.get('https://localhost:7777/r/counter-app/swagger.json', verify=False)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching Swagger spec from gateway: {e}")
        try:
            # Fallback to direct app URL
            response = requests.get('https://localhost:5001/r/counter-app/swagger.json', verify=False)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e2:
            print(f"Error fetching Swagger spec from direct app: {e2}")
            return None

def convert_to_openapi_3_1(swagger_2_0_spec):
    """Convert Swagger 2.0 to OpenAPI 3.1.0"""
    
    # Start with OpenAPI 3.1.0 structure
    openapi_3_1 = {
        "openapi": "3.1.0",
        "info": {
            "title": swagger_2_0_spec.get("info", {}).get("title", "CounterApp API"),
            "version": swagger_2_0_spec.get("info", {}).get("version", "1.0.0"),
            "description": swagger_2_0_spec.get("info", {}).get("description", "A Flask-based counter application with Eureka service discovery and Keycloak authentication"),
            "contact": {
                "name": "Linqra Platform",
                "url": "https://github.com/mehmetsen80/Linqra"
            }
        },
        "servers": [
            {
                "url": "https://localhost:7777/r/counter-app",
                "description": "Development server (via gateway)"
            },
            {
                "url": "https://localhost:5001/r/counter-app",
                "description": "Development server (direct)"
            }
        ],
        "paths": {},
        "components": {
            "securitySchemes": {
                "Bearer": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                    "description": "JWT token from Keycloak"
                },
                "X509Certificate": {
                    "type": "mutualTLS",
                    "description": "X.509 client certificate"
                }
            },
            "schemas": {}
        },
        "tags": [
            {
                "name": "counter",
                "description": "Counter operations"
            },
            {
                "name": "health",
                "description": "Health check operations"
            }
        ]
    }
    
    # Convert paths
    for path, path_item in swagger_2_0_spec.get("paths", {}).items():
        openapi_3_1["paths"][path] = {}
        
        for method, operation in path_item.items():
            if method.lower() in ["get", "post", "put", "delete", "patch"]:
                # Convert security from Swagger 2.0 format
                security = []
                if 'security' in operation:
                    for sec in operation['security']:
                        if 'Bearer' in sec:
                            security.append({"Bearer": []})
                        if 'X509Certificate' in sec:
                            security.append({"X509Certificate": []})
                
                # Convert responses
                responses = {}
                for status_code, response in operation.get("responses", {}).items():
                    responses[status_code] = {
                        "description": response.get("description", ""),
                        "content": {
                            "application/json": {
                                "schema": response.get("schema", {})
                            }
                        }
                    }
                
                # Build the operation
                openapi_operation = {
                    "summary": operation.get("summary", ""),
                    "description": operation.get("description", ""),
                    "operationId": operation.get("operationId", f"{method.lower()}_{path.replace('/', '_').replace('-', '_')}"),
                    "responses": responses
                }
                
                if security:
                    openapi_operation["security"] = security
                
                # Add tags based on path
                if "counter" in path or "count" in path:
                    openapi_operation["tags"] = ["counter"]
                elif "health" in path:
                    openapi_operation["tags"] = ["health"]
                else:
                    openapi_operation["tags"] = ["default"]
                
                openapi_3_1["paths"][path][method.lower()] = openapi_operation
    
    # Convert definitions to schemas
    for def_name, def_schema in swagger_2_0_spec.get("definitions", {}).items():
        openapi_3_1["components"]["schemas"][def_name] = def_schema
    
    return openapi_3_1

def save_openapi_spec(openapi_spec, filename="openapi_3_1_0.json"):
    """Save OpenAPI 3.1.0 specification to file"""
    with open(filename, 'w') as f:
        json.dump(openapi_spec, f, indent=2)
    print(f"✅ OpenAPI 3.1.0 specification saved to {filename}")

def main():
    """Main function to convert Swagger 2.0 to OpenAPI 3.1.0"""
    print("🔧 Fetching Swagger 2.0 specification...")
    
    # Fetch current Swagger spec
    swagger_spec = fetch_swagger_spec()
    if not swagger_spec:
        print("❌ Could not fetch Swagger specification. Make sure the app is running.")
        print("   Try accessing: https://localhost:7777/r/counter-app/swagger.json")
        return
    
    print(f"✅ Successfully fetched Swagger spec with {len(swagger_spec.get('paths', {}))} paths")
    print("🔄 Converting to OpenAPI 3.1.0...")
    
    # Convert to OpenAPI 3.1.0
    openapi_spec = convert_to_openapi_3_1(swagger_spec)
    
    # Save the OpenAPI 3.1.0 specification
    save_openapi_spec(openapi_spec)
    
    print("🎉 Conversion completed successfully!")
    print(f"📊 Generated spec contains:")
    print(f"   - {len(openapi_spec['paths'])} paths")
    print(f"   - {len(openapi_spec['components']['schemas'])} schemas")
    print(f"   - {len(openapi_spec['components']['securitySchemes'])} security schemes")
    print(f"   - {len(openapi_spec['tags'])} tags")
    print("\n📝 You can now use this OpenAPI 3.1.0 specification with Linqra.")

if __name__ == "__main__":
    main() 