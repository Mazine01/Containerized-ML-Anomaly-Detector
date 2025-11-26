import joblib
import numpy as np
from sklearn.ensemble import IsolationForest

# --- 1. Generate Synthetic Data for Anomaly Detection ---
# Simulates two features: CPU Usage and Memory Load.
# Creates distinct clusters for 'normal' operational states and scattered points for 'anomalies'.
rng = np.random.RandomState(42)

# Generate normal, clustered data (98% of the data)
X_normal = 0.3 * rng.randn(1000, 2)
# np.r_ concatenates the arrays vertically to create two major clusters of normal activity
X_normal = np.r_[X_normal + 2, X_normal - 2] 

# Generate abnormal, scattered data (2% of the data)
# These points are scattered far from the normal clusters, simulating true anomalies
X_abnormal = rng.uniform(low=-6, high=6, size=(20, 2))

# Combine datasets for training
X_data = np.r_[X_normal, X_abnormal]


# --- 2. Train the Isolation Forest Model ---
# Isolation Forest is effective for this task as it isolates outliers rather than learning normal boundaries.
# contamination=0.02 estimates that 2% of the training data is expected to be anomalous.
print("Training Isolation Forest model...")
model = IsolationForest(contamination=0.02, random_state=42)
model.fit(X_data)
print("Training complete.")

# --- 3. Save the Trained Model Artifact ---
# The model is serialized using joblib, which is lightweight and fast for scikit-learn objects.
# The resulting file 'anomaly_detector.pkl' will be included in the Docker image.
MODEL_PATH = 'anomaly_detector.pkl'
joblib.dump(model, MODEL_PATH)
print(f"Model artifact saved successfully to {MODEL_PATH}")

# Optional: Quick test of the saved model
# This verifies the serialization/deserialization process works correctly.
test_point_normal = np.array([[2.1, 2.1]]) 
test_point_anomaly = np.array([[-5.0, 5.0]]) 

loaded_model = joblib.load(MODEL_PATH)
print(f"\nPrediction for normal point {test_point_normal[0]}: {loaded_model.predict(test_point_normal)} (1 = Normal)")
print(f"Prediction for anomaly point {test_point_anomaly[0]}: {loaded_model.predict(test_point_anomaly)} (-1 = Anomaly)")