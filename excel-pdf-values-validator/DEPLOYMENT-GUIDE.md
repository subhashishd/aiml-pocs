# Excel-PDF-Validator Deployment Guide
## Oracle VM + Azure DevOps + Kong Gateway Setup (Demo/Pilot)

This guide provides step-by-step instructions for deploying the Excel-PDF-Validator application on Oracle VM with Kong Gateway authentication and Azure DevOps CI/CD.

---

## 🚀 Quick Start Summary

**What we're building:**
- **CI**: Azure DevOps builds & tests on GitHub webhook
- **Registry**: Docker Hub (free 2GB)
- **CD**: Deploy to Oracle VM via self-hosted agent
- **Security**: Kong Gateway with Google OAuth + email whitelist
- **Monitoring**: Basic rate limiting + health checks

---

## 📋 Prerequisites

### Required Accounts & Services
1. **Azure DevOps** account (free)
2. **Docker Hub** account (free tier: 2GB storage)
3. **Google Cloud Console** account (for OAuth setup)
4. **Oracle VM** instance (free tier available)
5. **GitHub** repository (already exists)

### Required Information
- Oracle VM IP address
- Google OAuth Client ID & Secret
- List of allowed email addresses
- Docker Hub username

---

## 🏗️ Part 1: Oracle VM Setup

### 1.1 Provision Oracle VM

