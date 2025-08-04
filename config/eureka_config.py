import os
import uuid
import ssl
import urllib.request
import threading
import time
import socket
from dotenv import load_dotenv

load_dotenv()

# Global Eureka configuration instance
_eureka_config = None

def get_eureka_config():
    """Get Eureka configuration based on environment"""
    global _eureka_config
    if _eureka_config is None:
        current_env = os.environ.get('FLASK_ENV', 'development')
        _eureka_config = EurekaConfig(environment=current_env)
    return _eureka_config

def register_with_eureka():
    """Register with Eureka on startup"""
    try:
        eureka_config = get_eureka_config()
        success = eureka_config.register_with_eureka()
        if success:
            # Start heartbeat after successful registration
            eureka_config.start_heartbeat()
    except Exception as e:
        print(f"❌ Failed to register with Eureka: {e}")

def deregister_from_eureka():
    """Deregister from Eureka on shutdown"""
    try:
        eureka_config = get_eureka_config()
        eureka_config.deregister_from_eureka()
    except Exception as e:
        print(f"❌ Failed to deregister from Eureka: {e}")

def stop_heartbeat():
    """Stop the Eureka heartbeat"""
    try:
        eureka_config = get_eureka_config()
        eureka_config.stop_heartbeat()
    except Exception as e:
        print(f"❌ Failed to stop Eureka heartbeat: {e}")

