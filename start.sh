#!/bin/bash
# SolidBeam Solution - ClamAV Web Interface Startup Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="SolidBeam Solution - ClamAV Web Interface"
CONTAINER_NAME="solidbeam-clamav-web"
COMPOSE_FILE="docker-compose.yml"
DEV_COMPOSE_FILE="docker-compose.dev.yml"

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to check if Docker Compose is available
check_docker_compose() {
    if ! command -v docker-compose > /dev/null 2>&1; then
        print_error "Docker Compose is not installed. Please install Docker Compose and try again."
        exit 1
    fi
    print_success "Docker Compose is available"
}

# Function to create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p data
    mkdir -p quarantine
    mkdir -p logs
    
    # Set proper permissions
    chmod 755 data quarantine logs
    
    print_success "Directories created successfully"
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check available memory (minimum 1GB)
    local mem_available=$(free -m | awk 'NR==2{printf "%.0f", $7}')
    if [ "$mem_available" -lt 1024 ]; then
        print_warning "Available memory is less than 1GB (${mem_available}MB). Performance may be affected."
    else
        print_success "Memory requirement met (${mem_available}MB available)"
    fi
    
    # Check available disk space (minimum 5GB)
    local disk_available=$(df -BG . | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$disk_available" -lt 5 ]; then
        print_warning "Available disk space is less than 5GB (${disk_available}GB). Consider freeing up space."
    else
        print_success "Disk space requirement met (${disk_available}GB available)"
    fi
    
    # Check if port 5000 is available
    if netstat -tuln | grep -q ":5000 "; then
        print_warning "Port 5000 is already in use. The application may not start properly."
    else
        print_success "Port 5000 is available"
    fi
}

# Function to build the application
build_app() {
    print_status "Building $APP_NAME..."
    
    if docker-compose -f "$COMPOSE_FILE" build; then
        print_success "Application built successfully"
    else
        print_error "Failed to build application"
        exit 1
    fi
}

# Function to start the application
start_app() {
    print_status "Starting $APP_NAME..."
    
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        print_success "Application started successfully"
        print_status "The web interface will be available at: http://localhost:5000"
        print_status "Health check endpoint: http://localhost:5000/health"
    else
        print_error "Failed to start application"
        exit 1
    fi
}

# Function to start the application in development mode
start_dev() {
    print_status "Starting $APP_NAME in development mode..."
    
    if docker-compose -f "$DEV_COMPOSE_FILE" up -d; then
        print_success "Application started in development mode"
        print_status "The web interface will be available at: http://localhost:5000"
        print_status "Development mode features:"
        print_status "  - Auto-reload on code changes"
        print_status "  - Debug mode enabled"
        print_status "  - Volume mounts for live development"
    else
        print_error "Failed to start application in development mode"
        exit 1
    fi
}

# Function to stop the application
stop_app() {
    print_status "Stopping $APP_NAME..."
    
    if docker-compose -f "$COMPOSE_FILE" down; then
        print_success "Application stopped successfully"
    else
        print_error "Failed to stop application"
        exit 1
    fi
}

# Function to restart the application
restart_app() {
    print_status "Restarting $APP_NAME..."
    stop_app
    sleep 2
    start_app
}

# Function to show application status
show_status() {
    print_status "Checking application status..."
    
    if docker ps | grep -q "$CONTAINER_NAME"; then
        print_success "Application is running"
        
        # Show container details
        echo ""
        docker ps --filter "name=$CONTAINER_NAME" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Show health status
        echo ""
        print_status "Health check:"
        if curl -s http://localhost:5000/health > /dev/null; then
            print_success "Web interface is responding"
        else
            print_warning "Web interface is not responding"
        fi
    else
        print_warning "Application is not running"
    fi
}

# Function to show logs
show_logs() {
    print_status "Showing application logs..."
    docker-compose -f "$COMPOSE_FILE" logs -f
}

# Function to update virus definitions
update_virus_db() {
    print_status "Updating virus definitions..."
    
    if docker exec "$CONTAINER_NAME" freshclam; then
        print_success "Virus definitions updated successfully"
    else
        print_error "Failed to update virus definitions"
        exit 1
    fi
}

# Function to run diagnostics
run_diagnostics() {
    print_status "Running system diagnostics..."
    
    if curl -s http://localhost:5000/api/diagnostics > /dev/null; then
        print_success "Diagnostics endpoint is accessible"
        echo ""
        print_status "Diagnostic results:"
        curl -s http://localhost:5000/api/diagnostics | jq '.' 2>/dev/null || curl -s http://localhost:5000/api/diagnostics
    else
        print_error "Diagnostics endpoint is not accessible"
    fi
}

# Function to backup data
backup_data() {
    local backup_dir="backup_$(date +%Y%m%d_%H%M%S)"
    print_status "Creating backup in $backup_dir..."
    
    mkdir -p "$backup_dir"
    
    if docker-compose -f "$COMPOSE_FILE" exec -T solidbeam-clamav-web tar czf - /opt/clamav-web/data > "$backup_dir/data.tar.gz"; then
        print_success "Data backup created successfully"
    else
        print_error "Failed to create data backup"
    fi
    
    if [ -d "quarantine" ] && [ "$(ls -A quarantine)" ]; then
        tar czf "$backup_dir/quarantine.tar.gz" quarantine
        print_success "Quarantine backup created successfully"
    fi
    
    print_success "Backup completed: $backup_dir"
}

# Function to restore data
restore_data() {
    local backup_dir="$1"
    
    if [ -z "$backup_dir" ]; then
        print_error "Please specify a backup directory"
        exit 1
    fi
    
    if [ ! -d "$backup_dir" ]; then
        print_error "Backup directory $backup_dir does not exist"
        exit 1
    fi
    
    print_status "Restoring data from $backup_dir..."
    
    if [ -f "$backup_dir/data.tar.gz" ]; then
        docker-compose -f "$COMPOSE_FILE" exec -T solidbeam-clamav-web tar xzf - < "$backup_dir/data.tar.gz"
        print_success "Data restored successfully"
    else
        print_warning "No data backup found in $backup_dir"
    fi
    
    if [ -f "$backup_dir/quarantine.tar.gz" ]; then
        tar xzf "$backup_dir/quarantine.tar.gz"
        print_success "Quarantine restored successfully"
    else
        print_warning "No quarantine backup found in $backup_dir"
    fi
}

# Function to show help
show_help() {
    echo "SolidBeam Solution - ClamAV Web Interface Management Script"
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  start       Start the application"
    echo "  start-dev   Start the application in development mode"
    echo "  stop        Stop the application"
    echo "  restart     Restart the application"
    echo "  status      Show application status"
    echo "  logs        Show application logs"
    echo "  build       Build the application"
    echo "  update-db   Update virus definitions"
    echo "  diagnostics Run system diagnostics"
    echo "  backup      Create a backup of data"
    echo "  restore     Restore data from backup"
    echo "  help        Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 start"
    echo "  $0 start-dev"
    echo "  $0 status"
    echo "  $0 backup"
    echo "  $0 restore backup_20231201_120000"
}

# Main script logic
case "${1:-}" in
    start)
        check_docker
        check_docker_compose
        check_requirements
        create_directories
        build_app
        start_app
        ;;
    start-dev)
        check_docker
        check_docker_compose
        check_requirements
        create_directories
        start_dev
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs
        ;;
    build)
        check_docker
        check_docker_compose
        build_app
        ;;
    update-db)
        update_virus_db
        ;;
    diagnostics)
        run_diagnostics
        ;;
    backup)
        backup_data
        ;;
    restore)
        restore_data "$2"
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        print_error "Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac