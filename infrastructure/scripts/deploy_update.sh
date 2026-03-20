#!/usr/bin/env bash
set -e

# SEC-16: validate hostname argument before using it in SSH
PI_HOST="${1:-}"
if [ -z "$PI_HOST" ]; then
    echo "Usage: ./deploy_update.sh <pi_hostname_or_ip>"
    exit 1
fi

# Only allow alphanumeric, dots, dashes, underscores — block shell metacharacters
if [[ ! "$PI_HOST" =~ ^[0-9a-zA-Z._-]+$ ]]; then
    echo "ERROR: Invalid hostname '${PI_HOST}' — must match [0-9a-zA-Z._-]+"
    exit 1
fi

echo "Pushing latest git changes to ${PI_HOST}..."
ssh urbanflow@"$PI_HOST" 'cd /mnt/sata/urbanflow && git pull origin main && sudo systemctl restart urbanflow-edge'
echo "Update complete on Pi ${PI_HOST}"
