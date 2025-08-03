#!/usr/bin/env python3
"""
SolidBeam Solution - ClamAV Web Interface
Main Flask application with API endpoints
"""

import os
import json
import subprocess
import shutil
import time
import uuid
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import psutil
import sqlite3
from werkzeug.utils import secure_filename
import magic

# Configuration
SCAN_TIMEOUT = 300  # 5 minutes
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
QUARANTINE_ENABLED = True
LOG_LEVEL = 'INFO'

# Initialize Flask app
app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE
CORS(app)

# Database setup
DB_PATH = os.environ.get('CLAMAV_DB_PATH', '/opt/clamav-web/data')
QUARANTINE_PATH = os.environ.get('CLAMAV_QUARANTINE_PATH', '/opt/clamav-web/quarantine')
LOGS_PATH = os.environ.get('CLAMAV_LOGS_PATH', '/opt/clamav-web/logs')

# Ensure directories exist
os.makedirs(DB_PATH, exist_ok=True)
os.makedirs(QUARANTINE_PATH, exist_ok=True)
os.makedirs(LOGS_PATH, exist_ok=True)

DB_FILE = os.path.join(DB_PATH, 'clamav_web.db')

def init_db():
    """Initialize SQLite database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Create scan history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scan_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            scan_type TEXT NOT NULL,
            path TEXT NOT NULL,
            status TEXT NOT NULL,
            infected_count INTEGER DEFAULT 0,
            total_files INTEGER DEFAULT 0,
            scan_duration REAL DEFAULT 0,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            details TEXT
        )
    ''')
    
    # Create quarantine table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS quarantine (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_path TEXT NOT NULL,
            quarantine_path TEXT NOT NULL,
            virus_name TEXT,
            file_size INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'quarantined'
        )
    ''')
    
    conn.commit()
    conn.close()

def log_scan(scan_type, path, status, infected_count=0, total_files=0, scan_duration=0, details=None):
    """Log scan results to database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scan_history (scan_type, path, status, infected_count, total_files, scan_duration, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (scan_type, path, status, infected_count, total_files, scan_duration, details))
    
    conn.commit()
    conn.close()

def get_scan_history(limit=50):
    """Get scan history from database"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, scan_type, path, status, infected_count, total_files, scan_duration, timestamp, details
        FROM scan_history
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (limit,))
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'scan_type': row[1],
            'path': row[2],
            'status': row[3],
            'infected_count': row[4],
            'total_files': row[5],
            'scan_duration': row[6],
            'timestamp': row[7],
            'details': row[8]
        }
        for row in results
    ]

def quarantine_file(file_path, virus_name=None):
    """Move infected file to quarantine"""
    if not QUARANTINE_ENABLED:
        return None
    
    try:
        file_size = os.path.getsize(file_path)
        quarantine_filename = f"{uuid.uuid4()}_{os.path.basename(file_path)}"
        quarantine_file_path = os.path.join(QUARANTINE_PATH, quarantine_filename)
        
        # Move file to quarantine
        shutil.move(file_path, quarantine_file_path)
        
        # Log to database
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO quarantine (original_path, quarantine_path, virus_name, file_size)
            VALUES (?, ?, ?, ?)
        ''', (file_path, quarantine_file_path, virus_name, file_size))
        
        conn.commit()
        conn.close()
        
        return quarantine_file_path
    except Exception as e:
        app.logger.error(f"Failed to quarantine {file_path}: {e}")
        return None

def get_quarantine_list():
    """Get list of quarantined files"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, original_path, quarantine_path, virus_name, file_size, timestamp, status
        FROM quarantine
        ORDER BY timestamp DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    return [
        {
            'id': row[0],
            'original_path': row[1],
            'quarantine_path': row[2],
            'virus_name': row[3],
            'file_size': row[4],
            'timestamp': row[5],
            'status': row[6]
        }
        for row in results
    ]