1. **Create Oracle Cloud Free Account**
   - Go to [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
   - Sign up for free account (includes Always Free resources)

2. **Launch VM Instance**
   ```bash
   # Recommended specs for demo/pilot:
   # - Shape: VM.Standard.E2.1.Micro (Always Free)
   # - Image: Ubuntu 22.04 LTS
   # - Memory: 1GB RAM (Always Free)
   # - Storage: 47GB (Always Free)
   ```

3. **Configure Security Rules**
   ```bash
   # Open required ports in Oracle Cloud Security List:
   Port 22   (SSH)
   Port 80   (HTTP - Kong Gateway)
   Port 443  (HTTPS - future use)
   Port 8001 (Kong Admin - restrict to your IP)
   ```

### 1.2 VM Initial Setup

```bash
# Connect to your VM
ssh -i your-key.pem ubuntu@YOUR_VM_IP

# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker ubuntu

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.21.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install additional tools
sudo apt install -y jq curl git htop

# Verify installations
docker --version
docker-compose --version

# Log out and back in for docker group changes
exit
ssh -i your-key.pem ubuntu@YOUR_VM_IP
```

### 1.3 Configure VM for Azure DevOps

```bash
# Create application directory
sudo mkdir -p /opt/excel-pdf-validator
sudo chown -R ubuntu:ubuntu /opt/excel-pdf-validator

# Create Docker network for Kong integration
docker network create app-net

# Configure firewall (Ubuntu UFW)
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8001/tcp  # Kong admin (restrict this in production)

# Test Docker installation
docker run hello-world
```

---

## 🔐 Part 2: Google OAuth Setup

### 2.1 Create Google OAuth Application

1. **Go to Google Cloud Console**
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create new project or select existing one

2. **Enable Google+ API**
   ```bash
   # Navigate to: APIs & Services > Library
   # Search for: Google+ API
   # Click: Enable
   ```

3. **Create OAuth 2.0 Credentials**
   ```bash
   # Navigate to: APIs & Services > Credentials
   # Click: Create Credentials > OAuth 2.0 Client IDs
   # Application Type: Web application
   # Name: excel-pdf-validator
   
   # Authorized redirect URIs:
   http://YOUR_VM_IP/app/auth/callback
   https://YOUR_VM_IP/app/auth/callback  # for future HTTPS
   ```

4. **Note Your Credentials**
   ```bash
   # Save these values securely:
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   ```

### 2.2 Configure Email Whitelist

```bash
# Prepare your allowed emails list (comma-separated)
ALLOWED_EMAILS=user1@company.com,user2@company.com,admin@company.com

# For demo/pilot, you can start with just your email
ALLOWED_EMAILS=your-email@gmail.com
```

---

## 🔧 Part 3: Azure DevOps Setup

### 3.1 Create Azure DevOps Project

1. **Create Organization & Project**
   - Go to [Azure DevOps](https://dev.azure.com/)
   - Create new organization (if needed)
   - Create new project: "excel-pdf-validator"

2. **Connect to GitHub**
   ```bash
   # In Azure DevOps:
   # Project Settings > Service connections > New service connection
   # Choose: GitHub
   # Authorize: Your GitHub account
   # Connection name: GitHub-Connection
   ```

### 3.2 Create Service Connections

1. **Docker Hub Connection**
   ```bash
   # Project Settings > Service connections > New service connection
   # Choose: Docker Registry
   # Registry type: Docker Hub
   # Docker ID: your-dockerhub-username
   # Password: your-dockerhub-password
   # Connection name: DockerHub-Connection
   ```

2. **Oracle VM Connection**
   ```bash
   # We'll use self-hosted agent (next section)
   # No separate connection needed
   ```

### 3.3 Setup Self-Hosted Agent on Oracle VM

```bash
# On your Oracle VM, run:

# Download Azure DevOps agent
cd /home/ubuntu
mkdir azagent && cd azagent
wget https://vstsagentpackage.azureedge.net/agent/3.232.0/vsts-agent-linux-x64-3.232.0.tar.gz
tar zxvf vsts-agent-linux-x64-3.232.0.tar.gz

# Configure agent (follow prompts)
./config.sh

# Example configuration:
# Server URL: https://dev.azure.com/your-organization
# Authentication: PAT (Personal Access Token)
# Agent pool: Default
# Agent name: OracleVM-Agent
# Work folder: _work

# Install as service
sudo ./svc.sh install ubuntu
sudo ./svc.sh start

# Verify agent is online in Azure DevOps:
# Organization Settings > Agent pools > Default > Agents
```

### 3.4 Create Variable Groups

```bash
# In Azure DevOps:
# Pipelines > Library > Variable groups

# Create group: "Excel-PDF-Secrets" (mark as secret)
DOCKER_HUB_USERNAME=your-dockerhub-username
DOCKER_HUB_PASSWORD=your-dockerhub-password (mark as secret)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret (mark as secret)
POSTGRES_PASSWORD=secure-db-password (mark as secret)
KONG_DB_PASSWORD=secure-kong-db-password (mark as secret)
JWT_SECRET_KEY=your-jwt-secret-key (mark as secret)
SESSION_SECRET=your-session-secret (mark as secret)
REDIS_PASSWORD=your-redis-password (mark as secret)

# Create group: "Excel-PDF-Config" (plain text)
ORACLE_VM_IP=your-vm-ip-address
ALLOWED_EMAILS=email1@domain.com,email2@domain.com
```

---

## 🚢 Part 4: Deploy Pipeline

### 4.1 Create Pipeline

1. **Create Pipeline in Azure DevOps**
   ```bash
   # Pipelines > Create Pipeline
   # Choose: GitHub
   # Select: your repository
   # Configure: Existing Azure Pipelines YAML file
   # Path: /.azure/pipelines/ci-cd-pipeline.yml
   ```

2. **Create Environment**
   ```bash
   # Pipelines > Environments
   # New environment: "OracleVM-Production"
   # Resource type: Virtual machines
   # Add resource: Select your self-hosted agent
   ```

### 4.2 Test Pipeline

1. **Trigger First Build**
   ```bash
   # Make a small change to trigger pipeline
   echo "Demo deployment ready" >> README.md
   git add README.md
   git commit -m "Trigger initial deployment"
   git push origin main
   ```

2. **Monitor Pipeline**
   ```bash
   # In Azure DevOps:
   # Pipelines > Runs
   # Watch the build progress
   ```

---

## 🔍 Part 5: Verification & Testing

### 5.1 Verify Deployment

```bash
# On Oracle VM, check running services:
cd /opt/excel-pdf-validator
docker-compose ps

# Check logs if needed:
docker-compose logs backend
docker-compose logs frontend
docker-compose -f docker-compose.kong.yml logs kong
```

### 5.2 Test Application

1. **Test Public Endpoints**
   ```bash
   curl http://YOUR_VM_IP/
   curl http://YOUR_VM_IP/health
   curl http://YOUR_VM_IP/docs
   ```

2. **Test Authentication**
   ```bash
   # Visit in browser:
   http://YOUR_VM_IP/app/
   
   # Should redirect to Google OAuth
   # After auth, should access application
   ```

3. **Test Rate Limiting**
   ```bash
   # Make rapid requests to test rate limiting:
   for i in {1..150}; do curl http://YOUR_VM_IP/health; done
   
   # Should see 429 (Too Many Requests) after 100 requests/minute
   ```

### 5.3 Monitor Services

```bash
# Kong Admin API (restrict access in production)
curl http://YOUR_VM_IP:8001/status
curl http://YOUR_VM_IP:8001/services
curl http://YOUR_VM_IP:8001/routes

# Application logs
tail -f /opt/excel-pdf-validator/logs/deployments.log
```

---

## 🛠️ Part 6: Maintenance & Troubleshooting

### 6.1 Common Commands

```bash
# Restart services
cd /opt/excel-pdf-validator
docker-compose restart

# Update images
docker-compose pull
docker-compose up -d

# Check resource usage
docker stats

# Clean up old images
docker system prune -f
```

### 6.2 Troubleshooting

**Issue: Kong not starting**
```bash
# Check Kong logs
docker-compose -f docker-compose.kong.yml logs kong

# Verify database connection
docker-compose -f docker-compose.kong.yml exec kong-database pg_isready -U kong
```

**Issue: OAuth not working**
```bash
# Verify environment variables
docker-compose exec backend env | grep GOOGLE

# Check Kong OIDC plugin
curl http://localhost:8001/routes/protected-app/plugins
```

**Issue: Services not accessible**
```bash
# Check firewall
sudo ufw status

# Check Docker networks
docker network ls
docker network inspect app-net
```

### 6.3 Security Hardening (Future)

```bash
# For production deployment:

# 1. Enable HTTPS with Let's Encrypt
# 2. Restrict Kong Admin API access
# 3. Use stronger rate limiting
# 4. Enable IP whitelisting
# 5. Configure proper logging and monitoring
# 6. Setup automated backups
# 7. Enable Docker security scanning
```

---

## 📊 Part 7: Monitoring & Metrics

### 7.1 Basic Monitoring

```bash
# Kong metrics endpoint
curl http://YOUR_VM_IP:8001/metrics

# Application health
curl http://YOUR_VM_IP/health

# Resource monitoring
htop
docker stats
```

### 7.2 Log Locations

```bash
# Application logs
/opt/excel-pdf-validator/logs/

# Docker logs
docker logs excel-pdf-backend
docker logs excel-pdf-frontend
docker logs kong-gateway

# System logs
/var/log/syslog
journalctl -u docker
```

---

## 🎯 Success Criteria

Your deployment is successful when:

✅ Pipeline builds and deploys automatically on GitHub push  
✅ Public endpoints respond without authentication  
✅ Protected endpoints redirect to Google OAuth  
✅ Authenticated users can access the application  
✅ Rate limiting blocks excessive requests  
✅ File uploads work within 50MB limit  
✅ Health checks pass consistently  

---

## 📞 Support & Next Steps

### For Demo/Pilot Phase:
- Monitor application usage and performance
- Collect user feedback
- Document any issues or improvements needed
- Plan for production hardening

### For Production Phase:
- Implement HTTPS/SSL certificates
- Setup proper monitoring and alerting
- Configure automated backups
- Implement log aggregation
- Setup disaster recovery procedures
- Review and harden security configurations

---

## 🔗 Useful Links

- [Kong Documentation](https://docs.konghq.com/)
- [Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)
- [Docker Hub](https://hub.docker.com/)
- [Oracle Cloud Free Tier](https://www.oracle.com/cloud/free/)
- [Google OAuth Setup](https://developers.google.com/identity/protocols/oauth2)

---

**🎉 Congratulations! Your Excel-PDF-Validator is now deployed and secured for demo/pilot use.**
