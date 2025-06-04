import optuna
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from model import TrendLearner
from preprocess import load_and_preprocess
from joblib import dump


def add_features(df):
    df = df.copy()

    # Handle timestamp parsing with mixed formats
    df["Hour"] = pd.to_datetime(df["Timestamp"], format='mixed').dt.hour

    # Add engineered features
    df["RequestRate_Delta"] = df["Request Rate"].diff().fillna(0)
    df["Hour_sin"] = np.sin(2 * np.pi * df["Hour"] / 24)
    df["Hour_cos"] = np.cos(2 * np.pi * df["Hour"] / 24)

    return df.drop(columns=["Hour"])


def objective(trial):
    df = load_and_preprocess("data/resource_usage.csv")
    df = add_features(df)

    # Train/test split
    split_idx = int(len(df) * 0.8)
    train_df, test_df = df[:split_idx], df[split_idx:]

    features = [
        "CPU Usage", "Memory Usage", "Request Rate", "CPU Limit", "Memory Limit",
        "Latency", "RequestRate_Delta", "Hour_sin", "Hour_cos"
    ]

    X_train = train_df[features].values
    y_cpu_train = train_df["CPU_Usage_Delta"].values
    y_mem_train = train_df["Memory_Usage_Delta"].values

    X_test = test_df[features].values
    y_cpu_test = test_df["CPU_Usage_Delta"].values
    y_mem_test = test_df["Memory_Usage_Delta"].values

    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Suggest hyperparameters
    alpha = trial.suggest_float("ema_alpha", 0.1, 0.9)
    backend = trial.suggest_categorical("backend", ["river", "river_forest"])

    model = TrendLearner(backend=backend, alpha=alpha)
    model.train(X_train_scaled, y_cpu_train, y_mem_train)

    # Predict row-by-row for online compatibility
    pred_cpu = []
    for xi in X_test_scaled:
        xi = xi.reshape(1, -1)
        cpu_pred, _ = model.predict_usage(xi)
        pred_cpu.append(cpu_pred[0])

    pred_cpu = np.array(pred_cpu)

    # Evaluation metric
    cpu_mae = mean_absolute_error(y_cpu_test, pred_cpu)
    cpu_r2 = r2_score(y_cpu_test, pred_cpu)
    return cpu_mae + (1 - cpu_r2)  # lower is better


if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=30)

    print("Best trial params:", study.best_trial.params)

    # Retrain model on all data with best params
    df = load_and_preprocess("data/resource_usage.csv")
    df = add_features(df)

    features = [
        "CPU Usage", "Memory Usage", "Request Rate", "CPU Limit", "Memory Limit",
        "Latency", "RequestRate_Delta", "Hour_sin", "Hour_cos"
    ]

    X = df[features].values
    y_cpu = df["CPU_Usage_Delta"].values
    y_mem = df["Memory_Usage_Delta"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best = study.best_trial.params
    final_model = TrendLearner(backend=best["backend"], alpha=best["ema_alpha"])
    final_model.train(X_scaled, y_cpu, y_mem)

    final_model.save("models/tl_model.pkl")
    dump(scaler, "models/scaler.pkl")
