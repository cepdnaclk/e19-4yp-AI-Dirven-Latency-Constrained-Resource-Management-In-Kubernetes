# Enhanced model and tuning code with improvements for performance

import optuna
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import TimeSeriesSplit
from enhanced_model import EnhancedTrendLearner
from preprocess import load_and_preprocess
import joblib
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedModelOptimizer:
    def __init__(self, data_path: str, test_size: float = 0.2):
        self.data_path = data_path
        self.test_size = test_size
        self.df = None
        self.scaler = None

    def load_data(self):
        self.df = load_and_preprocess(self.data_path)
        logger.info(f"Loaded {len(self.df)} samples")

    def create_time_series_splits(self, n_splits=5):
        tscv = TimeSeriesSplit(n_splits=n_splits)
        return tscv.split(self.df)

    def objective(self, trial):
        try:
            params = self._suggest_hyperparameters(trial)
            cv_scores = []
            tscv = TimeSeriesSplit(n_splits=3)

            features = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]
            X = self.df[features].values
            y_cpu = self.df["CPU_Usage_Delta"].values
            y_mem = self.df["Memory_Usage_Delta"].values

            for train_idx, val_idx in tscv.split(X):
                X_train, X_val = X[train_idx], X[val_idx]
                y_cpu_train, y_cpu_val = y_cpu[train_idx], y_cpu[val_idx]
                y_mem_train, y_mem_val = y_mem[train_idx], y_mem[val_idx]

                scaler = StandardScaler()
                X_train_scaled = scaler.fit_transform(X_train)
                X_val_scaled = scaler.transform(X_val)

                model = EnhancedTrendLearner(**params)
                model.train(X_train_scaled, y_cpu_train, y_mem_train)

                pred_cpu, pred_mem = model.predict_usage(X_val_scaled)
                if pred_cpu is not None and pred_mem is not None:
                    cpu_mse = mean_squared_error(y_cpu_val, pred_cpu)
                    mem_mse = mean_squared_error(y_mem_val, pred_mem)
                    cpu_mae = mean_absolute_error(y_cpu_val, pred_cpu)
                    mem_mae = mean_absolute_error(y_mem_val, pred_mem)
                    combined_score = (0.4 * cpu_mse + 0.4 * mem_mse + 0.1 * cpu_mae + 0.1 * mem_mae)
                    cv_scores.append(combined_score)
                else:
                    cv_scores.append(float('inf'))

            return np.mean(cv_scores)

        except Exception as e:
            logger.error(f"Trial failed: {e}")
            return float('inf')

    def _suggest_hyperparameters(self, trial) -> Dict[str, Any]:
        ema_alpha = trial.suggest_float("ema_alpha", 0.1, 0.9)
        window_size = trial.suggest_int("window_size", 5, 20)
        ensemble_method = trial.suggest_categorical("ensemble_method", ["sgd", "rf"])
        feature_engineering = trial.suggest_categorical("feature_engineering", [True, False])

        if ensemble_method == "sgd":
            sgd_params = {
                "alpha": trial.suggest_float("sgd_alpha", 1e-6, 1e-1, log=True),
                "eta0": trial.suggest_float("eta0", 1e-4, 0.1, log=True),
                "penalty": trial.suggest_categorical("penalty", ["l2", "l1", "elasticnet"]),
                "learning_rate": trial.suggest_categorical("learning_rate", ["constant", "adaptive", "invscaling"]),
                "max_iter": trial.suggest_int("max_iter", 1000, 5000),
                "tol": trial.suggest_float("tol", 1e-5, 1e-2, log=True),
                "random_state": 42
            }
            if sgd_params["penalty"] == "elasticnet":
                sgd_params["l1_ratio"] = trial.suggest_float("l1_ratio", 0.1, 0.9)
            cpu_params = mem_params = sgd_params

        elif ensemble_method == "rf":
            rf_params = {
                "n_estimators": trial.suggest_int("n_estimators", 100, 300),
                "max_depth": trial.suggest_int("max_depth", 10, 30),
                "min_samples_split": trial.suggest_int("min_samples_split", 2, 10),
                "min_samples_leaf": trial.suggest_int("min_samples_leaf", 1, 5),
                "max_features": trial.suggest_categorical("max_features", ["sqrt", "log2", None]),
                "random_state": 42,
                "n_jobs": -1
            }
            cpu_params = mem_params = rf_params

        return {
            "alpha": ema_alpha,
            "window_size": window_size,
            "ensemble_method": ensemble_method,
            "feature_engineering": feature_engineering,
            "cpu_params": cpu_params,
            "mem_params": mem_params
        }

    def optimize(self, n_trials: int = 100, study_name: str = "enhanced_trend_learner"):
        if self.df is None:
            self.load_data()

        study = optuna.create_study(
            direction="minimize",
            pruner=optuna.pruners.MedianPruner(n_startup_trials=5, n_warmup_steps=10),
            study_name=study_name
        )

        logger.info(f"Starting optimization with {n_trials} trials")
        study.optimize(self.objective, n_trials=n_trials, show_progress_bar=True)

        logger.info(f"Best trial: {study.best_trial.params}")
        logger.info(f"Best value: {study.best_value}")

        return study

    def train_final_model(self, best_params: Dict[str, Any], save_path: str = "models/enhanced_tl_model.pkl"):
        if self.df is None:
            self.load_data()

        sgd_specific_params = ['sgd_alpha', 'eta0', 'penalty', 'learning_rate', 'max_iter', 'tol', 'l1_ratio']
        rf_specific_params = ['n_estimators', 'max_depth', 'min_samples_split', 'min_samples_leaf', 'max_features']
        clean_params = {}
        for key, value in best_params.items():
            if key not in sgd_specific_params + rf_specific_params:
                clean_params[key] = value

        if clean_params.get('ensemble_method') == 'sgd':
            sgd_params = {k.replace('sgd_', ''): v for k, v in best_params.items() if k in sgd_specific_params}
            sgd_params.update({'random_state': 42})
            clean_params['cpu_params'] = sgd_params.copy()
            clean_params['mem_params'] = sgd_params.copy()

        if clean_params.get('ensemble_method') == 'rf':
            rf_params = {k: v for k, v in best_params.items() if k in rf_specific_params}
            rf_params.update({'random_state': 42, 'n_jobs': -1})
            clean_params['cpu_params'] = rf_params.copy()
            clean_params['mem_params'] = rf_params.copy()

        features = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]
        X = self.df[features].values
        y_cpu = self.df["CPU_Usage_Delta"].values
        y_mem = self.df["Memory_Usage_Delta"].values

        self.scaler = StandardScaler()
        X_scaled = self.scaler.fit_transform(X)

        split_idx = int(len(X_scaled) * 0.8)
        X_train, X_val = X_scaled[:split_idx], X_scaled[split_idx:]
        y_cpu_train, y_cpu_val = y_cpu[:split_idx], y_cpu[split_idx:]
        y_mem_train, y_mem_val = y_mem[:split_idx], y_mem[split_idx:]

        model = EnhancedTrendLearner(**clean_params)
        model.train(X_train, y_cpu_train, y_mem_train, validation_data=(X_val, y_cpu_val, y_mem_val))

        pred_cpu, pred_mem = model.predict_usage(X_val)
        if pred_cpu is not None and pred_mem is not None:
            cpu_mse = mean_squared_error(y_cpu_val, pred_cpu)
            mem_mse = mean_squared_error(y_mem_val, pred_mem)
            cpu_r2 = r2_score(y_cpu_val, pred_cpu)
            mem_r2 = r2_score(y_mem_val, pred_mem)
            logger.info(f"Final Model Performance:")
            logger.info(f"CPU - MSE: {cpu_mse:.6f}, R²: {cpu_r2:.4f}")
            logger.info(f"Memory - MSE: {mem_mse:.6f}, R²: {mem_r2:.4f}")

        model.save(save_path)
        scaler_path = save_path.replace("_model.pkl", "_scaler.pkl")
        joblib.dump(self.scaler, scaler_path)

        importance = model.get_feature_importance()
        if importance:
            logger.info("Feature Importance:")
            for feature, imp in importance['cpu_importance'].items():
                logger.info(f"  {feature}: {imp:.4f}")

        return model

    def analyze_model_performance(self, model_path: str, scaler_path: str):
        model = EnhancedTrendLearner.load(model_path)
        scaler = joblib.load(scaler_path)
        if self.df is None:
            self.load_data()

        test_idx = int(len(self.df) * (1 - self.test_size))
        test_df = self.df[test_idx:]
        features = ["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]
        X_test = test_df[features].values
        y_cpu_test = test_df["CPU_Usage_Delta"].values
        y_mem_test = test_df["Memory_Usage_Delta"].values

        X_test_scaled = scaler.transform(X_test)
        pred_cpu, pred_mem, cpu_std, mem_std = model.predict_with_uncertainty(X_test_scaled)

        if pred_cpu is not None:
            metrics = {
                'cpu_mse': mean_squared_error(y_cpu_test, pred_cpu),
                'mem_mse': mean_squared_error(y_mem_test, pred_mem),
                'cpu_mae': mean_absolute_error(y_cpu_test, pred_cpu),
                'mem_mae': mean_absolute_error(y_mem_test, pred_mem),
                'cpu_r2': r2_score(y_cpu_test, pred_cpu),
                'mem_r2': r2_score(y_mem_test, pred_mem)
            }
            logger.info("Test Set Performance:")
            for metric, value in metrics.items():
                logger.info(f"  {metric}: {value:.6f}")
            val_metrics = model.get_validation_metrics()
            if val_metrics:
                logger.info(f"Latest Validation R²: CPU={val_metrics['latest_cpu_r2']:.4f}, Memory={val_metrics['latest_mem_r2']:.4f}")
            return metrics
        return None

def run_enhanced_optimization():
    optimizer = EnhancedModelOptimizer("data/resource_usage.csv")
    study = optimizer.optimize(n_trials=100)
    best_params = study.best_trial.params
    model = optimizer.train_final_model(best_params)
    optimizer.analyze_model_performance("models/enhanced_tl_model.pkl", "models/enhanced_tl_scaler.pkl")
    return study, model

if __name__ == "__main__":
    study, model = run_enhanced_optimization()
