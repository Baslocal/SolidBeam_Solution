# Multi-stage build for SolidBeam Solution ClamAV Web Interface
FROM python:3.11-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    wget \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install ClamAV
RUN wget -O - https://www.clamav.net/downloads/production/clamav-1.0.1.tar.gz | tar xz \
    && cd clamav-1.0.1 \
    && ./configure --prefix=/usr/local \
    && make -j$(nproc) \
    && make install

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    clamav \
    clamav-daemon \
    freshclam \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create application user
RUN groupadd -r clamav && useradd -r -g clamav clamav

# Create necessary directories
RUN mkdir -p /opt/clamav-web/{data,logs,quarantine} \
    && mkdir -p /var/lib/clamav \
    && mkdir -p /tmp/uploads \
    && chown -R clamav:clamav /opt/clamav-web \
    && chown -R clamav:clamav /var/lib/clamav \
    && chown -R clamav:clamav /tmp/uploads

# Copy Python packages from builder
COPY --from=builder /root/.local /home/clamav/.local

# Copy application code
COPY . /opt/clamav-web/app
WORKDIR /opt/clamav-web/app

# Set permissions
RUN chown -R clamav:clamav /opt/clamav-web/app

# Initialize ClamAV database
RUN freshclam --quiet

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Update virus definitions\n\
freshclam --quiet || true\n\
\n\
# Initialize database if not exists\n\
if [ ! -f /opt/clamav-web/data/clamav_web.db ]; then\n\
    python init_db.py\n\
fi\n\
\n\
# Start the application\n\
exec python app.py\n\
' > /opt/clamav-web/entrypoint.sh \
    && chmod +x /opt/clamav-web/entrypoint.sh

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:5000/health || exit 1

# Expose port
EXPOSE 5000

# Switch to clamav user
USER clamav

# Set PATH to include local Python packages
ENV PATH="/home/clamav/.local/bin:$PATH"

# Run entrypoint
ENTRYPOINT ["/opt/clamav-web/entrypoint.sh"]