# SolidBeam Solution - ClamAV Web Interface Deployment Guide

## 🚀 Quick Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ available RAM
- 5GB+ available disk space

### 1. Clone and Setup
```bash
# Clone the repository
git clone <repository-url>
cd solidbeam-clamav-web

# Make startup script executable
chmod +x start.sh
```

### 2. Start the Application
```bash
# Start in production mode
./start.sh start

# Or start in development mode
./start.sh start-dev
```

### 3. Access the Web Interface
Open your browser and navigate to: **http://localhost:5000**

## 📋 Detailed Installation

### Manual Docker Compose Deployment
```bash
# Create necessary directories
mkdir -p data quarantine logs

# Build and start the application
docker-compose up -d

# Check status
docker-compose ps
```

### Manual Docker Build
```bash
# Build the image
docker build -t solidbeam-clamav-web .

# Run the container
docker run -d \
  --name solidbeam-clamav-web \
  -p 5000:5000 \
  -v $(pwd)/data:/opt/clamav-web/data \
  -v $(pwd)/quarantine:/opt/clamav-web/quarantine \
  -v $(pwd)/logs:/opt/clamav-web/logs \
  solidbeam-clamav-web
```

## 🔧 Configuration

### Environment Variables
Create a `.env` file for custom configuration:

```bash
# Flask Configuration
FLASK_ENV=production
FLASK_DEBUG=False
CLAMAV_WEB_PORT=5000
CLAMAV_WEB_HOST=0.0.0.0

# ClamAV Configuration
SCAN_TIMEOUT=300
MAX_FILE_SIZE=104857600
QUARANTINE_ENABLED=True

# Database Configuration
CLAMAV_DB_PATH=/opt/clamav-web/data
CLAMAV_QUARANTINE_PATH=/opt/clamav-web/quarantine
CLAMAV_LOGS_PATH=/opt/clamav-web/logs

# Security
SECRET_KEY=your-secret-key-change-in-production
```

### Volume Mounts
The application uses the following volume mounts:

| Host Path | Container Path | Purpose |
|-----------|----------------|---------|
| `./data` | `/opt/clamav-web/data` | SQLite database |
| `./quarantine` | `/opt/clamav-web/quarantine` | Infected files |
| `./logs` | `/opt/clamav-web/logs` | Application logs |
| `clamav_db` | `/var/lib/clamav` | Virus definitions |

## 🛠️ Management Commands

### Using the Startup Script
```bash
# Start the application
./start.sh start

# Start in development mode
./start.sh start-dev

# Stop the application
./start.sh stop

# Restart the application
./start.sh restart

# Check status
./start.sh status

# View logs
./start.sh logs

# Update virus definitions
./start.sh update-db

# Run diagnostics
./start.sh diagnostics

# Create backup
./start.sh backup

# Restore from backup
./start.sh restore backup_20231201_120000
```

### Using Docker Compose
```bash
# Start services
docker-compose up -d

# Stop services
docker-compose down

# View logs
docker-compose logs -f

# Rebuild and start
docker-compose up -d --build

# Scale services (if needed)
docker-compose up -d --scale solidbeam-clamav-web=2
```

## 🔍 Monitoring and Health Checks

### Health Check Endpoint
```bash
# Check application health
curl http://localhost:5000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2023-12-01T12:00:00",
  "version": "1.0.0"
}
```

### System Diagnostics
```bash
# Run comprehensive diagnostics
curl http://localhost:5000/api/diagnostics

# Check system metrics
curl http://localhost:5000/api/metrics
```

### Container Health
```bash
# Check container status
docker ps --filter "name=solidbeam-clamav-web"

# View container logs
docker logs solidbeam-clamav-web

# Execute commands in container
docker exec -it solidbeam-clamav-web bash
```

## 🔒 Security Considerations

### Network Security
- The application runs on port 5000 by default
- Consider using a reverse proxy (nginx, Traefik) for production
- Enable SSL/TLS for secure communication

### File Permissions
```bash
# Set proper permissions for data directories
chmod 755 data quarantine logs
chown -R 1000:1000 data quarantine logs
```

### Container Security
- The application runs as non-root user (clamav)
- Resource limits are configured in docker-compose.yml
- Health checks monitor application status

## 📊 Performance Tuning

