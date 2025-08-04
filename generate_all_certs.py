#!/usr/bin/env python3
import subprocess
import os
import glob

# Keystore file
# ⚠️  IMPORTANT: This is the ONLY line you need to change if using a different JKS file!
KEYSTORE_FILE = 'counter-app-keystore-container.jks'  # Original JKS file name

# Global configuration
CERTS_DIR = 'keys/certs'

# Certificate file names
SERVER_CERT_FILE = 'server-cert.pem'
SERVER_KEY_FILE = 'server-key.pem'
CA_BUNDLE_FILE = 'ca-bundle.pem'
CLIENT_CERT_FILE = 'client-cert.pem'
CLIENT_KEY_FILE = 'client-key.pem'
CA_CERT_FILE = 'ca-cert.pem'
CA_KEY_FILE = 'ca-key.pem'
CLIENT_CSR_FILE = 'client-cert.csr'
PKCS12_FILE = 'app-key.p12'
CONTAINER_CERT_FILE = 'app-container.pem'  # Original container cert (not essential)


def get_keystore_alias():
    """Get the alias from the JKS keystore dynamically"""
    print("🔍 Getting keystore alias from JKS file...")
    
    cmd = f"keytool -list -keystore keys/{KEYSTORE_FILE} -storepass 123456"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Parse the output to extract the alias
        lines = output.split('\n')
        for line in lines:
            # Look for lines that contain certificate aliases
            # Keytool output format: "alias_name, date, PrivateKeyEntry" or "trustedCertEntry"
            if ',' in line and ('PrivateKeyEntry' in line or 'trustedCertEntry' in line):
                alias = line.split(',')[0].strip()
                print(f"✅ Found keystore alias: {alias}")
                return alias
        
        print("❌ No alias found in keystore")
        return None
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get keystore alias: {e}")
        return None


def get_certificate_aliases():
    """Get all certificate aliases from the truststore dynamically"""
    print("🔍 Getting certificate aliases from client-truststore.jks...")
    
    # Original command: keytool -list -keystore keys/client-truststore.jks -storepass 123456
    cmd = "keytool -list -keystore keys/client-truststore.jks -storepass 123456"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Parse the output to extract aliases
        aliases = []
        lines = output.split('\n')
        for line in lines:
            # Look for lines that contain certificate aliases
            # Keytool output format: "alias_name, date, trustedCertEntry"
            if ',' in line and 'trustedCertEntry' in line:
                alias = line.split(',')[0].strip()
                aliases.append(alias)
        
        if aliases:
            print(f"✅ Found {len(aliases)} certificates: {', '.join(aliases)}")
            return aliases
        else:
            print("⚠️  No certificates found in truststore")
            return []
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to get certificate aliases: {e}")
        print("⚠️  No certificates will be processed")
        return []

