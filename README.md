# CounterApp

A well-structured Flask-based counter application demonstrating **Linqra integration** with Eureka service discovery and zero-trust security principles.

## Overview

This CounterApp serves as an **example application** to showcase how to integrate with the **Linqra platform**. It demonstrates key zero-trust security principles and service discovery patterns used in the Linqra ecosystem.

**🌐 Linqra Platform**: [https://github.com/mehmetsen80/Linqra](https://github.com/mehmetsen80/Linqra)

### **Zero-Trust Security Model**
- 🔒 **HTTPS everywhere**: Always runs on HTTPS with mutual TLS, even for localhost development
- 🔐 **Client certificate validation**: All requests require valid client certificates
- 🛡️ **No implicit trust**: No HTTP endpoints, only secure HTTPS communication
- 🔑 **Certificate-based authentication**: Server validates client certificates against CA bundle

### **Service Discovery Integration**
- 🌐 **Eureka registration**: App automatically registers with Eureka service discovery
- 🔍 **Service visibility**: Linqra can discover and route to this app via Eureka
- 📊 **Health monitoring**: Eureka monitors app health via `/health` endpoint
- 🔄 **Automatic lifecycle**: Registration on startup, deregistration on shutdown

### **Linqra Platform Integration**
This app demonstrates the standard patterns for integrating with Linqra:
- **Secure communication** with mutual TLS
- **Service discovery** via Eureka
- **Health monitoring** for load balancing
- **Graceful lifecycle management**

## Project Structure

```
CounterApp/
├── .venv/                    # Virtual environment
├── controllers/              # HTTP request handlers
│   ├── __init__.py
│   └── counter_controller.py
├── models/                   # Data models
│   ├── __init__.py
│   └── counter_model.py
├── services/                 # Business logic
│   ├── __init__.py
│   └── counter_service.py
├── enums/                    # Enum definitions
│   ├── __init__.py
│   └── status_enum.py
├── config/                   # Configuration modules
│   ├── __init__.py
│   └── eureka_config.py
├── tests/                    # Unit tests
│   ├── __init__.py
│   ├── test_app.py
│   ├── test_counter_service.py
│   └── test_status_enum.py
├── app.py                    # Main Flask application
├── run.py                    # Alternative run script
├── app_config.py             # Application configuration
├── requirements.txt          # Python dependencies
├── env.example               # Example environment variables
├── README.md                 # This file
└── .env                      # Environment variables (create this)
```

## Setup

1. **Activate your virtual environment:**
   ```bash
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate     # On Windows
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create environment file:**
   ```bash
   cp env.example .env
   # Edit .env with your specific values
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

The app will always run on `https://localhost:5001` with mutual TLS enabled by default, even for localhost development.

## Default Configuration

The CounterApp is configured with secure defaults:

### **Mutual TLS (mTLS) - Configurable**
- ✅ **HTTPS with optional client certificate validation**
- ✅ **Server certificate**: `keys/certs/server-cert.pem`
- ✅ **Server private key**: `keys/certs/server-key.pem`
- ✅ **CA bundle**: `keys/certs/ca-bundle.pem` (for client validation when mTLS enabled)
- ✅ **Client certificates required** only when `MUTUAL_TLS_ENABLED=true`

### **Running Without mTLS**
To run the app without requiring client certificates (for direct browser access):
```bash
export MUTUAL_TLS_ENABLED=false && python app.py
```

### **Running With mTLS (Default)**
To run the app with client certificate validation:
```bash
export MUTUAL_TLS_ENABLED=true && python app.py
# or simply
python app.py
```

### **Eureka Service Discovery - Enabled by Default**
- ✅ **Automatic registration** with Eureka server on startup
- ✅ **Health check endpoint**: `/health` (monitored by Eureka)
- ✅ **Graceful deregistration** on shutdown
- ✅ **Signal handling** for proper cleanup (SIGINT/SIGTERM)

### **How Eureka Registration Works**
1. **Startup**: App generates unique instance ID and registers with Eureka
2. **Health Monitoring**: Eureka polls `/health` endpoint every 30 seconds
3. **Shutdown**: App sends DELETE request to deregister from Eureka
4. **Instance ID Format**: `counter-app:<uuid>` (e.g., `counter-app:3613af7b-1d20-4a02-ab6c-a83d936b6a53`)

### **Environment Control**
You can disable features using environment variables:
```bash
# Disable Eureka registration
EUREKA_ENABLED=false python app.py

# Disable mutual TLS (use standard HTTPS)
MUTUAL_TLS_ENABLED=false python app.py

# Disable both
EUREKA_ENABLED=false MUTUAL_TLS_ENABLED=false python app.py
```

## Security Integration

The CounterApp implements enterprise-grade security similar to Java Spring Security:

### **Authentication Methods**
- 🔐 **JWT Token Authentication**: Bearer token validation
- 🛡️ **X.509 Certificate Authentication**: Client certificate validation
- 🔑 **Dual Authentication**: Supports both JWT and certificate auth
- 📝 **CN Extraction**: Extracts Common Name from certificates (similar to Java implementation)

### **Security Features**
- ✅ **Certificate Validation**: Validates client certificates against CA bundle
- ✅ **JWT Validation**: Validates JWT tokens with configurable issuers
- ✅ **Flexible Auth**: Endpoints can require specific auth methods
- ✅ **Zero-Trust**: All endpoints require authentication by default

### **Environment Variables for Security**
```bash
# Keycloak JWT Configuration (matching Spring Security)
KEYCLOAK_GATEWAY_URL=localhost
KEYCLOAK_GATEWAY_PORT=8281
JWT_ISSUER_URI=http://${KEYCLOAK_GATEWAY_URL}:${KEYCLOAK_GATEWAY_PORT}/realms/Linqra
JWT_JWK_SET_URI=http://${KEYCLOAK_GATEWAY_URL}:${KEYCLOAK_GATEWAY_PORT}/realms/Linqra/protocol/openid-connect/certs
```

### **Keycloak Configuration**

The CounterApp integrates with Keycloak for JWT authentication. Here's the required Keycloak setup:

#### **1. Client Scope Configuration**
Create a new client scope in Keycloak:
- **Name**: `counter-app.read`
- **Description**: To read the endpoint of counter-app
- **Display on consent screen**: ✅ ON
- **Include in token scope**: ✅ ON

#### **2. Gateway Client Configuration**
In the `linqra-gateway-client`:
- Go to **Client Scopes** tab
- Add scope: `counter-app.read` (OpenID Connect)
- Description: To read the endpoint of counter-app

#### **3. Route Configuration**
Create a route in the system:
- **Route Name**: `counter-app`
- **Required Scope**: `counter-app.read`
- **Target**: CounterApp service endpoints

#### **4. JWT Token Validation**
The CounterApp validates JWT tokens by:
- ✅ **Fetching JWK set** from Keycloak endpoint
- ✅ **Validating signature** using Keycloak's public keys
- ✅ **Checking issuer** against allowed Keycloak realms
- ✅ **Verifying scope** (`counter-app.read`) in token claims

### **Usage Examples**
```bash
# With JWT token (from Keycloak)
curl -H "Authorization: Bearer your-keycloak-jwt-token" https://localhost:5001/counter/api/v1/count

# With client certificate
curl --cert client-cert.pem --key client-key.pem https://localhost:5001/counter/api/v1/count

# JWT-only endpoint (requires Keycloak token)
curl -H "Authorization: Bearer your-keycloak-jwt-token" https://localhost:5001/counter/api/v1/count/protected

# Certificate-only endpoint
curl --cert client-cert.pem --key client-key.pem https://localhost:5001/counter/api/v1/count/cert-only
```

## Eureka Integration

The CounterApp automatically registers with Eureka service discovery on startup:

### Environment Variables for Eureka:
```bash
EUREKA_ENABLED=true                    # Enable/disable Eureka registration (enabled by default)
EUREKA_CLIENT_URL=localhost            # Eureka server host
EUREKA_CLIENT_PORT=8761               # Eureka server port
EUREKA_CLIENT_PATH=/eureka/eureka/    # Eureka server context path
EUREKA_INSTANCE_URL=localhost         # Instance host for registration
APP_NAME=counter-app                   # Application name in Eureka (required)
PORT=5001                             # Instance port
SECURE_PORT_ENABLED=true              # Use HTTPS for health checks
NON_SECURE_PORT_ENABLED=false         # Disable HTTP health checks
```

### Registration Process:
1. **Instance ID Generation**: Creates unique UUID for each app instance
2. **Registration Request**: POST to `https://localhost:8761/eureka/eureka/apps/COUNTER-APP`
3. **Health Check URL**: `https://localhost:5001/health` (HTTPS by default)
4. **Status Page URL**: `https://localhost:5001/` (HTTPS by default)
5. **Deregistration**: DELETE request on shutdown or signal

### Features:
- **Automatic Registration**: App registers with Eureka on startup
- **Health Checks**: Eureka monitors the `/health` endpoint via HTTPS
- **Graceful Shutdown**: App deregisters from Eureka on shutdown
- **Signal Handling**: Proper cleanup on SIGINT/SIGTERM
- **SSL Context**: Handles self-signed certificates for Eureka communication

## API Endpoints

### Core Endpoints
- `GET /` - Health check and API info
- `GET /health` - Health status (used by Eureka)

### Counter API (v1)
- `GET /counter/api/v1/count` - Get current count with metadata (requires JWT or X.509 certificate)
- `GET /counter/api/v1/count/increment` - Increment counter
- `GET /counter/api/v1/count/reset` - Reset counter to 0
- `GET /counter/api/v1/count/details` - Get detailed counter information
- `GET /counter/api/v1/count/protected` - Get count with JWT authentication only
- `GET /counter/api/v1/count/cert-only` - Get count with X.509 certificate authentication only

### API Documentation
- `GET /apidocs/` - Swagger UI documentation
- `GET /swagger.json` - OpenAPI specification

## Swagger Integration

The CounterApp includes comprehensive API documentation using Swagger/OpenAPI:

### **Swagger UI Interface**
- 🌐 **Direct Access**: `https://localhost:5001/r/counter-app/apidocs/` (⚠️ CSS/JS may not load due to context path)
- 🌐 **Gateway Access**: `https://localhost:7777/r/counter-app/apidocs/` (⚠️ CSS/JS may not load due to context path)
- 📖 **Interactive Documentation**: Test APIs directly from browser
- 🔐 **Authentication Support**: Shows JWT and certificate requirements
- 📋 **Request/Response Examples**: Complete API documentation
- ⚠️ **Note**: Swagger UI loads but CSS/JavaScript files may not display properly due to context path routing issues

### **API Documentation Endpoints**
- 📄 **Swagger 2.0**: `https://localhost:7777/r/counter-app/swagger.json` (flask-restx generated)
- 📄 **OpenAPI 3.1.0**: `https://localhost:7777/r/counter-app/openapi/openapi.json` (custom endpoint)
- 🌐 **Swagger UI**: `https://localhost:5001/r/counter-app/apidocs/` or `https://localhost:7777/r/counter-app/apidocs/` (interactive documentation)

### **Specification Formats**
- **Swagger 2.0**: Generated by flask-restx, compatible with Linqra
- **OpenAPI 3.1.0**: Custom specification matching Java implementation exactly
- **Usage**: Use `/openapi/openapi.json` for modern integrations, `/swagger.json` for legacy compatibility

### **OpenAPI 2.0 to 3.1.0 Conversion**

The CounterApp includes a conversion script to transform Flask-RESTX's Swagger 2.0 specification to OpenAPI 3.1.0 format:

#### **Conversion Script**
```bash
# Run the conversion script
python3 convert_to_openapi.py
```

This script will:
1. **Fetch** the Swagger 2.0 spec from your running app
2. **Convert** it to OpenAPI 3.1.0 format
3. **Save** it as `openapi_3_1_0.json`

#### **What the Script Does**
- ✅ **Fetches** Swagger 2.0 from `https://localhost:7777/r/counter-app/swagger.json` (gateway) or `https://localhost:5001/r/counter-app/swagger.json` (direct)
- ✅ **Converts** paths, schemas, and security definitions to OpenAPI 3.1.0 format
- ✅ **Updates** server URLs to include both gateway and direct access
- ✅ **Generates** a complete, valid OpenAPI 3.1.0 specification

#### **Generated Output**
The script creates `openapi_3_1_0.json` with:
- **16 paths** converted from Swagger 2.0
- **7 schemas** (data models)
- **2 security schemes** (Bearer token and X509 Certificate)
- **2 tags** (counter and health)
- **Multiple server URLs** for different access methods

#### **Usage Example**
```bash
# 1. Start your CounterApp
python3 app.py

# 2. Run the conversion script
python3 convert_to_openapi.py

# 3. Use the generated OpenAPI 3.1.0 spec
# The file openapi_3_1_0.json is now ready for use with Linqra or other tools
```

### **Linqra Integration**
To integrate with the Linqra platform:

1. **Access the OpenAPI spec**: `https://localhost:7777/r/counter-app/swagger.json`
2. **Copy the JSON content** from the response
3. **Import into Linqra gateway** using the JSON specification
4. **Configure routes** based on the documented endpoints

**For OpenAPI 3.1.0 Integration:**
1. **Generate** the OpenAPI 3.1.0 spec using the conversion script
2. **Use** the generated `openapi_3_1_0.json` file
3. **Import** into Linqra or other OpenAPI 3.1.0 compatible tools

### **Gateway Integration**
The CounterApp provides standard endpoints that the Linqra gateway can route to:

- **Health Check**: `https://localhost:5001/health` (for gateway health monitoring)
- **API Endpoints**: `https://localhost:5001/counter/api/v1/*` (all counter API endpoints)

The Linqra gateway is responsible for mapping `/r/counter-app/*` routes to these actual endpoints.

### **Service Discovery Fix**
The CounterApp automatically registers with the correct network IP address (not localhost) to ensure proper service discovery by the Linqra gateway. This resolves the 404 errors that occurred when the gateway tried to access the counter-app.

**Before Fix**:
- `ipAddr`: `127.0.0.1` (localhost)
- `hostName`: `localhost`
- Gateway couldn't reach the service

**After Fix**:
- `ipAddr`: `172.16.102.80` (actual network IP)
- `hostName`: `172.16.102.80` (actual network IP)
- Gateway can now properly route to the service

### **Documented Endpoints**
All API endpoints include comprehensive Swagger documentation:
- ✅ **Authentication requirements** (JWT/X.509)
- ✅ **Request/response schemas**
- ✅ **Error handling documentation**
- ✅ **Security definitions** (Bearer token, X.509 certificate)
- ✅ **Example responses** for all endpoints

### **Security Documentation**
The Swagger UI includes:
- 🔐 **Bearer Token**: JWT authentication from Keycloak
- 🛡️ **X.509 Certificate**: Client certificate authentication
- 📝 **Scope Requirements**: `counter-app.read` scope documentation
- ⚠️ **Error Responses**: 401 authentication errors documented

### Status Values
All API responses use standardized status values:
- `success` - Operation completed successfully
- `incremented` - Counter was incremented
- `reset` - Counter was reset to 0
- `error` - An error occurred
- `not_found` - Resource not found
- `bad_request` - Invalid request

### Example Response
```json
{
  "count": 5,
  "status": "success",
  "metadata": {
    "value": 5,
    "last_updated": "2025-07-08T20:45:30.123456",
    "description": "Main counter"
  }
}
```

## Testing

Run all tests:
```bash
python -m unittest discover tests
```

Run specific test files:
```bash
python -m unittest tests.test_app
python -m unittest tests.test_counter_service
python -m unittest tests.test_status_enum
```

## Environment Variables

Create a `.env` file in the root directory (see `env.example`):

```bash
# Flask Configuration
FLASK_ENV=development
PORT=5001

# SSL Configuration (enabled by default)
SSL_ENABLED=true
MUTUAL_TLS_ENABLED=true

# Eureka Configuration (enabled by default)
EUREKA_ENABLED=true
EUREKA_CLIENT_URL=localhost
EUREKA_CLIENT_PORT=8761
EUREKA_CLIENT_PATH=/eureka/eureka/
EUREKA_INSTANCE_URL=localhost
APP_NAME=counter-app
SECURE_PORT_ENABLED=true
NON_SECURE_PORT_ENABLED=false
```

**Note**: `APP_NAME` is required. If not set, the app will raise a `ValueError`.

## Configuration

The app uses different configurations based on the `FLASK_ENV` environment variable:

- **development**: Debug mode enabled, detailed error messages
- **production**: Debug mode disabled, optimized for production
- **testing**: Debug mode enabled, optimized for testing

You can run with different configurations:
```bash
# Development (default)
FLASK_ENV=development python app.py

# Production
FLASK_ENV=production python app.py

# Testing
FLASK_ENV=testing python app.py
```

## Architecture

This project follows a clean architecture pattern:

- **Controllers**: Handle HTTP requests and responses
- **Services**: Contain business logic
- **Models**: Define data structures (Counter model with value, timestamp, description)
- **Enums**: Define standardized values (StatusEnum for API responses)
- **Configuration**: Manage different environment settings
- **Eureka Integration**: Service discovery and registration

## Development

The application uses:
- **Flask Blueprints** for route organization
- **Application Factory Pattern** for better testing and configuration
- **Service Layer** for business logic separation
- **Data Models** for structured data representation
- **Enums** for type-safe status values
- **Eureka Client** for service discovery
- **Unit Tests** for both API and service layers

## Certificate Management and mTLS Setup

This application supports mutual TLS (mTLS) for secure communication. The certificate setup involves three main parts:

### Part 1: Java Keystore Creation (Linqra/keys folder)

**Step 1: Create Counter-App Keystore**
```bash
keytool -genkeypair -alias counter-app-container -keyalg RSA -keysize 2048 \
  -keystore counter-app-keystore-container.jks -validity 3650 -storetype PKCS12 \
  -dname "CN=counter-app, OU=Software, O=Dipme, L=Richmond, ST=TX, C=US" \
  -storepass 123456 -keypass 123456
```

**Step 2: Export Counter-App Certificate**
```bash
keytool -exportcert -alias counter-app-container \
  -file counter-app-cert-container.pem \
  -keystore counter-app-keystore-container.jks -storepass 123456
```

**Step 3: Import Certificate into Truststores**
```bash
# Import into Gateway truststore
keytool -importcert -file counter-app-cert-container.pem -alias counter-app-container \
  -keystore gateway-truststore.jks -storepass 123456

# Import into Client truststore
keytool -importcert -file counter-app-cert-container.pem -alias counter-app-container \
  -keystore client-truststore.jks -storepass 123456

# Import into Eureka truststore
keytool -importcert -file counter-app-cert-container.pem -alias counter-app-container \
  -keystore eureka-truststore.jks -storepass 123456
```

**Step 4: Copy Required Files to CounterApp**
```bash
# Copy the keystore and truststore to CounterApp/keys/
cp counter-app-keystore-container.jks /path/to/CounterApp/keys/
cp client-truststore.jks /path/to/CounterApp/keys/
```

### Part 2: Complete Certificate Setup (Automated)

**⚠️  IMPORTANT: Before running the script, check the JKS file name!**

If you're using a different JKS file than `counter-app-keystore-container.jks`, you need to modify the `KEYSTORE_FILE` variable in `generate_all_certs.py`:

```python
# ⚠️  IMPORTANT: This is the ONLY line you need to change if using a different JKS file!
KEYSTORE_FILE = 'counter-app-keystore-container.jks'  # Change this to your JKS file name
```

**Run Complete Certificate Setup Script**
```bash
python generate_all_certs.py
```
This script automatically handles ALL certificate setup parts:
- **1**: Get certificate aliases dynamically from truststore
- **2**: Extract all certificates from truststore (DER format)
- **3**: Convert DER certificates to PEM format
- **4**: Extract server certificate and private key from Java keystore
- **5**: Extract server private key from Java keystore
- **6**: Create CA bundle with all certificates
- **7**: Clean up temporary files and unnecessary certificates
- **8**: Create CA certificate for signing client certificates
- **9**: Create client certificate signed by the CA
- **10**: Update CA bundle with the CA certificate and cleanup

**Final files after script execution:**
- `server-cert.pem`: Server certificate (for Flask HTTPS)
- `server-key.pem`: Server private key (for Flask HTTPS)
- `ca-bundle.pem`: Combined CA certificates (for server validation)
- `ca-key.pem`: CA private key
- `ca-cert.pem`: CA certificate
- `client-key.pem`: Client private key
- `client-cert.pem`: Client certificate

*Note: The script is completely dynamic and will automatically detect and process all certificates in your truststore. All manual steps are now automated!*

### Part 3: Gateway Truststore Configuration

**Step 5: Add Counter-App Server Certificate to Gateway Truststore**

The Linqra gateway needs to trust the counter-app's server certificate for health checks and routing. Add the server certificate to the gateway's truststore:

```bash
keytool -import -alias counter-app-server -file keys/certs/server-cert.pem \
  -keystore /Users/mehmetsen/IdeaProjects/Linqra/keys/gateway-truststore.jks \
  -storepass 123456 -noprompt
```

This allows the gateway to:
- ✅ **Perform health checks** on `https://localhost:5001/health`
- ✅ **Route requests** to the counter-app service
- ✅ **Trust the server certificate** for secure communication

### Part 4: Without mTLS (Standard HTTPS)

**Step 6a: Start Flask App with Standard HTTPS**

For development and browser compatibility, you can run the app without mTLS:

```bash
export MUTUAL_TLS_ENABLED=false && python app.py
```

**Testing Standard HTTPS:**

**Test with curl (should succeed):**
```bash
curl -k https://localhost:5001/health
```

**Test in browser:**
- Open `https://localhost:5001/health` in Chrome
- Works without any certificate imports
- Standard HTTPS encryption only

### Part 5: With mTLS (Import Client Certificate for Browser Testing)

**Step 6b: Import Certificate into macOS Keychain**
```bash
# Import certificate into macOS Keychain for Chrome
security import keys/certs/client-cert.pem -k ~/Library/Keychains/login.keychain-db \
  -T /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome -f pemseq

# Import private key into macOS Keychain
security import keys/certs/client-key.pem -k ~/Library/Keychains/login.keychain-db \
  -T /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome -t priv
```

**Alternative: Import via Keychain Access GUI (Recommended)**
1. Open **Keychain Access** application
2. Go to **File → Import Items...**
3. Select `keys/certs/client-cert.pem` and `keys/certs/client-key.pem` files
4. Enter your macOS password when prompted
5. Set trust settings to "Always Trust" for testing

**Start Flask App with mTLS Enabled**

This step starts the Flask application with mutual TLS enabled.

```bash
export EUREKA_ENABLED=false && export MUTUAL_TLS_ENABLED=true && export HTTP_ENABLED=false && python app.py
```

### Testing mTLS

**Test with curl (should succeed):**
```bash
curl -vk --cert keys/certs/client-cert.pem --key keys/certs/client-key.pem https://127.0.0.1:5001/health
```

**Test without certificate (should fail):**
```bash
curl -vk https://127.0.0.1:5001/health
```

**Test in browser:**
- Open `https://127.0.0.1:5001/health` in Chrome
- Chrome will prompt for certificate selection
- Select the "client-app" certificate
- Enter your macOS password when prompted

### File Structure After Setup

```
CounterApp/keys/
├── counter-app-keystore-container.jks    # Java keystore (from Phase 1)
├── client-truststore.jks                 # Java truststore (from Phase 1)
└── certs/
    ├── server-cert.pem                  # Server certificate (for Flask HTTPS)
    ├── server-key.pem                   # Server private key (for Flask HTTPS)
    ├── ca-key.pem                       # CA private key
    ├── ca-cert.pem                      # CA certificate
    ├── client-key.pem                   # Client private key
    ├── client-cert.pem                  # Client certificate
    ├── client-cert.csr                  # Client certificate signing request
    ├── ca-bundle.pem                    # Combined CA certificates
    └── ... (other extracted certificates)
```

### Environment Variables for mTLS

```bash
MUTUAL_TLS_ENABLED=true                  # Enable mTLS
HTTP_ENABLED=false                       # Disable HTTP (use HTTPS only)
EUREKA_ENABLED=false                     # Disable Eureka for testing
``` 

## 🚀 Quick Start - Complete Setup

Once you have the CounterApp code and the required JKS files from the Linqra project, here's the complete setup process:

### **Step 1: Generate All Certificates**
```bash
# Generate all certificates and import server cert into gateway truststore
python generate_all_certs.py
```

This command will:
- ✅ Generate CA certificate and key
- ✅ Create client certificate and key  
- ✅ Create server certificate with localhost support
- ✅ Create CA bundle with all certificates
- ✅ Clean up temporary files
- ✅ **Import server certificate into gateway truststore** (NEW!)

### **Step 2: Start the Application**
```bash
# Start the counter-app with HTTPS and Eureka registration
python app.py
```

The app will:
- ✅ Start on `https://localhost:5001`
- ✅ Register with Eureka service discovery
- ✅ Enable health monitoring
- ✅ Support both JWT and certificate authentication

### **Step 3: Verify Everything Works**
```bash
# Test health endpoint directly
curl -k https://localhost:5001/health

# Test through gateway (if Linqra is running)
curl -k https://localhost:7777/r/counter-app/health
```

### **Complete Setup Summary**
```bash
# 1. Generate certificates (includes gateway truststore import)
python generate_all_certs.py

# 2. Start the application
python app.py

# 3. Test the endpoints
curl -k https://localhost:5001/health
```

That's it! The CounterApp is now fully integrated with the Linqra platform with:
- 🔐 **Secure HTTPS communication**
- 🌐 **Eureka service discovery**
- 🛡️ **JWT and certificate authentication**
- 📊 **Health monitoring**
- 🔄 **Gateway truststore integration** 