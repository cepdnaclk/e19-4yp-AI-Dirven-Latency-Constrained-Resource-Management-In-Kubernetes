import numpy as np
from sklearn.linear_model import SGDRegressor
from joblib import dump, load
import sys

class TrendLearner:
    def __init__(self, alpha=0.3):
        self.cpu_model = SGDRegressor(max_iter=1000, tol=1e-3)
        self.mem_model = SGDRegressor(max_iter=1000, tol=1e-3)
        self.alpha = alpha
        self.ema_feature = None  # For storing EMA of inputs
        
    def _apply_ema(self, X):
        if last_X is None:
            return X
        return self.alpha * X + (1 - self.alpha) * last_X
    
    def train(self, X, y_cpu, y_mem):
        for xi, y_cpu_i, y_mem_i in zip(X, y_cpu, y_mem):
            xi = xi.reshape(1, -1)
            xi_ema = self._apply_ema(xi)
            self.cpu_model.partial_fit(xi_ema, [y_cpu_i])
            self.mem_model.partial_fit(xi_ema, [y_mem_i])
            
    def predict_usage(self, X):
        X = self._apply_ema(X)
        return self.cpu_model.predict(X), self.mem_model.predict(X)
    
    def save(self, path):
        dump(self, path)
        
    @staticmethod
    def load(path):
        import dare_tl.model as model_module
        sys.modules['model'] = model_module  # spoof the module path
        return load(path)
    
    def safe_range(self, pred_cpu, pred_mem, cpu_margin=0.1, mem_margin=0.1):
        cpu_min = max(0, pred_cpu * (1 - cpu_margin))
        cpu_max = pred_cpu * (1 + cpu_margin)
        mem_min = max(0, pred_mem * (1 - mem_margin))
        mem_max = pred_mem * (1 + mem_margin)
        return {
            "cpu_range_m": (round(cpu_min), round(cpu_max)),
            "mem_range_mib": (round(mem_min), round(mem_max)),
        }
        
    def partial_fit(self, X, y_cpu, y_mem):
        X = self._apply_ema(X)
        self.cpu_model.partial_fit(X, y_cpu)
        self.mem_model.partial_fit(X, y_mem)