class EurekaConfig:
    """Eureka client configuration for service discovery (matching Java Spring Boot pattern)"""
    
    def __init__(self, environment=None):
        # Determine environment (matching Java profiles)
        self.environment = environment or os.environ.get('FLASK_ENV', 'development')
        
        # Eureka server configuration (matching Java Spring Boot pattern)
        self.eureka_server = os.environ.get('EUREKA_CLIENT_URL', 'localhost')
        self.eureka_port = os.environ.get('EUREKA_CLIENT_PORT', '8761')
        self.eureka_path = os.environ.get('EUREKA_CLIENT_PATH', '/eureka/eureka/')
        
        # Build the full Eureka server URL - use HTTPS by default
        self.eureka_server_url = f"https://{self.eureka_server}:{self.eureka_port}{self.eureka_path}"
        
        # Application configuration
        self.app_name = os.environ.get('APP_NAME')
        if not self.app_name:
            raise ValueError("APP_NAME environment variable is required but not set")
        
        self.instance_port = int(os.environ.get('PORT', 5001))
        self.instance_host = os.environ.get('EUREKA_INSTANCE_URL', 'localhost')
        
        # Get the actual network IP address for service discovery
        self.instance_ip = self._get_network_ip()
        print(f"🔍 Constructor: self.instance_ip = {self.instance_ip}")
        
        # Instance ID: always generate a new UUID
        self.instance_id = f"{self.app_name}:{str(uuid.uuid4())}"
        
        # Security configuration (matching Java pattern)
        self.secure_port_enabled = os.environ.get('SECURE_PORT_ENABLED', 'true').lower() == 'true'
        self.non_secure_port_enabled = os.environ.get('NON_SECURE_PORT_ENABLED', 'false').lower() == 'true'
        
        # Heartbeat configuration
        self.heartbeat_interval = 30  # seconds
        self.heartbeat_thread = None
        self.heartbeat_running = False
        
        # Environment-specific overrides
        self._apply_environment_overrides()
        
        # Health check configuration
        protocol = 'https' if self.secure_port_enabled else 'http'
        self.health_check_url = f"{protocol}://{self.instance_host}:{self.instance_port}/health"
        self.status_page_url = f"{protocol}://{self.instance_host}:{self.instance_port}/"
        
        # Configure SSL context for self-signed certificates
        self._configure_ssl_context()
        
    def _get_network_ip(self):
        """Get the actual network IP address (not localhost)"""
        try:
            # Create a socket to get the local IP address
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Connect to a remote address (doesn't actually send data)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            print(f"🔍 Detected network IP: {ip}")
            return ip
        except Exception as e:
            print(f"⚠️  Network IP detection failed: {str(e)}")
            # Try alternative method
            try:
                hostname = socket.gethostname()
                ip = socket.gethostbyname(hostname)
                print(f"🔍 Alternative IP detection: {ip}")
                return ip
            except Exception as e2:
                print(f"⚠️  Alternative IP detection also failed: {str(e2)}")
                # Fallback to localhost if network detection fails
                return "127.0.0.1"
        
    def _configure_ssl_context(self):
        """Configure SSL context to handle self-signed certificates"""
        try:
            # Create SSL context that bypasses certificate verification
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create HTTPS handler with the SSL context
            https_handler = urllib.request.HTTPSHandler(context=ssl_context)
            
            # Install the handler globally
            opener = urllib.request.build_opener(https_handler)
            urllib.request.install_opener(opener)
            
            print("SSL context configured for self-signed certificates")
        except Exception as e:
            print(f"Warning: Could not configure SSL context: {str(e)}")
        
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides"""
        if self.environment == 'development':
            # Development: Use HTTPS for local development
            self.secure_port_enabled = True
            self.non_secure_port_enabled = False
            # Use the correct double context path
            self.eureka_server_url = f"https://{self.eureka_server}:{self.eureka_port}{self.eureka_path}"
            
        elif self.environment == 'production':
            # Production: Use HTTPS, secure settings
            self.secure_port_enabled = True
            self.non_secure_port_enabled = False
            
        elif self.environment == 'testing':
            # Testing: Use HTTP for localhost, but HTTPS for Eureka server
            self.secure_port_enabled = False
            self.non_secure_port_enabled = True
            # Keep HTTPS for Eureka server since it's running on HTTPS
            # Use the correct double context path
            self.eureka_server_url = f"https://{self.eureka_server}:{self.eureka_port}{self.eureka_path}"
        
    def register_with_eureka(self):
        """Register with Eureka using direct HTTP POST"""
        try:
            if not self.app_name:
                print("⚠️  APP_NAME environment variable is not set. Skipping Eureka registration.")
                return False

            import json
            import urllib.request
            import urllib.error
            import ssl
            
            print(f"🔄 Registering with Eureka server: {self.eureka_server_url}")
            
            # Create SSL context for HTTPS
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Prepare instance data with correct format (matching Spring Boot pattern)
            print(f"🔍 Registration: self.instance_ip = {self.instance_ip}")
            instance_data = {
                "instance": {
                    "instanceId": self.instance_id,
                    "hostName": self.instance_host,
                    "app": self.app_name,
                    "ipAddr": self.instance_ip,
                    "status": "UP",
                    "overriddenstatus": "UNKNOWN",
                    "port": {"$": self.instance_port, "@enabled": "false"},  # HTTP port disabled
                    "securePort": {"$": self.instance_port, "@enabled": "true"},  # HTTPS port enabled
                    "countryId": 1,
                    "dataCenterInfo": {
                        "@class": "com.netflix.appinfo.InstanceInfo$DefaultDataCenterInfo",
                        "name": "MyOwn"
                    },
                    "leaseInfo": {
                        "renewalIntervalInSecs": 30,
                        "durationInSecs": 90,
                        "registrationTimestamp": 0,
                        "lastRenewalTimestamp": 0,
                        "evictionTimestamp": 0,
                        "serviceUpTimestamp": 0
                    },
                    "metadata": {},
                    "homePageUrl": f"http://{self.instance_host}:{self.instance_port}/",  # HTTP URL
                    "statusPageUrl": f"http://{self.instance_host}:{self.instance_port}/",  # HTTP status URL (using home page since actuator/info was removed)
                    "secureHealthCheckUrl": f"https://{self.instance_host}:{self.instance_port}/health",  # HTTPS health check (using regular health endpoint)
                    "vipAddress": self.app_name,
                    "secureVipAddress": self.app_name,
                    "isCoordinatingDiscoveryServer": False,
                    "lastUpdatedTimestamp": 0,
                    "lastDirtyTimestamp": 0,
                    "actionType": "ADDED"
                }
            }
            
            # Create request
            url = f"{self.eureka_server_url}apps/{self.app_name}"
            data = json.dumps(instance_data).encode('utf-8')
            
            print(f"📤 Sending registration to: {url}")
            print(f"📦 Payload: {json.dumps(instance_data, indent=2)}")
            
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                },
                method='POST'
            )
            
            # Send request
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                response_body = response.read().decode('utf-8')
                print(f"📥 Response status: {response.status}")
                print(f"📥 Response body: {response_body}")
                
                if response.status == 204:
                    print(f"✅ Successfully registered with Eureka server: {url}")
                    return True
                else:
                    print(f"⚠️  Registration returned status: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            print(f"💡 Response body: {e.read().decode('utf-8')}")
            return False
        except Exception as e:
            print(f"❌ Failed to register with Eureka: {str(e)}")
            return False
    
    def deregister_from_eureka(self):
        """Deregister the application from Eureka server"""
        try:
            if not self.app_name:
                print("⚠️  APP_NAME environment variable is not set. Skipping Eureka deregistration.")
                return False

            import urllib.request
            import urllib.error
            import ssl
            
            print(f"🔄 Deregistering from Eureka server: {self.eureka_server_url}")
            
            # Create SSL context for HTTPS
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create DELETE request - FIXED URL format
            url = f"{self.eureka_server_url}apps/{self.app_name}/{self.instance_id}"
            
            req = urllib.request.Request(
                url,
                headers={
                    'Accept': 'application/json'
                },
                method='DELETE'
            )
            
            # Send request
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                if response.status == 200:
                    print(f"✅ Successfully deregistered from Eureka server: {url}")
                    return True
                else:
                    print(f"⚠️  Deregistration returned status: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            print(f"❌ HTTP Error {e.code}: {e.reason}")
            return False
        except Exception as e:
            print(f"❌ Failed to deregister from Eureka: {str(e)}")
            return False

    def start_heartbeat(self):
        """Start the heartbeat renewal thread"""
        if self.heartbeat_thread is None or not self.heartbeat_thread.is_alive():
            self.heartbeat_running = True
            self.heartbeat_thread = threading.Thread(target=self._heartbeat_worker, daemon=True)
            self.heartbeat_thread.start()
            print(f"💓 Started Eureka heartbeat thread (interval: {self.heartbeat_interval}s)")
    
    def stop_heartbeat(self):
        """Stop the heartbeat renewal thread"""
        self.heartbeat_running = False
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=5)
            print("💓 Stopped Eureka heartbeat thread")
    
    def _heartbeat_worker(self):
        """Background worker that sends periodic heartbeats to Eureka"""
        while self.heartbeat_running:
            try:
                self.send_heartbeat()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                print(f"❌ Heartbeat error: {str(e)}")
                time.sleep(self.heartbeat_interval)
    
    def send_heartbeat(self):
        """Send heartbeat renewal to Eureka server"""
        try:
            import urllib.request
            import urllib.error
            import ssl
            
            # Create SSL context for HTTPS
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            # Create PUT request for heartbeat
            url = f"{self.eureka_server_url}apps/{self.app_name}/{self.instance_id}"
            
            req = urllib.request.Request(
                url,
                headers={
                    'Accept': 'application/json'
                },
                method='PUT'
            )
            
            # Send request
            with urllib.request.urlopen(req, context=ssl_context, timeout=10) as response:
                if response.status == 200:
                    print(f"💓 Heartbeat sent successfully to Eureka")
                    return True
                else:
                    print(f"⚠️  Heartbeat returned status: {response.status}")
                    return False
                    
        except urllib.error.HTTPError as e:
            print(f"❌ Heartbeat HTTP Error {e.code}: {e.reason}")
            return False
        except Exception as e:
            print(f"❌ Failed to send heartbeat: {str(e)}")
            return False