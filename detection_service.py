import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List

# --- 1. Model Loading ---
MODEL_PATH = 'anomaly_detector.pkl'
model = None # Initialize model globally

try:
    # Load the trained model artifact into memory. This happens once at service startup.
    model = joblib.load(MODEL_PATH)
    print(f"Successfully loaded model from {MODEL_PATH}")
except FileNotFoundError:
    # If the model file is missing, the service starts, but the health check will fail (503).
    print(f"ERROR: Model file '{MODEL_PATH}' not found. Prediction service will be non-functional.")
except Exception as e:
    print(f"ERROR: Failed to load model artifact due to: {e}")

# --- 2. FastAPI Setup ---
app = FastAPI(
    title="Containerized Anomaly Detection API",
    description="A secure, containerized service exposing an Isolation Forest model for real-time anomaly detection.",
    version="1.0.0"
)


# --- 3. Define Secure Input Schema (Pydantic) ---
# This is crucial for security. Pydantic strictly validates the request payload structure 
# before any data touches the ML model, preventing runtime errors and malformed data issues.
class PredictionRequest(BaseModel):
    # Enforces that 'data' must be a list of exactly two floats: [CPU_Usage, Memory_Load]
    data: List[float] = Field(..., min_length=2, max_length=2, description="List of two features [CPU_Usage, Memory_Load].")

# --- 4. Secure API Endpoint for Prediction ---

@app.post("/predict", tags=["Prediction"])
async def predict_anomaly(request: PredictionRequest):
    """
    Analyzes input data (CPU Usage, Memory Load) to determine if it is anomalous.
    Returns: 1 (Normal) or -1 (Anomaly).
    """
    # Check if the core ML model is available (ensures 503 is returned if model load failed)
    if model is None:
        raise HTTPException(status_code=503, detail="Model artifact not loaded. Service unavailable.")
        
    try:
        # Convert the input list to a NumPy array, reshaped for scikit-learn model input (1 sample, 2 features)
        input_data = np.array(request.data).reshape(1, -1)
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        
        # Map prediction result to a human-readable status
        status = "Anomaly Detected" if prediction == -1 else "Normal Traffic"
        
        return {
            "status": status,
            "prediction_score": int(prediction),
            "input_data": request.data,
            "message": "Prediction successful. Score of -1 indicates an anomaly."
        }
    except Exception as e:
        # Structured 500 Error Handling: Prevents exposure of internal exceptions/stack traces, a security best practice.
        print(f"Prediction failed due to internal error: {e}")
        raise HTTPException(status_code=500, detail="Internal processing error during prediction.")

# --- 5. Health Check Endpoint (Monitoring) ---

@app.get("/health", tags=["Monitoring"])
def health_check():
    """
    Returns the service status and model availability.
    Crucial for container orchestration platforms (Docker, Kubernetes) to verify service readiness.
    """
    model_loaded_status = model is not None
    
    if not model_loaded_status:
        # Returns 503 Service Unavailable if the model (the core dependency) is missing
        raise HTTPException(status_code=503, detail="Service is running, but the ML model failed to load.")
        
    return {
        "status": "OK",
        "service": app.title,
        "model_loaded": model_loaded_status,
        "message": "Service is running and ML model is operational."
    }

# NOTE: This application is designed to be run using Uvicorn/Gunicorn as defined in the Dockerfile.