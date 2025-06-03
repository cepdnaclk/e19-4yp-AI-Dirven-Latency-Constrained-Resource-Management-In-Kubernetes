import optuna
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from dare_tl.model import TrendLearner
from dare_tl.preprocess import load_and_preprocess
from joblib import dump


def objective(trial):
    df = load_and_preprocess("data/resource_usage.csv")
    train_idx = int(len(df) * 0.8)
    train_df, test_df = df[:train_idx], df[train_idx:]

    features = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]
    X_train = train_df[features].values
    y_cpu_train = train_df["CPU_Usage_Delta"].values
    y_mem_train = train_df["Memory_Usage_Delta"].values

    X_test = test_df[features].values
    y_cpu_test = test_df["CPU_Usage_Delta"].values
    y_mem_test = test_df["Memory_Usage_Delta"].values

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Optuna hyperparameters
    alpha = trial.suggest_float("ema_alpha", 0.1, 0.9)
    backend = trial.suggest_categorical("backend", ["river", "river_forest"])

    model = TrendLearner(backend=backend, alpha=alpha)
    model.train(X_train_scaled, y_cpu_train, y_mem_train)

    pred_cpu, pred_mem = model.predict_usage(X_test_scaled)
    cpu_mse = mean_squared_error(y_cpu_test, pred_cpu)
    mem_mse = mean_squared_error(y_mem_test, pred_mem)

    return (cpu_mse + mem_mse) / 2


if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=30)

    print("Best trial:", study.best_trial.params)

    # Retrain on full data with best params
    df = load_and_preprocess("data/resource_usage.csv")
    X = df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu = df["CPU_Usage_Delta"].values
    y_mem = df["Memory_Usage_Delta"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best = study.best_trial.params
    final_model = TrendLearner(backend=best["backend"], alpha=best["ema_alpha"])
    final_model.train(X_scaled, y_cpu, y_mem)

    final_model.save("models/tl_model.pkl")
    dump(scaler, "models/scaler.pkl")
