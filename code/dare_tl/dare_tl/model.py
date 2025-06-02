import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.metrics import mean_squared_error
from joblib import dump, load
import sys
import optuna

class TrendLearner:
    def __init__(self, alpha=0.3, cpu_params=None, mem_params=None):
        self.alpha = alpha
        self.cpu_model = SGDRegressor(**(cpu_params or {"max_iter": 1000, "tol": 1e-3}))
        self.mem_model = SGDRegressor(**(mem_params or {"max_iter": 1000, "tol": 1e-3}))
        self.ema_feature = None  # For storing EMA of inputs
        self.is_fitted = False
        
    def _split_data(self, X, y_cpu, y_mem, ratio=0.8):
        split_idx = int(len(X) * ratio)
        return (
            X[:split_idx], X[split_idx:],
            y_cpu[:split_idx], y_cpu[split_idx:],
            y_mem[:split_idx], y_mem[split_idx:]
        )
        
    def _optuna_objective(self, trial, X_train, X_val, y_cpu_train, y_cpu_val, y_mem_train, y_mem_val):
        cpu_params = {
            "alpha": trial.suggest_loguniform("cpu_alpha", 1e-6, 1e-1),
            "max_iter": trial.suggest_int("cpu_max_iter", 500, 2000),
            "tol": trial.suggest_float("cpu_tol", 1e-4, 1e-2),
            "eta0": trial.suggest_loguniform("cpu_eta0", 1e-4, 1e-1),
            "learning_rate": trial.suggest_categorical("cpu_lr", ["constant", "optimal", "invscaling", "adaptive"]),
        }
        mem_params = {
            "alpha": trial.suggest_loguniform("mem_alpha", 1e-6, 1e-1),
            "max_iter": trial.suggest_int("mem_max_iter", 500, 2000),
            "tol": trial.suggest_float("mem_tol", 1e-4, 1e-2),
            "eta0": trial.suggest_loguniform("mem_eta0", 1e-4, 1e-1),
            "learning_rate": trial.suggest_categorical("mem_lr", ["constant", "optimal", "invscaling", "adaptive"]),
        }
        alpha_ema = trial.suggest_float("ema_alpha", 0.01, 0.9)

        learner = TrendLearner(alpha=alpha_ema, cpu_params=cpu_params, mem_params=mem_params)
        learner.train(X_train, y_cpu_train, y_mem_train, tune=False)

        cpu_pred, mem_pred = learner.predict_usage(X_val)
        cpu_loss = mean_squared_error(y_cpu_val, cpu_pred)
        mem_loss = mean_squared_error(y_mem_val, mem_pred)

        return cpu_loss + mem_loss
        
    def _apply_ema(self, X):
        if self.ema_feature is None:
            self.ema_feature = X.copy()
        else:
            self.ema_feature = self.alpha * X + (1 - self.alpha) * self.ema_feature
        return self.ema_feature

    def train(self, X, y_cpu, y_mem):
        for xi, y_cpu_i, y_mem_i in zip(X, y_cpu, y_mem):
            xi = xi.reshape(1, -1)
            xi_ema = self._apply_ema(xi)
            if not self.is_fitted:
                # First fit
                self.cpu_model.fit(xi_ema, [y_cpu_i])
                self.mem_model.fit(xi_ema, [y_mem_i])
                self.is_fitted = True
            else:
                # Partial fit for subsequent data
                self.cpu_model.partial_fit(xi_ema, [y_cpu_i])
                self.mem_model.partial_fit(xi_ema, [y_mem_i])
            
    def predict_usage(self, X):
        """Predict CPU and memory usage deltas"""
        if not self.is_fitted:
            return None, None
        
        X_ema = self._apply_ema(X)  # Or pass last_X if you have history
        cpu_pred = self.cpu_model.predict(X_ema)
        mem_pred = self.mem_model.predict(X_ema)
        return cpu_pred, mem_pred
    
    def save(self, path):
        dump(self, path)
        
    @staticmethod
    def load(path):
        """Load model from file"""
        return load(path)
    
    def safe_range(self, pred_cpu, pred_mem, cpu_margin=0.1, mem_margin=0.1):
        cpu_min = max(0, pred_cpu * (1 - cpu_margin))
        cpu_max = pred_cpu * (1 + cpu_margin)
        mem_min = max(0, pred_mem * (1 - mem_margin))
        mem_max = pred_mem * (1 + mem_margin)
        return {
            "cpu_range_m": (round(cpu_min, 4), round(cpu_max, 4)),
            "mem_range_mib": (round(mem_min, 0), round(mem_max, 0)),
        }
        
    def partial_fit(self, X, y_cpu, y_mem):
        """Update model with new data point"""
        if not self.is_fitted:
            # If not fitted yet, use regular fit
            self.train(X, y_cpu, y_mem)
        else:
            X_ema = self._apply_ema(X)
            self.cpu_model.partial_fit(X_ema, y_cpu)
            self.mem_model.partial_fit(X_ema, y_mem)