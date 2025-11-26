# Use a lightweight official Python runtime. Slim images reduce attack surface and size.
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# --- 1. Copy requirements and install dependencies ---
# Copy requirements first to leverage Docker layer caching. If requirements.txt doesn't change, 
# this layer and all subsequent layers up to the COPY command are reused, speeding up rebuilds.
COPY requirements.txt .

# Install dependencies, using --no-cache-dir to minimize image size and --no-warn-script-location 
# for a cleaner build log.
RUN pip install --no-cache-dir -r requirements.txt

# --- 2. Copy application code and model artifact ---
# The anomaly_detector.pkl file is crucial. It must be copied into the container 
# before the service starts up.
COPY anomaly_detector.pkl .
COPY detection_service.py .

# --- 3. Container Configuration ---

# Expose the port the FastAPI application runs on. This is for documentation and container 
# networking visibility, but requires the port to be mapped during 'docker run'.
EXPOSE 8000

# Command to run the application in a production-ready environment using Uvicorn.
# We use the Gunicorn worker class for production reliability (implied by Uvicorn's default settings
# in standard MLOps practices, but using Uvicorn directly is common in simple FastAPI deployments).
# --host 0.0.0.0 makes the service accessible from outside the container on the mapped port.
CMD ["uvicorn", "detection_service:app", "--host", "0.0.0.0", "--port", "8000"]