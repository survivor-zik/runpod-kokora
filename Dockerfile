FROM ghcr.io/remsky/kokoro-fastapi-gpu:latest

# Switch back to root to install packages
USER root

# Copy requirements first for better layer caching
COPY requirements.txt /app/

# Install additional Python packages using uv
# The base image already has a venv at /app/.venv with PATH set up
RUN uv pip install --no-cache-dir -r /app/requirements.txt

# Copy application files
COPY handler.py /app/
COPY startup.sh /app/

# Make executable and set ownership (as root)
RUN chmod +x /app/startup.sh && \
    chown -R appuser:appuser /app

# Switch back to appuser
USER appuser

WORKDIR /app

# Use startup script to run both server and handler
CMD ["./startup.sh"]
