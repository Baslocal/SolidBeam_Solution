#!/usr/bin/env python3
"""
Database initialization script for SolidBeam Solution ClamAV Web Interface
"""

import os
import sqlite3
from datetime import datetime

# Database setup
DB_PATH = os.environ.get('CLAMAV_DB_PATH', '/opt/clamav-web/data')
os.makedirs(DB_PATH, exist_ok=True)
DB_FILE = os.path.join(DB_PATH, 'clamav_web.db')

def init_database():
    """Initialize the SQLite database with required tables"""
    print(f"Initializing database at: {DB_FILE}")
    
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
    print("✓ Created scan_history table")
    
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
    print("✓ Created quarantine table")
    
    # Create indexes for better performance
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_history_timestamp ON scan_history(timestamp)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scan_history_type ON scan_history(scan_type)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_quarantine_timestamp ON quarantine(timestamp)')
    print("✓ Created database indexes")
    
    # Insert initial system record
    cursor.execute('''
        INSERT INTO scan_history (scan_type, path, status, infected_count, total_files, scan_duration, details)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', ('system', 'initialization', 'completed', 0, 0, 0, 'Database initialized'))
    
    conn.commit()
    conn.close()
    
    print("✓ Database initialization completed successfully")
    print(f"✓ Database file: {DB_FILE}")

if __name__ == '__main__':
    try:
        init_database()
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        exit(1)