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