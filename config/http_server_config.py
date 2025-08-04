import threading
import logging
import time
from flask import Flask

logger = logging.getLogger(__name__)

# Global variable to track HTTP server thread
_http_server_thread = None
_shutdown_event = threading.Event()

def run_http_server(app, port, shutdown_event):
    """Run HTTP server in a separate thread with graceful shutdown support"""
    try:
        print(f"🌐 Starting HTTP server on port {port}")
        
        # Create a custom Flask app for HTTP server that can be stopped gracefully
        http_app = Flask(__name__)
        http_app.config.update(app.config)
        
        # Copy all routes from the main app
        for rule in app.url_map.iter_rules():
            http_app.add_url_rule(
                rule.rule,
                endpoint=rule.endpoint,
                view_func=app.view_functions[rule.endpoint],
                methods=rule.methods
            )
        
        # Start the server in a way that can be interrupted
        http_app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False, threaded=True)
        
    except Exception as e:
        print(f"❌ HTTP server error: {e}")
    finally:
        print(f"🛑 HTTP server on port {port} stopped")

def start_http_server_if_enabled(app, port, ssl_context):
    """Start HTTP server if enabled and HTTPS is disabled"""
    global _http_server_thread, _shutdown_event
    
    http_enabled = app.config.get('HTTP_ENABLED', False)
    
    if http_enabled and not ssl_context:
        http_port = port + 1000  # Use port 6001 for HTTP
        print(f"🌐 HTTP server enabled on port {http_port} (HTTPS disabled)")
        
        # Create and start the HTTP server thread
        _http_server_thread = threading.Thread(
            target=run_http_server, 
            args=(app, http_port, _shutdown_event),
            name="HTTP-Server-Thread"
        )
        _http_server_thread.daemon = True
        _http_server_thread.start()
        
        print(f"✅ HTTP server thread started: {_http_server_thread.name}")
        return _http_server_thread
    elif http_enabled and ssl_context:
        print("⚠️  HTTP server disabled (HTTPS is enabled)")
        return None
    
    return None

def stop_http_server():
    """Stop the HTTP server thread gracefully"""
    global _http_server_thread, _shutdown_event
    
    if _http_server_thread and _http_server_thread.is_alive():
        print(f"🛑 Stopping HTTP server thread: {_http_server_thread.name}")
        
        # Set shutdown event to signal the thread to stop
        _shutdown_event.set()
        
        # Wait for the thread to finish (with timeout)
        _http_server_thread.join(timeout=5)
        
        if _http_server_thread.is_alive():
            print("⚠️  HTTP server thread did not stop gracefully, forcing termination")
        else:
            print("✅ HTTP server thread stopped gracefully")
        
        _http_server_thread = None
    else:
        print("ℹ️  No HTTP server thread to stop")

def get_http_server_status():
    """Get the current status of the HTTP server thread"""
    global _http_server_thread
    
    if _http_server_thread is None:
        return {"status": "not_started", "thread_name": None, "is_alive": False}
    
    return {
        "status": "running" if _http_server_thread.is_alive() else "stopped",
        "thread_name": _http_server_thread.name,
        "is_alive": _http_server_thread.is_alive()
    } 