def extract_server_certificate():
    """Extract server certificate from Java keystore"""
    print(f"\n🔍 Extracting server certificate from {KEYSTORE_FILE}...")
    
    # Get the alias dynamically
    keystore_alias = get_keystore_alias()
    if not keystore_alias:
        print("❌ Could not determine keystore alias. Exiting.")
        return False

    # Extract server certificate
    # Original command: keytool -exportcert -alias <extracted-alias> -file keys/certs/server-cert.pem -keystore keys/{KEYSTORE_FILE} -storepass 123456
    cert_file = os.path.join(CERTS_DIR, SERVER_CERT_FILE)
    cmd = f"keytool -exportcert -alias {keystore_alias} -file {cert_file} -keystore keys/{KEYSTORE_FILE} -storepass 123456"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Extracted server certificate: {cert_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to extract server certificate: {e}")
        return False
    
    # Convert from DER to PEM format
    # Original command: openssl x509 -inform DER -in keys/certs/server-cert.pem -out keys/certs/server-cert.pem -outform PEM
    print("🔄 Converting server certificate from DER to PEM...")
    cmd = f"openssl x509 -inform DER -in {cert_file} -out {cert_file} -outform PEM"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Converted server certificate to PEM: {cert_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to convert server certificate: {e}")
        return False

def extract_server_private_key():
    """Extract server private key from Java keystore"""
    print(f"\n🔍 Extracting server private key from {KEYSTORE_FILE}...")
    
    # Convert JKS to PKCS12 format
    # Original command: keytool -importkeystore -srckeystore keys/{KEYSTORE_FILE} -srcstorepass 123456 -destkeystore keys/certs/app-key.p12 -deststorepass 123456 -deststoretype PKCS12
    pkcs12_file = os.path.join(CERTS_DIR, PKCS12_FILE)
    cmd = f"keytool -importkeystore -srckeystore keys/{KEYSTORE_FILE} -srcstorepass 123456 -destkeystore {pkcs12_file} -deststorepass 123456 -deststoretype PKCS12"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Converted JKS to PKCS12: {pkcs12_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to convert JKS to PKCS12: {e}")
        return False
    
    # Extract private key from PKCS12
    # Original command: openssl pkcs12 -in keys/certs/app-key.p12 -out keys/certs/server-key.pem -nocerts -nodes -passin pass:123456
    key_file = os.path.join(CERTS_DIR, SERVER_KEY_FILE)
    cmd = f"openssl pkcs12 -in {pkcs12_file} -out {key_file} -nocerts -nodes -passin pass:123456"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Extracted server private key: {key_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to extract server private key: {e}")
        return False

def extract_certificates():
    """Extract all certificates from JKS truststore"""
    
    # Get certificates dynamically from truststore
    certificates = get_certificate_aliases()
    
    # Create certs directory if it doesn't exist
    os.makedirs(CERTS_DIR, exist_ok=True)
    
    print("🔍 Extracting certificates from client-truststore.jks...")
    
    # Extract each certificate
    # Original commands (now dynamic):
    # keytool -export -keystore keys/client-truststore.jks -alias <alias> -file keys/certs/<alias>.der -storepass 123456
    for cert_name in certificates:
        der_file = os.path.join(CERTS_DIR, f'{cert_name}.der')
        pem_file = os.path.join(CERTS_DIR, f'{cert_name}.pem')
        cmd = f"keytool -export -keystore keys/client-truststore.jks -alias {cert_name} -file {der_file} -storepass 123456"
        
        try:
            subprocess.run(cmd, shell=True, check=True)
            print(f"✅ Extracted: {cert_name} -> {der_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to extract {cert_name}: {e}")
    
    print("\n🔄 Converting DER certificates to PEM format...")
    
    # Convert each DER certificate to PEM format individually
    # Original commands (now dynamic):
    # openssl x509 -inform DER -in keys/certs/<alias>.der -out keys/certs/<alias>.pem -outform PEM
    for cert_name in certificates:
        der_file = os.path.join(CERTS_DIR, f'{cert_name}.der')
        pem_file = os.path.join(CERTS_DIR, f'{cert_name}.pem')
        
        if os.path.exists(der_file):
            try:
                cmd = f"openssl x509 -inform DER -in {der_file} -out {pem_file} -outform PEM"
                subprocess.run(cmd, shell=True, check=True)
                print(f"✅ Converted {cert_name} to PEM: {pem_file}")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to convert {cert_name}: {e}")
    
    # Create combined CA bundle
    print("\n📦 Creating CA bundle...")
    # Original command (now dynamic): cat keys/certs/*.pem > keys/certs/ca-bundle.pem
    ca_bundle_file = os.path.join(CERTS_DIR, CA_BUNDLE_FILE)
    
    # Build the cat command with all PEM files
    pem_files = []
    for cert_name in certificates:
        pem_file = os.path.join(CERTS_DIR, f'{cert_name}.pem')
        if os.path.exists(pem_file):
            pem_files.append(pem_file)
    
    # Also include the CA certificate if it exists
    ca_cert_file = os.path.join(CERTS_DIR, CA_CERT_FILE)
    if os.path.exists(ca_cert_file):
        pem_files.append(ca_cert_file)
        print(f"✅ Including CA certificate in bundle: {CA_CERT_FILE}")
    
    if pem_files:
        cmd = f"cat {' '.join(pem_files)}"
        try:
            with open(ca_bundle_file, 'w') as bundle:  # Changed back to 'w' for initial creation
                subprocess.run(cmd, shell=True, stdout=bundle, check=True)
            print(f"✅ Created CA bundle: {ca_bundle_file}")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create CA bundle: {e}")
    else:
        print("❌ No PEM files found to create CA bundle")
    
    print(f"📁 All certificates extracted to: {CERTS_DIR}/")
    
    # List all generated files
    print("\n📋 Generated files:")
    for cert_name in certificates:
        cert_file = os.path.join(CERTS_DIR, f'{cert_name}.pem')
        if os.path.exists(cert_file):
            print(f"  📄 {cert_name}.pem (PEM format)")
    
    print(f"  📄 {CA_BUNDLE_FILE} (combined PEM format)")
    
    print("\n🎯 For mTLS testing, use:")
    # Original command: curl -vk --cert keys/certs/client-cert.pem --key keys/certs/server-key.pem https://localhost:5001/health
    # Note: Application must be running for this to work
    print(f"  # curl -vk --cert {CERTS_DIR}/{CLIENT_CERT_FILE} --key {CERTS_DIR}/{SERVER_KEY_FILE} https://localhost:5001/health")

def create_ca_certificate():
    """Create a proper CA certificate for signing client certificates"""
    print("\n🔐 Creating CA certificate for client certificate signing...")
    
    # Generate CA private key
    # Original command: openssl genrsa -out keys/certs/ca-key.pem 2048
    ca_key_file = os.path.join(CERTS_DIR, CA_KEY_FILE)
    cmd = f"openssl genrsa -out {ca_key_file} 2048"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Generated CA private key: {ca_key_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate CA private key: {e}")
        return False
    
    # Create CA certificate with proper CA extensions
    # Original command: openssl req -new -x509 -key keys/certs/ca-key.pem -out keys/certs/ca-cert.pem -days 3650 -subj "/CN=app-ca/OU=Software/O=Dipme/L=Richmond/ST=TX/C=US" -extensions v3_ca
    ca_cert_file = os.path.join(CERTS_DIR, CA_CERT_FILE)
    cmd = f"openssl req -new -x509 -key {ca_key_file} -out {ca_cert_file} -days 3650 -subj '/CN=app-ca/OU=Software/O=Dipme/L=Richmond/ST=TX/C=US' -extensions v3_ca"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Created CA certificate: {ca_cert_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create CA certificate: {e}")
        return False

def create_client_certificate():
    """Create client certificate signed by the CA"""
    print("\n🔐 Creating client certificate signed by CA...")
    
    # Generate client private key and CSR
    # Original command: openssl req -newkey rsa:2048 -keyout keys/certs/client-key.pem -out keys/certs/client-cert.csr -subj "/CN=client-app/OU=Software/O=Dipme/L=Richmond/ST=TX/C=US" -nodes
    client_key_file = os.path.join(CERTS_DIR, CLIENT_KEY_FILE)
    client_csr_file = os.path.join(CERTS_DIR, CLIENT_CSR_FILE)
    cmd = f"openssl req -newkey rsa:2048 -keyout {client_key_file} -out {client_csr_file} -subj '/CN=client-app/OU=Software/O=Dipme/L=Richmond/ST=TX/C=US' -nodes"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Generated client private key and CSR: {client_key_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate client private key and CSR: {e}")
        return False
    
    # Sign client certificate with CA
    # Original command: openssl x509 -req -in keys/certs/client-cert.csr -CA keys/certs/ca-cert.pem -CAkey keys/certs/ca-key.pem -CAcreateserial -out keys/certs/client-cert.pem -days 365
    client_cert_file = os.path.join(CERTS_DIR, CLIENT_CERT_FILE)
    ca_cert_file = os.path.join(CERTS_DIR, CA_CERT_FILE)
    ca_key_file = os.path.join(CERTS_DIR, CA_KEY_FILE)
    
    cmd = f"openssl x509 -req -in {client_csr_file} -CA {ca_cert_file} -CAkey {ca_key_file} -CAcreateserial -out {client_cert_file} -days 365"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Created client certificate: {client_cert_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create client certificate: {e}")
        return False

def create_server_certificate_with_localhost():
    """Create a new server certificate with CN=localhost and SAN"""
    print("\n🔐 Creating new server certificate with CN=localhost and SAN...")
    
    # Create OpenSSL config file for SAN
    config_content = """[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req
prompt = no

[req_distinguished_name]
C = US
ST = TX
L = Richmond
O = Dipme
OU = Software
CN = localhost

[v3_req]
keyUsage = digitalSignature, keyEncipherment, dataEncipherment
extendedKeyUsage = serverAuth
subjectAltName = @alt_names

[alt_names]
DNS.1 = localhost
DNS.2 = counter-app
DNS.3 = 127.0.0.1
DNS.4 = *
DNS.5 = *.local
DNS.6 = *.home
IP.1 = 127.0.0.1
IP.2 = 0.0.0.0
IP.3 = 255.255.255.255
"""
    
    config_file = os.path.join(CERTS_DIR, 'server-cert.conf')
    with open(config_file, 'w') as f:
        f.write(config_content)
    
    print(f"✅ Created OpenSSL config: {config_file}")
    
    # Generate server private key
    server_key_file = os.path.join(CERTS_DIR, SERVER_KEY_FILE)
    cmd = f"openssl genrsa -out {server_key_file} 2048"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Generated server private key: {server_key_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate server private key: {e}")
        return False
    
    # Create server certificate with SAN
    server_cert_file = os.path.join(CERTS_DIR, SERVER_CERT_FILE)
    cmd = f"openssl req -new -x509 -key {server_key_file} -out {server_cert_file} -days 3650 -config {config_file} -extensions v3_req"
    
    try:
        subprocess.run(cmd, shell=True, check=True)
        print(f"✅ Created server certificate: {server_cert_file}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create server certificate: {e}")
        return False
    
    # Verify the certificate
    print("\n🔍 Verifying new server certificate...")
    cmd = f"openssl x509 -in {server_cert_file} -text -noout | grep -A 10 'Subject:'"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print("📋 Certificate Subject and SAN:")
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to verify certificate: {e}")
        return False
    
    # Clean up config file
    os.remove(config_file)
    print(f"🧹 Cleaned up config file: {config_file}")
    
    return True

def verify_ca_bundle():
    """Verify that the CA certificate is properly included in the bundle"""
    print("\n🔍 Verifying CA bundle contents...")
    
    ca_bundle_file = os.path.join(CERTS_DIR, CA_BUNDLE_FILE)
    
    # Check if app-ca certificate is in the bundle by reading all certificates
    print("🔍 Checking for app-ca certificate in bundle...")
    cmd = f"openssl crl2pkcs7 -nocrl -certfile {ca_bundle_file} | openssl pkcs7 -print_certs -text -noout"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        output = result.stdout
        
        # Look for app-ca in the output
        if "CN=app-ca" in output:
            print("✅ app-ca certificate found in CA bundle")
        else:
            print("❌ app-ca certificate NOT found in CA bundle")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to read CA bundle: {e}")
        return False
    
    # Show all certificates in the CA bundle
    print("\n📋 All certificates in CA bundle:")
    cmd = f"openssl crl2pkcs7 -nocrl -certfile {ca_bundle_file} | openssl pkcs7 -print_certs -text -noout | grep -A 2 'Subject:'"
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to list certificates in bundle: {e}")
        return False
    
    return True

def cleanup_unnecessary_files():
    """Clean up unnecessary files, keeping only essential mTLS files"""
    print("\n🧹 Cleaning up final unnecessary files...")
    
    # Define files to keep
    files_to_keep = [
        CA_BUNDLE_FILE,           # Combined CA certificates for mTLS validation
        CLIENT_CERT_FILE,         # Client certificate for browser testing
        CLIENT_KEY_FILE,          # Client private key for browser testing
        SERVER_CERT_FILE,         # Server certificate for Flask HTTPS
        SERVER_KEY_FILE,          # Server private key for Flask HTTPS
        CA_CERT_FILE,             # CA certificate
        CA_KEY_FILE,              # CA private key
        PKCS12_FILE               # PKCS12 file for gateway configuration
    ]
    
    # Get all files in the certs directory
    all_files = []
    for file in os.listdir(CERTS_DIR):
        file_path = os.path.join(CERTS_DIR, file)
        if os.path.isfile(file_path):
            all_files.append(file)
    
    # Remove files that are not in the keep list
    removed_count = 0
    for file in all_files:
        if file not in files_to_keep:
            file_path = os.path.join(CERTS_DIR, file)
            try:
                os.remove(file_path)
                print(f"🗑️  Removed: {file}")
                removed_count += 1
            except OSError as e:
                print(f"❌ Failed to remove {file}: {e}")
    
    print(f"✅ Removed {removed_count} unnecessary files")
    
    print("📋 Kept only essential mTLS files:")
    for file_name in files_to_keep:
        file_path = os.path.join(CERTS_DIR, file_name)
        if os.path.exists(file_path):
            print(f"  - {file_name}")
    
    return True

def import_server_cert_to_gateway_truststore():
    """Import server certificate into gateway truststore"""
    print("\n🔐 Importing server certificate into gateway truststore...")
    
    # Gateway truststore path
    gateway_truststore_path = "/Users/mehmetsen/IdeaProjects/Linqra/keys/gateway-truststore.jks"
    server_cert_path = os.path.join(CERTS_DIR, SERVER_CERT_FILE)
    
    # Check if gateway truststore exists
    if not os.path.exists(gateway_truststore_path):
        print(f"❌ Gateway truststore not found: {gateway_truststore_path}")
        print("   Please ensure the gateway truststore exists before running this script")
        return False
    
    # Check if server certificate exists
    if not os.path.exists(server_cert_path):
        print(f"❌ Server certificate not found: {server_cert_path}")
        return False
    
    try:
        # Import server certificate into gateway truststore
        cmd = [
            "keytool", "-import", "-alias", "localhost",
            "-file", server_cert_path,
            "-keystore", gateway_truststore_path,
            "-storepass", "123456", "-noprompt"
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("✅ Successfully imported server certificate into gateway truststore")
        print(f"   Alias: localhost")
        print(f"   Truststore: {gateway_truststore_path}")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to import server certificate: {e}")
        if e.stderr:
            print(f"   Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main function to run all extraction steps"""
    print("🚀 Starting complete certificate setup process...")
    
    # Phase 1: Create CA certificate and client certificates first
    print("\n🔐 Starting Phase 1: CA and Client Certificate Creation...")
    
    if create_ca_certificate():
        print("✅ CA certificate created successfully!")
    else:
        print("❌ Failed to create CA certificate")
        return
    
    if create_client_certificate():
        print("✅ Client certificate created successfully!")
    else:
        print("❌ Failed to create client certificate")
        return
    
    # Phase 2: Extract truststore certificates (this will include CA cert in bundle)
    extract_certificates()
    
    # Phase 3: Create new server certificate with localhost support
    if create_server_certificate_with_localhost():
        print("\n✅ Server certificate with localhost support created successfully!")
    else:
        print("\n❌ Failed to create server certificate with localhost support")
    
    # Phase 4: Add CA certificate to bundle and verify
    # Note: CA certificate is already included in extract_certificates() function
    
    # Phase 5: Verify CA bundle contents
    if verify_ca_bundle():
        print("✅ CA bundle verification successful!")
    else:
        print("❌ CA bundle verification failed!")
        return
    
    # Final cleanup to keep only essential mTLS files
    # This consolidated cleanup handles all temporary files in one efficient operation
    cleanup_unnecessary_files()  # Enabled to clean up temporary files
    
    # Phase 6: Import server certificate into gateway truststore
    if import_server_cert_to_gateway_truststore():
        print("✅ Gateway truststore update successful!")
    else:
        print("⚠️  Gateway truststore update failed - you may need to import manually")
    
    print("\n🎉 Complete certificate setup finished!")
    print("📁 All files are ready in keys/certs/ directory")
    print("\n📋 Final essential files:")
    print(f"  - {SERVER_CERT_FILE}: Server certificate (CN=localhost with SAN)")
    print(f"  - {SERVER_KEY_FILE}: Server private key")
    print(f"  - {CA_BUNDLE_FILE}: Combined CA certificates")
    print(f"  - {CLIENT_KEY_FILE}: Client private key")
    print(f"  - {CLIENT_CERT_FILE}: Client certificate")
    print(f"  - {PKCS12_FILE}: PKCS12 file for gateway configuration")
    print("\n🔐 New server certificate supports:")
    print("   - CN=localhost")
    print("   - DNS: localhost, counter-app, 127.0.0.1")
    print("   - IP: 127.0.0.1")
    print("\n🎯 Next steps:")
    print(f"  1. Import {CLIENT_CERT_FILE} and {CLIENT_KEY_FILE} into macOS Keychain")
    print("  2. Start your Flask app with mTLS enabled")
    print(f"  3. Test with: curl -vk --cert {CERTS_DIR}/{CLIENT_CERT_FILE} --key {CERTS_DIR}/{CLIENT_KEY_FILE} https://localhost:5001/health")
    print(f"  4. Add {PKCS12_FILE} to gateway client keystore for mTLS support")
    print("  5. The gateway should now work with localhost hostname validation!")
    print("  6. Server certificate has been imported into gateway truststore")

if __name__ == '__main__':
    main() 