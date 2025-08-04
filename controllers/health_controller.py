from flask import jsonify
from flask_restx import Resource, fields, Namespace
import psutil
import time
from datetime import datetime, timedelta, timezone
import os

# Create namespace for health API documentation
api = Namespace('health', description='Health check APIs')

# Define response models
health_status_model = api.model('HealthStatus', {
    'serviceId': fields.String(description='Service identifier'),
    'status': fields.String(description='Health status (UP/DOWN)'),
    'uptime': fields.String(description='Service uptime in human readable format'),
    'timestamp': fields.String(description='Current timestamp'),
    'metrics': fields.Raw(description='System metrics including CPU, memory, and response time')
})

@api.route('/')
@api.route('')
class HealthResource(Resource):
    @api.doc('get_health',
             description='Get comprehensive health status matching Java implementation',
             responses={
                 200: ('Service is healthy', health_status_model),
                 503: ('Service is unhealthy', health_status_model)
             })
    def get(self):
        """Get comprehensive health status matching Java implementation"""
        health_status = health_controller.get_health_status()
        
        # Return appropriate HTTP status based on health
        if health_status['status'] == 'UP':
            return health_status, 200
        else:
            return health_status, 503

class HealthController:
    """Health controller matching Java Spring Boot implementation"""
    
    def __init__(self):
        self.start_time = time.time()
        self.service_id = os.environ.get('APP_NAME', 'counter-app')
    
    def is_healthy(self):
        """Check if the service is healthy"""
        try:
            # Get process-specific metrics (not system-wide)
            process = psutil.Process()
            memory_info = process.memory_info()
            memory_percent = process.memory_percent()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Define thresholds (matching Java implementation)
            memory_threshold = 90.0  # 80% memory usage threshold for process
            cpu_threshold = 0  # CPU load should be >= 0
            
            # Check if process is healthy
            memory_healthy = memory_percent < memory_threshold
            cpu_healthy = cpu_percent >= cpu_threshold
            
            # Debug logging
            print(f"🔍 Health Check - Process Memory: {memory_percent:.2f}% (threshold: {memory_threshold}%), CPU: {cpu_percent}% (threshold: {cpu_threshold}%)")
            print(f"🔍 Health Check - Memory healthy: {memory_healthy}, CPU healthy: {cpu_healthy}")
            
            return memory_healthy and cpu_healthy
        except Exception as e:
            print(f"Error checking service health: {e}")
            return False
    
    def format_uptime(self, uptime_seconds):
        """Format uptime in human readable format (matching Java implementation)"""
        uptime = timedelta(seconds=uptime_seconds)
        days = uptime.days
        hours = uptime.seconds // 3600
        minutes = (uptime.seconds % 3600) // 60
        seconds = uptime.seconds % 60
        
        return f"{days}d {hours}h {minutes}m {seconds}s"
    
    def measure_response_time(self):
        """Measure baseline response time (matching Java implementation)"""
        start_time = time.perf_counter()
        # Perform a simple operation to measure baseline response time
        _ = psutil.virtual_memory()
        end_time = time.perf_counter()
        return (end_time - start_time) * 1000  # Convert to milliseconds
    
    def get_health_status(self):
        """Get comprehensive health status (matching Java implementation)"""
        try:
            # Get process-specific metrics (not system-wide)
            process = psutil.Process()
            memory_percent = process.memory_percent()
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Calculate uptime
            uptime_seconds = time.time() - self.start_time
            
            # Set health status details
            healthy = self.is_healthy()
            status = "UP" if healthy else "DOWN"
            uptime = self.format_uptime(uptime_seconds)
            timestamp = datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')
            
            # Add detailed metrics (matching Java implementation)
            metrics = {
                "cpu":round(cpu_percent, 2),
                "memory":round(memory_percent, 2),
                "responseTime":round(self.measure_response_time(), 2)
            }
            
            return {
                "serviceId": self.service_id,
                "status":status,
                "uptime":uptime,
                "timestamp":timestamp,
                "metrics":metrics
            }
            
        except Exception as e:
            print(f"Error getting health status: {e}")
            return {
                "serviceId":self.service_id,
                "status":"DOWN",
                "uptime":"0d 0h 0m 0s",
                "timestamp":datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
                "metrics": {
                    "error":1.0,
                    "message":0.0
                }
            }

# Create health controller instance
health_controller = HealthController()

 