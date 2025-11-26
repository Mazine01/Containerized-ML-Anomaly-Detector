Containerized ML Model Deployment & API Integration (MLOps Focus)

This project demonstrates the successful deployment of an Anomaly Detection Machine Learning model as a production-ready, scalable REST API service using Python (FastAPI) and Docker. The focus is on security, reliability, and container optimization for robust deployment in UNIX/Linux environments.

1. Project Architecture Overview

The system utilizes a microservice approach: the ML core runs independently, and a conceptual external service (like a Java Spring Boot backend) would act as a secure gateway to consume its predictions.

Key Objectives Achieved:

REST API Development: Built a high-performance prediction API using FastAPI.

Containerization: Packaged the model, dependencies, and service into a single Docker image for environmental consistency.

Security & Monitoring: Implemented strict input validation (Pydantic) and a crucial /health check endpoint for production readiness.

2. ML Component: Anomaly Detection

Model: Isolation Forest

The model is trained to detect unusual server activity (anomalies) based on two features: CPU Usage and Memory Load. The IsolationForest model is used for its efficiency in detecting outliers in high-dimensional datasets.

Files

anomaly_model.py: Trains the Isolation Forest model and saves it to disk.

anomaly_detector.pkl: The serialized (trained) model artifact.

detection_service.py: Loads the model and serves predictions via FastAPI.

3. Secure Backend Implementation Highlights

The detection_service.py is designed with security and resilience in mind:

| Feature | Description | Production Value |
| Input Validation | Uses Pydantic to ensure the input payload always contains two valid floats, preventing model crashes from malformed data. | Security: Mitigates data injection and validation attacks. |
| /health Endpoint | Checks if the service is running AND if the anomaly_detector.pkl model file is successfully loaded into memory. | Reliability: Enables Kubernetes/Load Balancers to correctly identify a failed service instance. |
| Structured Error Handling | Catches internal exceptions and returns clean, controlled HTTPException responses (e.g., 500 or 503). | Security: Prevents exposure of internal stack traces to external clients. |

4. Deployment Instructions (Production Ready)

A. Local Setup (Generate Model Artifact)

Install dependencies locally:

pip install -r requirements.txt



Generate the model artifact:

python anomaly_model.py



This creates the anomaly_detector.pkl file, which must be present for the next step.

B. Container Build and Run (Docker Confirmed Ready)

All required files are present and tested. Use these commands to build and run the final container:

Build the Docker Image:

# This command uses the Dockerfile to create an image tagged 'ml-anomaly-api'
docker build -t ml-anomaly-api .



Run the Container:

# Runs the container in detached mode (-d) and maps the internal container port 8000 
# to the host machine's port 8000 (-p).
docker run -d --name anomaly-service -p 8000:8000 ml-anomaly-api



5. Verification and Testing

The service is now running on http://localhost:8000.

A. Health Check (Monitoring Test)

Verify that the service is running and the model is loaded:

curl -X GET http://localhost:8000/health



B. Prediction Test (Anomaly Detection)

Test an input point that should be classified as an Anomaly (e.g., extreme values):

curl -X POST http://localhost:8000/predict \
     -H 'Content-Type: application/json' \
     -d '{"data": [-5.5, 5.2]}'
# Expected: "prediction_score": -1 (Anomaly)



Test an input point that should be classified as Normal Traffic (e.g., clustered near the mean):

curl -X POST http://localhost:8000/predict \
     -H 'Content-Type: application/json' \
     -d '{"data": [2.1, 2.1]}'
# Expected: "prediction_score": 1 (Normal)

