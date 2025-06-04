import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from dare_tl.preprocess import load_and_preprocess
from dare_tl.model import TrendLearner
import joblib

FEATURES = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]

def calculate_metrics(y_true, y_pred, label=""):
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (np.abs(y_true) + 1e-8))) * 100
    within_10pct = np.mean(np.abs(y_true - y_pred) <= 0.1 * np.abs(y_true)) * 100
    return {
        f"{label}_MAE": mae,
        f"{label}_RMSE": rmse,
        f"{label}_MAPE": mape,
        f"{label}_R2": r2,
        f"{label}_Accuracy_10pct": within_10pct
    }

def evaluate_model():
    df = load_and_preprocess("data/resource_usage.csv")
    test_df = df[int(len(df) * 0.8):]

    X_test = test_df[FEATURES].values
    y_cpu_test = test_df["CPU_Usage_Delta"].values
    y_mem_test = test_df["Memory_Usage_Delta"].values

    # Load model and scaler
    model = TrendLearner.load("models/tl_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    X_scaled = scaler.transform(X_test)

    y_cpu_pred = []
    y_mem_pred = []

    for i in range(len(X_scaled)):
        xi = X_scaled[i].reshape(1, -1)
        pred_cpu, pred_mem = model.predict_usage(xi)
        y_cpu_pred.append(pred_cpu[0])
        y_mem_pred.append(pred_mem[0])

    cpu_metrics = calculate_metrics(y_cpu_test, y_cpu_pred, label="CPU")
    mem_metrics = calculate_metrics(y_mem_test, y_mem_pred, label="Memory")

    print("\nModel Performance Metrics:")
    for k, v in {**cpu_metrics, **mem_metrics}.items():
        print(f"{k}: {v:.4f}")

    return y_cpu_test, y_cpu_pred, y_mem_test, y_mem_pred

def plot_predictions(y_true_cpu, y_pred_cpu, y_true_mem, y_pred_mem):
    plt.figure(figsize=(12, 5))

    plt.subplot(1, 2, 1)
    plt.scatter(y_true_cpu, y_pred_cpu, alpha=0.5)
    plt.plot([min(y_true_cpu), max(y_true_cpu)], [min(y_true_cpu), max(y_true_cpu)], 'r--')
    plt.title("CPU Delta: Actual vs Predicted")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")

    plt.subplot(1, 2, 2)
    plt.scatter(y_true_mem, y_pred_mem, alpha=0.5)
    plt.plot([min(y_true_mem), max(y_true_mem)], [min(y_true_mem), max(y_true_mem)], 'r--')
    plt.title("Memory Delta: Actual vs Predicted")
    plt.xlabel("Actual")
    plt.ylabel("Predicted")

    plt.tight_layout()
    plt.savefig("model_predictions.png")
    plt.show()

if __name__ == "__main__":
    y_true_cpu, y_pred_cpu, y_true_mem, y_pred_mem = evaluate_model()
    plot_predictions(y_true_cpu, y_pred_cpu, y_true_mem, y_pred_mem)
