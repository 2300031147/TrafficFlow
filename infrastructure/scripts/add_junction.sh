#!/usr/bin/env bash
set -e

# Typically run from CC Server by Admin
# Usage: ./add_junction.sh [OPTIONAL_VPN_IP]

echo "Generating new UUID and Node configuration..."
JUNCTION_ID=$(cat /proc/sys/kernel/random/uuid)
TOKEN=$(head -c 32 /dev/urandom | base64 | tr -d '+/' | cut -c 1-64)

# SEC-18: VPN IP from arg or placeholder; operator must supply the real subnet-tracked IP
VPN_IP="${1:-10.8.0.MANUAL}"
if [ "$VPN_IP" = "10.8.0.MANUAL" ]; then
    echo "WARNING: VPN IP not supplied. You must assign this from your WireGuard subnet tracker."
fi

CRED_FILE="junction_${JUNCTION_ID}.env"

echo "--- Generated Configuration ---"
echo "JUNCTION_ID: $JUNCTION_ID"
# SEC-12: Do NOT print token to stdout — write to restricted file only
echo "API_TOKEN: [REDACTED — written to ${CRED_FILE} only]"
echo "VPN_IP: $VPN_IP"

# Write credentials to a permission-restricted file
{
    echo "JUNCTION_ID=${JUNCTION_ID}"
    echo "API_TOKEN=${TOKEN}"
    echo "VPN_IP=${VPN_IP}"
} > "${CRED_FILE}"
chmod 600 "${CRED_FILE}"

echo ""
echo "Credentials saved to ${CRED_FILE}"
echo "Copy to the Pi's .env.edge, then DELETE this file."
echo ""

# Would INSERT INTO junctions (id, vpn_ip, api_token_hash, ...) with hashed token here.
echo "Remember to INSERT the junction record into PostgreSQL with the bcrypt-hashed token."
