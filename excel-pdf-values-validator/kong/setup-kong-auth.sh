#!/bin/bash
# Kong Authentication Setup Script for Excel-PDF-Validator Demo/Pilot
# Simple setup focused on Google OAuth + Rate Limiting

set -e

KONG_ADMIN_URL="http://localhost:8001"
echo "🔧 Setting up Kong Authentication for Demo/Pilot..."

# Wait for Kong to be ready
echo "⏳ Waiting for Kong Admin API..."
timeout 60 bash -c 'until curl -f $KONG_ADMIN_URL/status > /dev/null 2>&1; do sleep 2; done'

# Install OIDC plugin (lua-resty-openidc)
echo "📦 Installing OIDC plugin..."
docker-compose -f docker-compose.kong.yml exec -T kong sh -c "
  apk add --no-cache git
  luarocks install lua-resty-openidc
  luarocks install lua-cjson
"

# Restart Kong to load plugins
echo "🔄 Restarting Kong to load plugins..."
docker-compose -f docker-compose.kong.yml restart kong

# Wait for Kong to restart
echo "⏳ Waiting for Kong to restart..."
sleep 30
timeout 60 bash -c 'until curl -f $KONG_ADMIN_URL/status > /dev/null 2>&1; do sleep 2; done'

# Create Services
echo "🌐 Creating Kong services..."

# Main Application Service
curl -i -X POST $KONG_ADMIN_URL/services \
  --data name=excel-pdf-app \
  --data url=http://nginx:8080

# Backend API Service  
curl -i -X POST $KONG_ADMIN_URL/services \
  --data name=excel-pdf-api \
  --data url=http://backend:8000

# Create Routes
echo "🛣️  Creating Kong routes..."

# Public routes (no auth)
curl -i -X POST $KONG_ADMIN_URL/services/excel-pdf-api/routes \
  --data name=public-health \
  --data 'paths[]=/health' \
  --data 'paths[]=/docs' \
  --data 'paths[]=/openapi.json' \
  --data strip_path=false

curl -i -X POST $KONG_ADMIN_URL/services/excel-pdf-app/routes \
  --data name=public-landing \
  --data 'paths[]=/' \
  --data 'methods[]=GET' \
  --data strip_path=false

# Protected routes (requires auth)
curl -i -X POST $KONG_ADMIN_URL/services/excel-pdf-app/routes \
  --data name=protected-app \
  --data 'paths[]=/app' \
  --data strip_path=false

curl -i -X POST $KONG_ADMIN_URL/services/excel-pdf-api/routes \
  --data name=protected-api \
  --data 'paths[]=/api' \
  --data 'paths[]=/upload' \
  --data 'paths[]=/validate' \
  --data 'paths[]=/results' \
  --data strip_path=false

# Configure Global Rate Limiting
echo "⚡ Setting up rate limiting..."
curl -i -X POST $KONG_ADMIN_URL/plugins \
  --data name=rate-limiting \
  --data config.minute=100 \
  --data config.hour=1000 \
  --data config.day=10000 \
  --data config.policy=local

# Configure CORS
echo "🌐 Setting up CORS..."
curl -i -X POST $KONG_ADMIN_URL/plugins \
  --data name=cors \
  --data config.origins=http://${ORACLE_VM_IP} \
  --data config.origins=https://${ORACLE_VM_IP} \
  --data config.methods=GET \
  --data config.methods=POST \
  --data config.methods=PUT \
  --data config.methods=DELETE \
  --data config.methods=OPTIONS \
  --data config.credentials=true \
  --data config.max_age=3600

# Setup Google OAuth for protected routes
echo "🔐 Setting up Google OAuth..."

# Get route IDs for OAuth setup
APP_ROUTE_ID=$(curl -s $KONG_ADMIN_URL/routes/protected-app | jq -r '.id')
API_ROUTE_ID=$(curl -s $KONG_ADMIN_URL/routes/protected-api | jq -r '.id')

# OAuth for app routes
curl -i -X POST $KONG_ADMIN_URL/routes/$APP_ROUTE_ID/plugins \
  --data name=oidc \
  --data config.client_id=${GOOGLE_CLIENT_ID} \
  --data config.client_secret=${GOOGLE_CLIENT_SECRET} \
  --data config.discovery=https://accounts.google.com/.well-known/openid_configuration \
  --data config.scope=openid email profile \
  --data config.redirect_uri=http://${ORACLE_VM_IP}/app/auth/callback \
  --data config.logout_path=/logout \
  --data config.realm=excel-pdf-validator \
  --data config.session_secret=${SESSION_SECRET}

# OAuth for API routes  
curl -i -X POST $KONG_ADMIN_URL/routes/$API_ROUTE_ID/plugins \
  --data name=oidc \
  --data config.client_id=${GOOGLE_CLIENT_ID} \
  --data config.client_secret=${GOOGLE_CLIENT_SECRET} \
  --data config.discovery=https://accounts.google.com/.well-known/openid_configuration \
  --data config.scope=openid email profile \
  --data config.redirect_uri=http://${ORACLE_VM_IP}/app/auth/callback \
  --data config.logout_path=/logout \
  --data config.realm=excel-pdf-validator \
  --data config.session_secret=${SESSION_SECRET}

# Setup request size limiting for uploads
echo "📁 Setting up upload size limits..."
curl -i -X POST $KONG_ADMIN_URL/routes/$API_ROUTE_ID/plugins \
  --data name=request-size-limiting \
  --data config.allowed_payload_size=52428800

# Enable monitoring (optional for demo)
echo "📊 Setting up basic monitoring..."
curl -i -X POST $KONG_ADMIN_URL/plugins \
  --data name=prometheus \
  --data config.per_consumer=false

echo "✅ Kong Authentication setup completed!"
echo ""
echo "📋 Configuration Summary:"
echo "========================"
echo "🌐 Public URLs:"
echo "   - Landing: http://${ORACLE_VM_IP}/"
echo "   - Health: http://${ORACLE_VM_IP}/health"
echo "   - API Docs: http://${ORACLE_VM_IP}/docs"
echo ""
echo "🔐 Protected URLs (requires Google OAuth):"
echo "   - Application: http://${ORACLE_VM_IP}/app/"
echo "   - API Endpoints: http://${ORACLE_VM_IP}/api/*"
echo ""
echo "⚡ Rate Limits:"
echo "   - 100 requests/minute"
echo "   - 1000 requests/hour"  
echo "   - 10000 requests/day"
echo ""
echo "📁 Upload Limit: 50MB"
echo "🔧 Kong Admin: http://${ORACLE_VM_IP}:8001"
echo "========================"
