# Use an official Python slim image for a lightweight base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies if any needed (e.g., sudo for remediation logic)
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and default config
COPY src/ /app/src/
COPY configs/ /app/configs/

# Ensure the logs directory exists
RUN mkdir -p /app/logs

# Set Python path to find our modules
ENV PYTHONPATH=/app/src

# Set environment variables for flexibility
ENV CONFIG_PATH=/app/configs/default_rules.yaml
ENV LOG_DIR=/app/logs

# The tool might need root for 'systemctl' or 'rm' remediation actions
# In Kubernetes, this is often handled via sidecars or specific service accounts

# Default command
ENTRYPOINT ["python", "src/main.py"]
CMD ["--config", "/app/configs/default_rules.yaml", "--logs", "/app/logs", "--follow"]
