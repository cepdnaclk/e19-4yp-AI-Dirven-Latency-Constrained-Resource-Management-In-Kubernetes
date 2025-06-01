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
        try:
            import dare_tl.model as model_module
            sys.modules['model'] = model_module  # spoof the module path
        except ImportError:
            pass  # Module might not exist in package structure
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
        """Update model with new data point"""
        if not self.is_fitted:
            # If not fitted yet, use regular fit
            self.train(X, y_cpu, y_mem)
        else:
            X_ema = self._apply_ema(X)
            self.cpu_model.partial_fit(X_ema, y_cpu)
            self.mem_model.partial_fit(X_ema, y_mem)