#!/bin/bash
# Generate self-signed TLS certificates for local production test

set -e

CERT_DIR="/Users/lordwilson/SovereignCore/certs"
mkdir -p "$CERT_DIR"

echo "🔐 Generating self-signed TLS certificates..."

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout "$CERT_DIR/key.pem" \
    -out "$CERT_DIR/cert.pem" \
    -subj "/C=US/ST=Sovereignty/L=Silicon/O=SovereignCore/CN=localhost"

chmod 600 "$CERT_DIR/key.pem"
chmod 644 "$CERT_DIR/cert.pem"

echo ""
echo "✅ Certificates generated in $CERT_DIR"
echo "  - cert.pem"
echo "  - key.pem"
echo ""
echo "To enable TLS, update your .env file:"
echo "  TLS_ENABLED=true"
echo "  TLS_CERT_PATH=$CERT_DIR/cert.pem"
echo "  TLS_KEY_PATH=$CERT_DIR/key.pem"