### Resource Limits
Adjust resource limits in `docker-compose.yml`:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

### ClamAV Optimization
```bash
# Update virus definitions
docker exec solidbeam-clamav-web freshclam

# Check ClamAV configuration
docker exec solidbeam-clamav-web cat /etc/clamav/clamd.conf
```

### Database Optimization
```bash
# Optimize SQLite database
docker exec solidbeam-clamav-web sqlite3 /opt/clamav-web/data/clamav_web.db "VACUUM;"
```

## 🚨 Troubleshooting

### Common Issues

#### 1. Container Won't Start
```bash
# Check logs
docker logs solidbeam-clamav-web

# Check port availability
netstat -tulpn | grep 5000

# Verify Docker daemon
docker info
```

#### 2. ClamAV Issues
```bash
# Check ClamAV installation
docker exec solidbeam-clamav-web clamscan --version

# Update virus definitions
docker exec solidbeam-clamav-web freshclam

# Check ClamAV logs
docker exec solidbeam-clamav-web tail -f /var/log/clamav/clamav.log
```

#### 3. Permission Issues
```bash
# Fix volume permissions
sudo chown -R 1000:1000 data quarantine logs

# Check file permissions
ls -la data quarantine logs
```

#### 4. Database Issues
```bash
# Check database file
docker exec solidbeam-clamav-web ls -la /opt/clamav-web/data/

# Reinitialize database
docker exec solidbeam-clamav-web python init_db.py
```

### Log Analysis
```bash
# View application logs
docker logs solidbeam-clamav-web

# View specific log files
docker exec solidbeam-clamav-web tail -f /opt/clamav-web/logs/clamav_web.log

# Check system logs
docker exec solidbeam-clamav-web journalctl -u clamav-daemon
```

## 🔄 Backup and Recovery

### Automated Backup
```bash
# Create backup
./start.sh backup

# Restore from backup
./start.sh restore backup_20231201_120000
```

### Manual Backup
```bash
# Backup data directory
tar czf backup_data_$(date +%Y%m%d_%H%M%S).tar.gz data/

# Backup quarantine
tar czf backup_quarantine_$(date +%Y%m%d_%H%M%S).tar.gz quarantine/

# Backup virus definitions
docker exec solidbeam-clamav-web tar czf - /var/lib/clamav > backup_clamav_$(date +%Y%m%d_%H%M%S).tar.gz
```

### Recovery Procedure
```bash
# Stop the application
./start.sh stop

# Restore data
tar xzf backup_data_YYYYMMDD_HHMMSS.tar.gz
tar xzf backup_quarantine_YYYYMMDD_HHMMSS.tar.gz

# Restore virus definitions
docker exec solidbeam-clamav-web tar xzf - < backup_clamav_YYYYMMDD_HHMMSS.tar.gz

# Start the application
./start.sh start
```

## 🔧 Development Setup

### Development Mode
```bash
# Start in development mode
./start.sh start-dev

# Features enabled in development:
# - Auto-reload on code changes
# - Debug mode
# - Volume mounts for live development
```

### Code Changes
```bash
# The application will auto-reload when you modify:
# - app.py
# - templates/
# - static/
```

### Testing
```bash
# Test file upload
curl -X POST -F "file=@test_scan.txt" http://localhost:5000/api/scan/upload

# Test quick scan
curl -X POST http://localhost:5000/api/scan/quick

# Test custom scan
curl -X POST -H "Content-Type: application/json" \
  -d '{"path":"/tmp","recursive":true}' \
  http://localhost:5000/api/scan/custom
```

## 📈 Scaling and Production

### Load Balancing
```yaml
# docker-compose.prod.yml
version: '3.8'
services:
  solidbeam-clamav-web:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 1G
```

### Reverse Proxy Setup
```nginx
# nginx.conf
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### SSL/TLS Configuration
```bash
# Generate SSL certificate
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout private.key -out certificate.crt

# Update docker-compose.yml
environment:
  - SSL_ENABLED=True
  - SSL_CERT_FILE=/path/to/certificate.crt
  - SSL_KEY_FILE=/path/to/private.key
```

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review application logs
3. Run diagnostics: `./start.sh diagnostics`
4. Check the README.md for detailed documentation

---

**SolidBeam Solution** - Enterprise-grade ClamAV Web Interface