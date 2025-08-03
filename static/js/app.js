/**
 * SolidBeam Solution - ClamAV Web Interface
 * Main JavaScript application
 */

// Global variables
let metricsInterval;
let currentScan = null;

// Initialize application
document.addEventListener('DOMContentLoaded', function() {
    console.log('SolidBeam Solution - ClamAV Web Interface initialized');
    
    // Initialize components
    initializeEventListeners();
    loadInitialData();
    startMetricsRefresh();
    
    // Load data when tabs are shown
    document.querySelectorAll('[data-bs-toggle="tab"]').forEach(tab => {
        tab.addEventListener('shown.bs.tab', function(e) {
            const target = e.target.getAttribute('data-bs-target');
            switch(target) {
                case '#history':
                    loadHistory();
                    break;
                case '#quarantine':
                    loadQuarantine();
                    break;
                case '#diagnostics':
                    runDiagnostics();
                    break;
            }
        });
    });
});

// Initialize event listeners
function initializeEventListeners() {
    // Custom scan form
    document.getElementById('customScanForm').addEventListener('submit', function(e) {
        e.preventDefault();
        runCustomScan();
    });
    
    // File upload form
    document.getElementById('uploadForm').addEventListener('submit', function(e) {
        e.preventDefault();
        uploadAndScan();
    });
}

// Load initial data
function loadInitialData() {
    refreshMetrics();
    loadHistory();
}

// Start metrics refresh interval
function startMetricsRefresh() {
    metricsInterval = setInterval(refreshMetrics, 5000); // Refresh every 5 seconds
}

