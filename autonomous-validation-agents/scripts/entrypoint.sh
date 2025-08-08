#!/bin/bash

# Entrypoint script for Orleans container
# Initializes models then starts the Orleans application

set -e

echo "Starting Orleans Model Management Container..."

# Initialize models (real or mock)
/usr/local/bin/init-models.sh

# Start Orleans application
echo "Starting Orleans application..."
exec dotnet AutonomousValidation.Orleans.dll "$@"
