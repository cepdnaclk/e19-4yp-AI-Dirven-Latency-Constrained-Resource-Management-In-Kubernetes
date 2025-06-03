import streamlit as st
import pandas as pd
import numpy as np
from joblib import load
from model import TrendLearner
from preprocess import load_and_preprocess
from sklearn.metrics import mean_absolute_error, r2_score

st.set_page_config(layout="wide")
st.title("🧠 DARE TrendLearner Evaluation Dashboard")

# === Feature Engineering ===
def add_features(df):
    df = df.copy()
    df["RequestRate_Delta"] = df["Request Rate"].diff().fillna(0)
    df["Hour"] = pd.to_datetime(df["Timestamp"], format='mixed').dt.hour
    df["Hour_sin"] = np.sin(2 * np.pi * df["Hour"] / 24)
    df["Hour_cos"] = np.cos(2 * np.pi * df["Hour"] / 24)
    return df.drop(columns=["Hour"])

# === Load model and scaler ===
model = TrendLearner.load("models/tl_model.pkl")
scaler = load("models/scaler.pkl")

# === Load & prepare data ===
df = load_and_preprocess("data/resource_usage.csv")
df = add_features(df)

features = [
    "CPU Usage", "Memory Usage", "Request Rate", "CPU Limit", "Memory Limit",
    "Latency", "RequestRate_Delta", "Hour_sin", "Hour_cos"
]
X = df[features].values
y = df["CPU_Usage_Delta"].values
X_scaled = scaler.transform(X)

# === Evaluate batch ===
pred_batch = []
for xi in X_scaled:
    xi = xi.reshape(1, -1)
    cpu_pred, _ = model.predict_usage(xi)
    pred_batch.append(cpu_pred[0])
pred_batch = np.array(pred_batch)

mae_batch = mean_absolute_error(y, pred_batch)
r2_batch = r2_score(y, pred_batch)

# === Evaluate online adaptation ===
online_model = TrendLearner.load("models/tl_model.pkl")  # fresh copy
online_preds = []

for i in range(len(X_scaled)):
    xi = X_scaled[i].reshape(1, -1)
    yi = y[i]
    pred, _ = online_model.predict_usage(xi)
    online_preds.append(pred[0])
    online_model.partial_fit(xi, [yi], [0.0])  # dummy mem delta

mae_online = mean_absolute_error(y, online_preds)
r2_online = r2_score(y, online_preds)

# === Display ===
st.subheader("📊 Evaluation Metrics")

st.markdown("### 🔁 Batch Prediction vs 🧠 Online Adaptation")
col1, col2 = st.columns(2)

with col1:
    st.metric("Batch MAE (CPU Δ)", f"{mae_batch:.6f}")
    st.metric("Batch R² Score", f"{r2_batch:.4f}")

with col2:
    st.metric("Online MAE (CPU Δ)", f"{mae_online:.6f}")
    st.metric("Online R² Score", f"{r2_online:.4f}")

st.line_chart({
    "True ΔCPU": y,
    "Batch Prediction": pred_batch,
    "Online Prediction": online_preds
})

st.caption("📈 Lower MAE and higher R² indicate better predictions. Online mode adapts incrementally to the stream.")
