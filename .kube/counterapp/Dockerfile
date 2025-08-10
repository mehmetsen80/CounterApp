# Dockerfile for counterapp

# Stage 1: Build the application using Python
FROM python:3.11-slim AS build

# Set the working directory in the build image
WORKDIR /app/counter-app

# Debug: List what's being copied
RUN pwd
RUN ls -la

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project to the Docker container
COPY . .

# Debug: List all Python files
RUN find /app/counter-app -name "*.py" -type f

# Stage 2: Create the runtime image with Python and application
FROM python:3.11-slim

# Install necessary packages
RUN apt-get update && apt-get install -y \
    net-tools \
    iputils-ping \
    openssl \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the runtime image
WORKDIR /app/counter-app

# Copy Python dependencies from build image
COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

# Copy the application code from build image
COPY --from=build /app/counter-app .

# Copy the keystore and truststore files from root keys directory
COPY keys/counter-app-keystore-container.jks /app/keys/counter-app-keystore-container.jks
COPY keys/client-truststore.jks /app/keys/client-truststore.jks

# Copy all certificate files from keys/certs directory
COPY keys/certs/ca-bundle.pem /app/keys/certs/ca-bundle.pem
COPY keys/certs/ca-cert.pem /app/keys/certs/ca-cert.pem
COPY keys/certs/ca-key.pem /app/keys/certs/ca-key.pem
COPY keys/certs/client-cert.pem /app/keys/certs/client-cert.pem
COPY keys/certs/client-key.pem /app/keys/certs/client-key.pem
COPY keys/certs/server-cert.pem /app/keys/certs/server-cert.pem
COPY keys/certs/server-key.pem /app/keys/certs/server-key.pem

# Create certs directory and set permissions for all certificate files
RUN mkdir -p /app/keys/certs && \
    chmod 644 /app/keys/client-truststore.jks /app/keys/counter-app-keystore-container.jks && \
    chmod 644 /app/keys/certs/*.pem && \
    chmod 600 /app/keys/certs/*-key.pem

# Set environment variables for keystore and truststore
ENV CLIENT_KEY_STORE=/app/keys/counter-app-keystore-container.jks
ENV CLIENT_KEY_STORE_PASSWORD=123456
ENV CLIENT_TRUST_STORE=/app/keys/client-truststore.jks
ENV CLIENT_TRUST_STORE_PASSWORD=123456
ENV GATEWAY_SERVICE_URL=api-gateway-service
ENV KEYCLOAK_GATEWAY_URL=keycloak-service
ENV KEYCLOAK_GATEWAY_PORT=8281
ENV PORT=5001

# Set environment variables for certificate files
ENV CA_BUNDLE_PATH=/app/keys/certs/ca-bundle.pem
ENV CA_CERT_PATH=/app/keys/certs/ca-cert.pem
ENV CA_KEY_PATH=/app/keys/certs/ca-key.pem
ENV CLIENT_CERT_PATH=/app/keys/certs/client-cert.pem
ENV CLIENT_KEY_PATH=/app/keys/certs/client-key.pem
ENV SERVER_CERT_PATH=/app/keys/certs/server-cert.pem
ENV SERVER_KEY_PATH=/app/keys/certs/server-key.pem

# Verify keystore and truststore exist
RUN if [ ! -f "${CLIENT_KEY_STORE}" ]; then \
        echo "counter-app-keystore-container.jks not found at ${CLIENT_KEY_STORE}"; \
        exit 1; \
    fi

RUN if [ ! -f "${CLIENT_TRUST_STORE}" ]; then \
        echo "client-truststore.jks not found at ${CLIENT_TRUST_STORE}"; \
        exit 1; \
    fi

# Verify certificate files exist
RUN if [ ! -f "${CA_BUNDLE_PATH}" ]; then \
        echo "ca-bundle.pem not found at ${CA_BUNDLE_PATH}"; \
        exit 1; \
    fi

RUN if [ ! -f "${CLIENT_CERT_PATH}" ]; then \
        echo "client-cert.pem not found at ${CLIENT_CERT_PATH}"; \
        exit 1; \
    fi

RUN if [ ! -f "${SERVER_CERT_PATH}" ]; then \
        echo "server-cert.pem not found at ${SERVER_CERT_PATH}"; \
        exit 1; \
    fi

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app/counter-app
USER app

# Expose the port the app runs on
EXPOSE 5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/r/counter-app/health || exit 1

# Run the CounterApp application
ENTRYPOINT ["python", "app.py"]
