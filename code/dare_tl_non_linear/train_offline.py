from preprocess import load_and_preprocess
from model import TrendLearner
import numpy as np
import os
from sklearn.preprocessing import StandardScaler
import joblib

df = load_and_preprocess("data/resource_usage.csv")


features = df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
y_cpu = df["CPU_Usage_Delta"].values
y_mem = df["Memory_Usage_Delta"].values

# Scale features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(features)

# Create models directory if it doesn't exist
os.makedirs("models", exist_ok=True)

# Save scaler for inference
joblib.dump(scaler, "models/scaler.pkl")

tl = TrendLearner()
tl.train(X_scaled, y_cpu, y_mem,tune=True, n_trials=100)



tl.save("models/tl_model.pkl")
print("Offline training complete and model saved.")

# Save trained model
tl.save("models/tl_model.pkl")
print("Offline training complete and model saved.")
print(f"Training data shape: {features.shape}")
print(f"Feature columns: CPU_Usage, Memory_Usage, RequestRate, CPU_Limit, Memory_Limit")