// API Functions
async function apiCall(endpoint, options = {}) {
    const defaultOptions = {
        method: 'GET',
        headers: {
            'Content-Type': 'application/json',
        },
    };
    
    const finalOptions = { ...defaultOptions, ...options };
    
    try {
        const response = await fetch(endpoint, finalOptions);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

// Metrics Functions
async function refreshMetrics() {
    try {
        const metrics = await apiCall('/api/metrics');
        updateMetricsDisplay(metrics);
    } catch (error) {
        console.error('Failed to refresh metrics:', error);
        updateStatusIndicator(false);
    }
}

function updateMetricsDisplay(metrics) {
    if (metrics.error) {
        console.error('Metrics error:', metrics.error);
        return;
    }
    
    // Update CPU
    const cpuPercent = Math.round(metrics.cpu_percent);
    document.getElementById('cpu-bar').style.width = `${cpuPercent}%`;
    document.getElementById('cpu-text').textContent = `${cpuPercent}%`;
    
    // Update memory
    const memoryPercent = Math.round(metrics.memory_percent);
    document.getElementById('memory-bar').style.width = `${memoryPercent}%`;
    document.getElementById('memory-text').textContent = `${memoryPercent}%`;
    
    // Update disk
    const diskPercent = Math.round(metrics.disk_percent);
    document.getElementById('disk-bar').style.width = `${diskPercent}%`;
    document.getElementById('disk-text').textContent = `${diskPercent}%`;
    
    // Update uptime
    const uptimeDays = Math.floor(metrics.uptime / 86400);
    document.getElementById('uptime-text').textContent = `${uptimeDays} days`;
    
    // Update status indicator
    updateStatusIndicator(true);
}

function updateStatusIndicator(online) {
    const indicator = document.getElementById('status-indicator');
    const statusText = document.getElementById('status-text');
    
    if (online) {
        indicator.className = 'fas fa-circle text-success me-1';
        statusText.textContent = 'Online';
    } else {
        indicator.className = 'fas fa-circle text-danger me-1';
        statusText.textContent = 'Offline';
    }
}

// Scan Functions
async function runQuickScan() {
    showLoading('Running quick scan...');
    
    try {
        const result = await apiCall('/api/scan/quick', { method: 'POST' });
        displayScanResults(result);
        loadHistory(); // Refresh history
    } catch (error) {
        showError('Quick scan failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function runCustomScan() {
    const path = document.getElementById('scanPath').value.trim();
    const recursive = document.getElementById('recursiveScan').checked;
    
    if (!path) {
        showError('Please enter a path to scan');
        return;
    }
    
    showLoading('Running custom scan...');
    
    try {
        const result = await apiCall('/api/scan/custom', {
            method: 'POST',
            body: JSON.stringify({ path, recursive })
        });
        displayScanResults(result);
        loadHistory(); // Refresh history
    } catch (error) {
        showError('Custom scan failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

async function uploadAndScan() {
    const fileInput = document.getElementById('fileUpload');
    const file = fileInput.files[0];
    
    if (!file) {
        showError('Please select a file to upload');
        return;
    }
    
    showLoading('Uploading and scanning file...');
    
    try {
        const formData = new FormData();
        formData.append('file', file);
        
        const response = await fetch('/api/scan/upload', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        displayScanResults(result);
        loadHistory(); // Refresh history
        
        // Clear file input
        fileInput.value = '';
    } catch (error) {
        showError('File upload and scan failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayScanResults(result) {
    const resultsContainer = document.getElementById('scanResults');
    
    if (result.scan_type === 'quick') {
        // Handle quick scan results
        let html = '<div class="scan-result success fade-in">';
        html += '<h6><i class="fas fa-bolt me-2"></i>Quick Scan Results</h6>';
        
        let totalInfected = 0;
        result.results.forEach(pathResult => {
            const infected = pathResult.result.infected_count || 0;
            totalInfected += infected;
            
            html += `<div class="mb-2">
                <strong>${pathResult.path}:</strong> 
                ${infected > 0 ? `<span class="virus-badge">${infected} infected</span>` : '<span class="safe-badge">Clean</span>'}
            </div>`;
        });
        
        html += `<div class="mt-2">
            <strong>Total Infected Files:</strong> ${totalInfected}
        </div>`;
        html += '</div>';
        
        resultsContainer.innerHTML = html;
    } else {
        // Handle single scan results
        const scanResult = result.result;
        const isSuccess = scanResult.success;
        const infectedCount = scanResult.infected_count || 0;
        
        let html = `<div class="scan-result ${isSuccess ? 'success' : 'error'} fade-in">`;
        html += `<h6><i class="fas fa-search me-2"></i>${result.scan_type.charAt(0).toUpperCase() + result.scan_type.slice(1)} Scan Results</h6>`;
        
        if (isSuccess) {
            html += `<div class="mb-2">
                <strong>Status:</strong> 
                ${infectedCount > 0 ? `<span class="virus-badge">${infectedCount} infected files found</span>` : '<span class="safe-badge">Clean</span>'}
            </div>`;
            
            if (scanResult.scan_duration) {
                html += `<div class="mb-2"><strong>Duration:</strong> ${scanResult.scan_duration.toFixed(2)} seconds</div>`;
            }
            
            if (infectedCount > 0 && scanResult.infected_files) {
                html += '<div class="mt-3"><strong>Infected Files:</strong><ul class="mt-2">';
                scanResult.infected_files.forEach(file => {
                    html += `<li><code>${file.file}</code> - ${file.virus}</li>`;
                });
                html += '</ul></div>';
            }
        } else {
            html += `<div class="text-danger"><strong>Error:</strong> ${scanResult.error}</div>`;
        }
        
        html += '</div>';
        resultsContainer.innerHTML = html;
    }
}

// History Functions
async function loadHistory() {
    try {
        const history = await apiCall('/api/history?limit=20');
        displayHistory(history);
    } catch (error) {
        console.error('Failed to load history:', error);
        document.getElementById('historyTable').innerHTML = 
            '<tr><td colspan="6" class="text-center text-danger">Failed to load history</td></tr>';
    }
}

function displayHistory(history) {
    const tbody = document.getElementById('historyTable');
    
    if (history.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center text-muted">No scan history found</td></tr>';
        return;
    }
    
    let html = '';
    history.forEach(record => {
        const timestamp = new Date(record.timestamp).toLocaleString();
        const statusClass = record.status === 'completed' ? 'status-completed' : 
                           record.status === 'failed' ? 'status-failed' : 'status-running';
        
        html += `<tr class="slide-in">
            <td><span class="status-badge ${statusClass}">${record.scan_type}</span></td>
            <td><code>${record.path}</code></td>
            <td><span class="status-badge ${statusClass}">${record.status}</span></td>
            <td>${record.infected_count || 0}</td>
            <td>${record.scan_duration ? record.scan_duration.toFixed(2) + 's' : '-'}</td>
            <td>${timestamp}</td>
        </tr>`;
    });
    
    tbody.innerHTML = html;
}

// Quarantine Functions
async function loadQuarantine() {
    try {
        const quarantine = await apiCall('/api/quarantine');
        displayQuarantine(quarantine);
    } catch (error) {
        console.error('Failed to load quarantine:', error);
        document.getElementById('quarantineTable').innerHTML = 
            '<tr><td colspan="5" class="text-center text-danger">Failed to load quarantine</td></tr>';
    }
}

function displayQuarantine(quarantine) {
    const tbody = document.getElementById('quarantineTable');
    
    if (quarantine.length === 0) {
        tbody.innerHTML = '<tr><td colspan="5" class="text-center text-muted">No quarantined files</td></tr>';
        return;
    }
    
    let html = '';
    quarantine.forEach(file => {
        const timestamp = new Date(file.timestamp).toLocaleString();
        const fileSize = formatFileSize(file.file_size);
        
        html += `<tr class="slide-in">
            <td><code>${file.original_path}</code></td>
            <td><span class="virus-badge">${file.virus_name || 'Unknown'}</span></td>
            <td>${fileSize}</td>
            <td>${timestamp}</td>
            <td>
                <button class="btn btn-sm btn-danger" onclick="removeFromQuarantine(${file.id})">
                    <i class="fas fa-trash me-1"></i>Delete
                </button>
            </td>
        </tr>`;
    });
    
    tbody.innerHTML = html;
}

async function removeFromQuarantine(fileId) {
    if (!confirm('Are you sure you want to permanently delete this file?')) {
        return;
    }
    
    try {
        await apiCall(`/api/quarantine/${fileId}`, { method: 'DELETE' });
        showSuccess('File removed from quarantine');
        loadQuarantine(); // Refresh list
    } catch (error) {
        showError('Failed to remove file from quarantine: ' + error.message);
    }
}

// Diagnostics Functions
async function runDiagnostics() {
    showLoading('Running diagnostics...');
    
    try {
        const diagnostics = await apiCall('/api/diagnostics');
        displayDiagnostics(diagnostics);
    } catch (error) {
        showError('Diagnostics failed: ' + error.message);
    } finally {
        hideLoading();
    }
}

function displayDiagnostics(diagnostics) {
    const container = document.getElementById('diagnosticsResults');
    
    let html = `<div class="mb-3">
        <strong>Diagnostics run at:</strong> ${new Date(diagnostics.timestamp).toLocaleString()}
    </div>`;
    
    Object.entries(diagnostics.tests).forEach(([testName, testResult]) => {
        const statusClass = testResult.status === 'PASS' ? 'pass' : 'fail';
        const icon = testResult.status === 'PASS' ? 'fa-check-circle' : 'fa-times-circle';
        const iconColor = testResult.status === 'PASS' ? 'text-success' : 'text-danger';
        
        html += `<div class="diagnostic-test ${statusClass} fade-in">
            <div class="d-flex align-items-center">
                <i class="fas ${icon} ${iconColor} me-2"></i>
                <strong>${testName.charAt(0).toUpperCase() + testName.slice(1)}:</strong>
                <span class="ms-2">${testResult.message}</span>
            </div>
        </div>`;
    });
    
    container.innerHTML = html;
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function showLoading(message = 'Processing...') {
    document.getElementById('loadingText').textContent = message;
    const modal = new bootstrap.Modal(document.getElementById('loadingModal'));
    modal.show();
}

function hideLoading() {
    const modal = bootstrap.Modal.getInstance(document.getElementById('loadingModal'));
    if (modal) {
        modal.hide();
    }
}

function showSuccess(message) {
    showAlert(message, 'success');
}

function showError(message) {
    showAlert(message, 'danger');
}

function showWarning(message) {
    showAlert(message, 'warning');
}

function showInfo(message) {
    showAlert(message, 'info');
}

function showAlert(message, type) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Insert at the top of the main content
    const mainContent = document.querySelector('.col-md-9');
    mainContent.insertBefore(alertDiv, mainContent.firstChild);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

// Cleanup on page unload
window.addEventListener('beforeunload', function() {
    if (metricsInterval) {
        clearInterval(metricsInterval);
    }
});