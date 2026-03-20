#!/usr/bin/env bash
set -e

echo "UrbanFlow Pi Provisioning Script"

if [ "$EUID" -ne 0 ]; then
  echo "Please run as root"
  exit 1
fi

apt update && apt upgrade -y
apt install -y git python3.11 python3.11-venv build-essential libgl1 libglib2.0-0 curl wireguard

# Setup User / Group logic
useradd -m -s /bin/bash urbanflow || true

echo "Preparing SATA Mount..."
mkdir -p /mnt/sata/urbanflow
chown urbanflow:urbanflow /mnt/sata/urbanflow

echo "Cloning..."
cd /mnt/sata/urbanflow
git clone https://github.example.com/urbanflow.git . || true
git fetch origin
git checkout ${URBANFLOW_VERSION:-main}  # L2: Pin to known secure commit matching release version
chown -R urbanflow:urbanflow /mnt/sata/urbanflow

echo "Configuring systemd services"
cat > /etc/systemd/system/urbanflow-edge.service << 'EOF'
[Unit]
Description=UrbanFlow Edge Analytics Inference
After=network.target

[Service]
User=urbanflow
WorkingDirectory=/mnt/sata/urbanflow
ExecStart=/mnt/sata/urbanflow/venv/bin/python edge/main.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable urbanflow-edge

echo "Setup completed. Remember to edit .env.edge before starting the service."
