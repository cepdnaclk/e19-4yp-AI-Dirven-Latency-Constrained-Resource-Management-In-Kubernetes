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


from sklearn.metrics import mean_absolute_error, r2_score

cpu_mae = mean_absolute_error(y_cpu, cpu_pred)
mem_mae = mean_absolute_error(y_mem, mem_pred)

cpu_r2 = r2_score(y_cpu, cpu_pred)
mem_r2 = r2_score(y_mem, mem_pred)

print(f"CPU MAE: {cpu_mae:.4f}, R²: {cpu_r2:.4f}")
print(f"Memory MAE: {mem_mae:.4f}, R²: {mem_r2:.4f}")