def run_clamscan(path, recursive=True):
    """Run ClamAV scan on specified path"""
    start_time = time.time()
    
    try:
        # Build clamscan command
        cmd = ['clamscan', '--no-summary', '--infected']
        if recursive:
            cmd.append('--recursive')
        cmd.append(path)
        
        # Run scan with timeout
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=SCAN_TIMEOUT
        )
        
        scan_duration = time.time() - start_time
        
        # Parse results
        infected_files = []
        if result.returncode == 1:  # Found viruses
            for line in result.stdout.split('\n'):
                if line.strip() and ': ' in line:
                    file_path, virus_name = line.rsplit(': ', 1)
                    if virus_name != 'OK':
                        infected_files.append({
                            'file': file_path.strip(),
                            'virus': virus_name.strip()
                        })
        
        return {
            'success': True,
            'infected_count': len(infected_files),
            'infected_files': infected_files,
            'scan_duration': scan_duration,
            'output': result.stdout,
            'error': result.stderr
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Scan timeout exceeded',
            'scan_duration': SCAN_TIMEOUT
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'scan_duration': time.time() - start_time
        }

def get_system_metrics():
    """Get system metrics"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        return {
            'cpu_percent': cpu_percent,
            'memory_total': memory.total,
            'memory_available': memory.available,
            'memory_percent': memory.percent,
            'disk_total': disk.total,
            'disk_free': disk.free,
            'disk_percent': (disk.used / disk.total) * 100,
            'uptime': time.time() - psutil.boot_time()
        }
    except Exception as e:
        return {'error': str(e)}

def run_diagnostics():
    """Run comprehensive system diagnostics"""
    diagnostics = {
        'timestamp': datetime.now().isoformat(),
        'tests': {}
    }
    
    # Test 1: Database connectivity
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM scan_history')
        count = cursor.fetchone()[0]
        conn.close()
        diagnostics['tests']['database'] = {
            'status': 'PASS',
            'message': f'Database accessible, {count} scan records found'
        }
    except Exception as e:
        diagnostics['tests']['database'] = {
            'status': 'FAIL',
            'message': f'Database error: {e}'
        }
    
    # Test 2: ClamAV availability
    try:
        result = subprocess.run(['clamscan', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            version = result.stdout.split('\n')[0]
            diagnostics['tests']['clamav'] = {
                'status': 'PASS',
                'message': f'ClamAV available: {version}'
            }
        else:
            diagnostics['tests']['clamav'] = {
                'status': 'FAIL',
                'message': 'ClamAV not responding'
            }
    except Exception as e:
        diagnostics['tests']['clamav'] = {
            'status': 'FAIL',
            'message': f'ClamAV error: {e}'
        }
    
    # Test 3: Quarantine directory
    try:
        if os.path.exists(QUARANTINE_PATH) and os.access(QUARANTINE_PATH, os.W_OK):
            diagnostics['tests']['quarantine'] = {
                'status': 'PASS',
                'message': 'Quarantine directory accessible'
            }
        else:
            diagnostics['tests']['quarantine'] = {
                'status': 'FAIL',
                'message': 'Quarantine directory not accessible'
            }
    except Exception as e:
        diagnostics['tests']['quarantine'] = {
            'status': 'FAIL',
            'message': f'Quarantine error: {e}'
        }
    
    # Test 4: Upload directory
    try:
        upload_dir = '/tmp/uploads'
        if os.path.exists(upload_dir) and os.access(upload_dir, os.W_OK):
            diagnostics['tests']['uploads'] = {
                'status': 'PASS',
                'message': 'Upload directory accessible'
            }
        else:
            diagnostics['tests']['uploads'] = {
                'status': 'FAIL',
                'message': 'Upload directory not accessible'
            }
    except Exception as e:
        diagnostics['tests']['uploads'] = {
            'status': 'FAIL',
            'message': f'Upload error: {e}'
        }
    
    # Test 5: System resources
    try:
        metrics = get_system_metrics()
        if 'error' not in metrics:
            diagnostics['tests']['resources'] = {
                'status': 'PASS',
                'message': f'CPU: {metrics["cpu_percent"]}%, Memory: {metrics["memory_percent"]:.1f}%'
            }
        else:
            diagnostics['tests']['resources'] = {
                'status': 'FAIL',
                'message': f'Resource monitoring error: {metrics["error"]}'
            }
    except Exception as e:
        diagnostics['tests']['resources'] = {
            'status': 'FAIL',
            'message': f'Resource error: {e}'
        }
    
    return diagnostics

# Routes
@app.route('/')
def index():
    """Serve the main web interface"""
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

@app.route('/api/scan/quick', methods=['POST'])
def quick_scan():
    """Perform quick scan of common paths"""
    common_paths = ['/tmp', '/var/tmp', '/home']
    results = []
    
    for path in common_paths:
        if os.path.exists(path):
            scan_result = run_clamscan(path, recursive=True)
            results.append({
                'path': path,
                'result': scan_result
            })
    
    # Log scan
    total_infected = sum(r['result']['infected_count'] for r in results if r['result']['success'])
    log_scan('quick', ';'.join(common_paths), 'completed', total_infected, 0, 0)
    
    return jsonify({
        'scan_type': 'quick',
        'results': results,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scan/custom', methods=['POST'])
def custom_scan():
    """Perform custom scan of specified path"""
    data = request.get_json()
    path = data.get('path', '')
    recursive = data.get('recursive', True)
    
    if not path or not os.path.exists(path):
        return jsonify({'error': 'Invalid path'}), 400
    
    scan_result = run_clamscan(path, recursive)
    
    # Log scan
    log_scan('custom', path, 'completed' if scan_result['success'] else 'failed',
             scan_result.get('infected_count', 0), 0, scan_result.get('scan_duration', 0))
    
    return jsonify({
        'scan_type': 'custom',
        'path': path,
        'result': scan_result,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/scan/upload', methods=['POST'])
def upload_scan():
    """Scan uploaded file"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    filename = secure_filename(file.filename)
    upload_path = os.path.join('/tmp/uploads', filename)
    
    try:
        file.save(upload_path)
        
        # Scan the uploaded file
        scan_result = run_clamscan(upload_path, recursive=False)
        
        # Quarantine if infected
        if scan_result['success'] and scan_result['infected_count'] > 0:
            for infected in scan_result['infected_files']:
                quarantine_file(infected['file'], infected['virus'])
        
        # Clean up uploaded file
        if os.path.exists(upload_path):
            os.remove(upload_path)
        
        # Log scan
        log_scan('upload', filename, 'completed' if scan_result['success'] else 'failed',
                 scan_result.get('infected_count', 0), 1, scan_result.get('scan_duration', 0))
        
        return jsonify({
            'scan_type': 'upload',
            'filename': filename,
            'result': scan_result,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/history')
def get_history():
    """Get scan history"""
    limit = request.args.get('limit', 50, type=int)
    history = get_scan_history(limit)
    return jsonify(history)

@app.route('/api/metrics')
def get_metrics():
    """Get system metrics"""
    metrics = get_system_metrics()
    return jsonify(metrics)

@app.route('/api/diagnostics')
def get_diagnostics():
    """Run system diagnostics"""
    diagnostics = run_diagnostics()
    return jsonify(diagnostics)

@app.route('/api/quarantine')
def get_quarantine():
    """Get quarantine list"""
    quarantine_list = get_quarantine_list()
    return jsonify(quarantine_list)

@app.route('/api/quarantine/<int:file_id>', methods=['DELETE'])
def remove_quarantine(file_id):
    """Remove file from quarantine"""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Get file info
    cursor.execute('SELECT quarantine_path FROM quarantine WHERE id = ?', (file_id,))
    result = cursor.fetchone()
    
    if not result:
        conn.close()
        return jsonify({'error': 'File not found'}), 404
    
    quarantine_path = result[0]
    
    try:
        # Delete file
        if os.path.exists(quarantine_path):
            os.remove(quarantine_path)
        
        # Remove from database
        cursor.execute('DELETE FROM quarantine WHERE id = ?', (file_id,))
        conn.commit()
        
        conn.close()
        return jsonify({'message': 'File removed from quarantine'})
        
    except Exception as e:
        conn.close()
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Initialize database
    init_db()
    
    # Start Flask app
    port = int(os.environ.get('CLAMAV_WEB_PORT', 5000))
    host = os.environ.get('CLAMAV_WEB_HOST', '0.0.0.0')
    
    app.run(host=host, port=port, debug=False)