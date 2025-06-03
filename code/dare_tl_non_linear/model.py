import numpy as np
from joblib import dump, load

# Optional import (River is required for advanced models)
try:
    from river import linear_model, ensemble, preprocessing, metrics, compose
    RIVER_AVAILABLE = True
except ImportError:
    RIVER_AVAILABLE = False

from sklearn.linear_model import SGDRegressor

class TrendLearner:
    def __init__(self, backend="sgd", alpha=0.3, cpu_params=None, mem_params=None):
        self.backend = backend
        self.alpha = alpha
        self.ema_feature = None
        self.is_fitted = False

        if self.backend == "sgd":
            self.cpu_model = SGDRegressor(**(cpu_params or {"max_iter": 1000, "tol": 1e-3}))
            self.mem_model = SGDRegressor(**(mem_params or {"max_iter": 1000, "tol": 1e-3}))

        elif self.backend == "river":
            if not RIVER_AVAILABLE:
                raise ImportError("River is not installed. Install it via 'pip install river'")

            self.cpu_model = compose.Pipeline(
                preprocessing.StandardScaler(),
                linear_model.LinearRegression()
            )
            self.mem_model = compose.Pipeline(
                preprocessing.StandardScaler(),
                linear_model.LinearRegression()
            )

        elif self.backend == "river_forest":
            if not RIVER_AVAILABLE:
                raise ImportError("River is not installed. Install it via 'pip install river'")

            self.cpu_model = ensemble.AdaptiveRandomForestRegressor(seed=42)
            self.mem_model = ensemble.AdaptiveRandomForestRegressor(seed=42)
        else:
            raise ValueError(f"Unsupported backend: {self.backend}")

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

            if self.backend.startswith("river"):
                x_dict = {f"f{i}": xi_ema[0][i] for i in range(xi_ema.shape[1])}
                self.cpu_model.learn_one(x_dict, y_cpu_i)
                self.mem_model.learn_one(x_dict, y_mem_i)
                self.is_fitted = True
            else:
                if not self.is_fitted:
                    self.cpu_model.fit(xi_ema, [y_cpu_i])
                    self.mem_model.fit(xi_ema, [y_mem_i])
                    self.is_fitted = True
                else:
                    self.cpu_model.partial_fit(xi_ema, [y_cpu_i])
                    self.mem_model.partial_fit(xi_ema, [y_mem_i])

    def predict_usage(self, X):
        if not self.is_fitted:
            return None, None

        X_ema = self._apply_ema(X)

        if self.backend.startswith("river"):
            x_dict = {f"f{i}": X_ema[0][i] for i in range(X_ema.shape[1])}
            cpu_pred = self.cpu_model.predict_one(x_dict)
            mem_pred = self.mem_model.predict_one(x_dict)
            return np.array([cpu_pred]), np.array([mem_pred])
        else:
            return self.cpu_model.predict(X_ema), self.mem_model.predict(X_ema)

    def partial_fit(self, X, y_cpu, y_mem):
        if not self.is_fitted:
            self.train(X, y_cpu, y_mem)
        else:
            X_ema = self._apply_ema(X)
            if self.backend.startswith("river"):
                x_dict = {f"f{i}": X_ema[0][i] for i in range(X_ema.shape[1])}
                self.cpu_model.learn_one(x_dict, y_cpu[0])
                self.mem_model.learn_one(x_dict, y_mem[0])
            else:
                self.cpu_model.partial_fit(X_ema, y_cpu)
                self.mem_model.partial_fit(X_ema, y_mem)

    def save(self, path):
        dump(self, path)

    @staticmethod
    def load(path):
        return load(path)

    def safe_range(self, pred_cpu, pred_mem, cpu_margin=0.1, mem_margin=0.1):
        return {
            "cpu_range_m": (round(max(0, pred_cpu * (1 - cpu_margin)), 4), round(pred_cpu * (1 + cpu_margin), 4)),
            "mem_range_mib": (round(max(0, pred_mem * (1 - mem_margin)), 0), round(pred_mem * (1 + mem_margin), 0))
        }
