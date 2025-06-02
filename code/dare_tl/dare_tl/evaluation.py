from model import TrendLearner
import joblib
import numpy as np
import pandas as pd

model_path = "./models/tl_model.pkl"
scaler_path = "./models/scaler.pkl"

model = TrendLearner.load(model_path)
scaler = joblib.load(scaler_path)

df = pd.read_csv("./data/resource_usage.csv")
X_raw = df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
y_cpu = df["CPU_Usage_Delta"].values
y_mem = df["Memory_Usage_Delta"].values

X_scaled = scaler.transform(X_raw)
cpu_pred, mem_pred = model.predict_usage(X_scaled)
