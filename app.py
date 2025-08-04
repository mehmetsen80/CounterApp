from flask import Flask, jsonify, current_app
import os
import atexit
import signal
import sys
import threading
from dotenv import load_dotenv
from app_config import config
from config.security_config import security_config
from service_name_interceptor import register_interceptors
from config.eureka_config import register_with_eureka, deregister_from_eureka, stop_heartbeat
from config.http_server_config import start_http_server_if_enabled, stop_http_server, get_http_server_status
import json

# Load environment variables
load_dotenv()

# Global variables for cleanup
shutdown_event = threading.Event()
http_thread = None

def create_app(config_name=None):
    """Application factory pattern"""
    # Get the context path from environment or use default
    context_path = os.environ.get('CONTEXT_PATH', '/r/counter-app')
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    app.config.from_object(config[config_name])
    
    # Set the application root URL prefix (similar to Spring Boot's context-path)
    app.config['APPLICATION_ROOT'] = context_path
    
    # Initialize security configuration
    security_config.init_app(app)
    
    # Register interceptors
    register_interceptors(app)
    
    # Create main blueprint with context path
    from flask import Blueprint
    main_blueprint = Blueprint('main', __name__, url_prefix=context_path)

    # Initialize Flask-RESTX API with the blueprint
    from flask_restx import Api
    api = Api(main_blueprint,
              version='1.0.0',
              title='CounterApp API',
              description='A Flask-based counter application with Eureka service discovery and Keycloak authentication',
              contact='Linqra Platform',
              contact_url='https://github.com/mehmetsen80/Linqra',
              doc='/apidocs/')

    # Add Flask-RESTX namespaces to the API
    from controllers.home_controller import api as home_api
    from controllers.counter_controller import api as counter_api
    from controllers.health_controller import api as health_api
    from controllers.openapi_controller import api as openapi_api
    api.add_namespace(home_api)
    api.add_namespace(counter_api)
    api.add_namespace(health_api)
    api.add_namespace(openapi_api)

    # Register the main blueprint with the app
    app.register_blueprint(main_blueprint)
    
    return app

# Create the app instance
app = create_app()

# Global variables for cleanup
http_thread = None
shutdown_event = threading.Event()

def cleanup_resources():
    """Clean up all resources on shutdown"""
    print("🧹 Cleaning up resources...")
    
    # Stop HTTP server thread first
    stop_http_server()
    
    # Stop heartbeat before deregistering
    stop_heartbeat()
    
    # Deregister from Eureka
    deregister_from_eureka()
    
    print("✅ Cleanup completed")

def signal_handler(sig, frame):
    """Handle shutdown signals"""
    print(f"🛑 Received signal {sig}, shutting down CounterApp...")
    cleanup_resources()
    sys.exit(0)

def shutdown_handler():
    """Handler for graceful shutdown"""
    print("🛑 Shutdown handler called")
    cleanup_resources()

# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

# Register cleanup function to run at exit
atexit.register(shutdown_handler)


if __name__ == '__main__':
    try:
        # Register with Eureka on startup
        register_with_eureka()
        
        port = int(os.environ.get('PORT', 5001))
        debug = False  # Disable debug mode to prevent crashes
        
        # Configure SSL context
        ssl_context = security_config.create_ssl_context(app)
        
        # Start HTTP server if enabled (only if HTTPS is disabled)
        http_thread = start_http_server_if_enabled(app, port, ssl_context)
        
        # Log startup information
        if ssl_context:
            print(f"🚀 Starting CounterApp with HTTPS on port {port}")
        else:
            print(f"🌐 Starting CounterApp with HTTP on port {port}")
        
        # Start the main Flask app
        if ssl_context:
            app.run(host='0.0.0.0', port=port, debug=False, ssl_context=ssl_context, use_reloader=False, threaded=True)
        else:
            app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
        
    except KeyboardInterrupt:
        print("🛑 Keyboard interrupt received")
        cleanup_resources()
    except Exception as e:
        print(f"❌ Application error: {e}")
        cleanup_resources()
        sys.exit(1) 