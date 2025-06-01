import numpy as np
from sklearn.linear_model import SGDRegressor
from joblib import dump, load

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
            self.cpu_model.partial_fit(xi_ema, [y_cpu_i])
            self.mem_model.partial_fit(xi_ema, [y_mem_i])
            
    def predict_usage(self, X):
        X = self._apply_ema(X)
        return self.cpu_model.predict(X), self.mem_model.predict(X)
    
    def save(self, path):
        dump(self, path)