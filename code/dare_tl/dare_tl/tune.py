import optuna
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error
from model import TrendLearner
from preprocess import load_and_preprocess
import joblib

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
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # Suggest hyperparameters
    ema_alpha = trial.suggest_float("ema_alpha", 0.1, 0.9)
    sgd_alpha = trial.suggest_float("sgd_alpha", 1e-5, 1e-1, log=True)
    sgd_eta0 = trial.suggest_float("eta0", 1e-4, 0.1, log=True)
    penalty = trial.suggest_categorical("penalty", ["l2", "l1", "elasticnet"])

    cpu_params = {
        "alpha": sgd_alpha,
        "eta0": sgd_eta0,
        "penalty": penalty,
        "learning_rate": "constant",
        "max_iter": 1000,
        "tol": 1e-3
    }

    mem_params = cpu_params.copy()

    model = TrendLearner(alpha=ema_alpha, cpu_params=cpu_params, mem_params=mem_params)
    model.train(X_train, y_cpu_train, y_mem_train)

    pred_cpu, pred_mem = model.predict_usage(X_test)
    cpu_mse = mean_squared_error(y_cpu_test, pred_cpu)
    mem_mse = mean_squared_error(y_mem_test, pred_mem)

    return (cpu_mse + mem_mse) / 2

if __name__ == "__main__":
    study = optuna.create_study(direction="minimize")
    study.optimize(objective, n_trials=50)

    print("Best trial:", study.best_trial.params)

    # Train final model on full dataset
    df = load_and_preprocess("data/resource_usage.csv")
    features = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]
    X = df[features].values
    y_cpu = df["CPU_Usage_Delta"].values
    y_mem = df["Memory_Usage_Delta"].values

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    best = study.best_trial.params
    cpu_params = {
        "alpha": best["sgd_alpha"],
        "eta0": best["eta0"],
        "penalty": best["penalty"],
        "learning_rate": "constant",
        "max_iter": 1000,
        "tol": 1e-3
    }
    model = TrendLearner(alpha=best["ema_alpha"], cpu_params=cpu_params, mem_params=cpu_params)
    model.train(X_scaled, y_cpu, y_mem)
    model.save("models/tl_model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
