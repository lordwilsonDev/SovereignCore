#!/bin/bash
# Generate self-signed TLS certificates for development
# For production, use Let's Encrypt or a proper CA

set -e

CERT_DIR="./certs"
mkdir -p "$CERT_DIR"

echo "Generating self-signed TLS certificates..."

# Generate private key
openssl genrsa -out "$CERT_DIR/key.pem" 2048

# Generate certificate signing request
openssl req -new -key "$CERT_DIR/key.pem" -out "$CERT_DIR/csr.pem" \
  -subj "/C=US/ST=State/L=City/O=SovereignCore/CN=localhost"

# Generate self-signed certificate (valid for 365 days)
openssl x509 -req -days 365 -in "$CERT_DIR/csr.pem" \
  -signkey "$CERT_DIR/key.pem" -out "$CERT_DIR/cert.pem"

# Clean up CSR
rm "$CERT_DIR/csr.pem"

echo "✓ Certificates generated in $CERT_DIR/"
echo "  - cert.pem (certificate)"
echo "  - key.pem (private key)"
echo ""
echo "⚠️  These are self-signed certificates for DEVELOPMENT ONLY"
echo "⚠️  For production, use Let's Encrypt or a proper CA"
echo ""
echo "To use with the API server, update .env:"
echo "  TLS_ENABLED=true"
echo "  TLS_CERT_PATH=./certs/cert.pem"
echo "  TLS_KEY_PATH=./certs/key.pem"

chmod 600 "$CERT_DIR/key.pem"
chmod 644 "$CERT_DIR/cert.pem"
