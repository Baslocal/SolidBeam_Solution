# SolidBeam Solution - ClamAV Web Interface

A modern, Docker-based web interface for ClamAV antivirus scanning with enterprise-grade features.

## 🚀 Quick Start

```bash
# Clone and run
git clone <repository>
cd solidbeam-clamav-web
docker-compose up -d

# Access the web interface
open http://localhost:5000
```

## 🏗️ Architecture

- **Frontend**: HTML5/JavaScript with responsive design
- **Backend**: Python Flask API server
- **Scanner**: ClamAV (clamscan) antivirus engine
- **Storage**: SQLite for persistent scan history
- **Container**: Docker with multi-stage build
- **Orchestration**: Docker Compose for easy deployment

## 🔧 Features

### 🔍 Scanning Capabilities
- **Quick Scan**: Common system paths
- **Custom Scan**: User-defined paths with recursion
- **Upload Scan**: Instant file upload and scanning
- **Real-time Output**: Live scan progress streaming
- **Result Parsing**: Visual infected/safe indicators

### 📦 Quarantine System
- **Automatic Isolation**: Secure infected file storage
- **Metadata Tracking**: Complete audit trail
- **Safe Delete**: One-click removal
- **Audit Trail**: All quarantine actions logged

### 📊 System Monitoring
- **Live Metrics**: CPU, RAM, Disk usage
- **Uptime Stats**: System health monitoring
- **Auto-refresh**: Real-time dashboard updates

### 🧪 Diagnostics Suite
- **Comprehensive Tests**: All subsystem validation
- **Modular Execution**: Targeted testing
- **Plaintext Output**: Detailed diagnostic logs

## 🐳 Docker Deployment

### Prerequisites
- Docker Engine 20.10+
- Docker Compose 2.0+
- 2GB+ available RAM
- 5GB+ available disk space

### Environment Variables
```bash
# Optional: Customize these in docker-compose.yml
CLAMAV_WEB_PORT=5000
CLAMAV_WEB_HOST=0.0.0.0
CLAMAV_DB_PATH=/opt/clamav-web/data
CLAMAV_QUARANTINE_PATH=/opt/clamav-web/quarantine
```

### Volume Mounts
- `/var/lib/clamav`: Virus signature database
- `/opt/clamav-web/data`: SQLite database
- `/opt/clamav-web/logs`: Application logs
- `/opt/clamav-web/quarantine`: Infected files
- `/tmp`: Upload area

## 🔒 Security Features

- **Container Isolation**: Sandboxed execution environment
- **File Permissions**: Secure volume mounting
- **Network Security**: Internal container networking
- **Resource Limits**: CPU and memory constraints
- **Health Monitoring**: Built-in health checks

## 📈 Performance

- **Lightweight**: ~200MB base image
- **Fast Startup**: <30 seconds to ready state
- **Efficient Scanning**: Optimized ClamAV configuration
- **Resource Aware**: Configurable limits

## 🛠️ Development

### Local Development
```bash
# Build and run locally
docker build -t solidbeam-clamav-web .
docker run -p 5000:5000 solidbeam-clamav-web

# Development with volumes
docker-compose -f docker-compose.dev.yml up
```

### Testing
```bash
# Run diagnostics
curl http://localhost:5000/api/diagnostics

# Health check
curl http://localhost:5000/health
```

## 📋 API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /api/scan/quick` - Quick system scan
- `POST /api/scan/custom` - Custom path scan
- `POST /api/scan/upload` - File upload scan
- `GET /api/history` - Scan history
- `GET /api/metrics` - System metrics
- `GET /api/diagnostics` - System diagnostics
- `GET /api/quarantine` - Quarantine list
- `DELETE /api/quarantine/<id>` - Remove from quarantine

## 🔧 Configuration

### ClamAV Settings
```bash
# Custom ClamAV configuration
docker exec -it solidbeam-clamav-web vi /etc/clamav/clamd.conf

# Update virus definitions
docker exec -it solidbeam-clamav-web freshclam
```

### Application Settings
```python
# config.py - Application configuration
SCAN_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
QUARANTINE_ENABLED = True
LOG_LEVEL = 'INFO'
```

## 📊 Monitoring

### Health Checks
```bash
# Container health
docker ps

# Application health
curl http://localhost:5000/health

# Detailed diagnostics
curl http://localhost:5000/api/diagnostics
```

### Logs
```bash
# Application logs
docker logs solidbeam-clamav-web

# Real-time logs
docker logs -f solidbeam-clamav-web
```

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   # Check logs
   docker logs solidbeam-clamav-web
   
   # Verify ports
   netstat -tulpn | grep 5000
   ```

2. **Scan failures**
   ```bash
   # Check ClamAV status
   docker exec solidbeam-clamav-web clamscan --version
   
   # Update virus definitions
   docker exec solidbeam-clamav-web freshclam
   ```

3. **Permission issues**
   ```bash
   # Fix volume permissions
   sudo chown -R 1000:1000 ./data ./quarantine
   ```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📞 Support

For support and questions:
- Create an issue in the repository
- Check the troubleshooting section
- Review the API documentation

---

**SolidBeam Solution** - Enterprise-grade ClamAV Web Interface