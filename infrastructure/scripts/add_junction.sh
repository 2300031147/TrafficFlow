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

CITY="${2:-Bengaluru}"
STATE="${3:-Karnataka}"
DISTRICT="${4:-Central}"
JUNCTION_TYPE="${5:-highway}"
NAME="${6:-New Edge Node}"

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

# SEC-12: Insert directly into PostgreSQL database
TOKEN_HASH=$(python3 -c "import bcrypt; print(bcrypt.hashpw(b'${TOKEN}', bcrypt.gensalt()).decode())")
echo "Inserting junction record into PostgreSQL..."
PGPASSWORD=${POSTGRES_PASSWORD:-changeme_dev_only} psql \
  -h localhost -U urban_admin -d urbanflow \
  -c "INSERT INTO junctions (id, vpn_ip, api_token_hash, name, city, district, state, country, junction_type, lat, lng, camera_count, status) VALUES ('$JUNCTION_ID', '$VPN_IP', '$TOKEN_HASH', '$NAME', '$CITY', '$DISTRICT', '$STATE', 'India', '$JUNCTION_TYPE', 12.9716, 77.5946, 4, 'offline');"

