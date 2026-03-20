#!/usr/bin/env bash
set -e

echo "UrbanFlow Developer Setup Initializing..."

# Check requirements
command -v python3.11 >/dev/null 2>&1 || { echo >&2 "Python 3.11 required but not installed. Aborting."; exit 1; }
command -v docker >/dev/null 2>&1 || { echo >&2 "Docker required but not installed. Aborting."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo >&2 "npm required but not installed. Aborting."; exit 1; }

echo "Installing Edge virtual environment..."
python3.11 -m venv venv_edge
source venv_edge/bin/activate
pip install -r requirements-server.txt
deactivate

echo "Starting Docker Compose services (Postgres + Redis)..."
docker-compose up -d

echo "Waiting for PostgreSQL to be ready..."
sleep 5

echo "Applying Schema..."
cat server/db/schema.sql | docker exec -i urbanflow-db psql -U urban_admin -d urbanflow

echo "Installing Dashboard dependencies..."
cd dashboard
npm install
cd ..

echo "Setup complete! Read the architecture notes to start the dev server components."
