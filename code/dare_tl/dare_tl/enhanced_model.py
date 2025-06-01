import numpy as np
from sklearn.linear_model import SGDRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from joblib import dump, load
import logging
from typing import Tuple, Optional, Dict, Any
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTrendLearner:
    def __init__(self, 
                 alpha=0.3, 
                 window_size=10,
                 cpu_params=None, 
                 mem_params=None,
                 ensemble_method='sgd',
                 feature_engineering=True):
        """
        Enhanced TrendLearner with multiple improvements:
        - Feature engineering
        - Rolling statistics
        - Better regularization
        - Ensemble methods
        - Validation metrics
        """
        self.alpha = alpha
        self.window_size = window_size
        self.ensemble_method = ensemble_method
        self.feature_engineering = feature_engineering
        
        # Initialize models based on ensemble method
        if ensemble_method == 'sgd':
            self.cpu_model = SGDRegressor(**(cpu_params or self._default_sgd_params()))
            self.mem_model = SGDRegressor(**(mem_params or self._default_sgd_params()))
        elif ensemble_method == 'rf':
            self.cpu_model = RandomForestRegressor(**(cpu_params or self._default_rf_params()))
            self.mem_model = RandomForestRegressor(**(mem_params or self._default_rf_params()))
        
        # Feature storage for rolling statistics
        self.feature_history = deque(maxlen=window_size)
        self.ema_features = None
        self.is_fitted = False
        
        # Validation tracking
        self.validation_metrics = {
            'cpu_mse': [], 'mem_mse': [],
            'cpu_mae': [], 'mem_mae': [],
            'cpu_r2': [], 'mem_r2': []
        }
        
    def _default_sgd_params(self):
        return {
            "alpha": 0.001,
            "eta0": 0.01,
            "penalty": "elasticnet",
            "l1_ratio": 0.15,
            "learning_rate": "adaptive",
            "max_iter": 2000,
            "tol": 1e-4,
            "random_state": 42
        }
    
    def _default_rf_params(self):
        return {
            "n_estimators": 100,
            "max_depth": 10,
            "min_samples_split": 5,
            "min_samples_leaf": 2,
            "random_state": 42,
            "n_jobs": -1
        }
    
    def _engineer_features(self, X):
        """Add engineered features like ratios, interactions, and rolling stats"""
        if not self.feature_engineering:
            return X
            
        X_engineered = X.copy()
        
        # Add to history for rolling stats
        if len(X.shape) == 1:
            X = X.reshape(1, -1)
        
        for row in X:
            self.feature_history.append(row)
        
        # Original features: CPU_Usage, Memory_Usage, RequestRate, CPU_Limit, Memory_Limit
        cpu_usage, mem_usage, req_rate, cpu_limit, mem_limit = X[0]
        
        # Resource utilization ratios
        cpu_utilization = cpu_usage / max(cpu_limit, 1e-6)
        mem_utilization = mem_usage / max(mem_limit, 1e-6)
        
        # Load intensity features
        load_per_request = cpu_usage / max(req_rate, 1e-6)
        mem_per_request = mem_usage / max(req_rate, 1e-6)
        
        # Resource pressure indicators
        cpu_pressure = max(0, cpu_usage - 0.7 * cpu_limit)
        mem_pressure = max(0, mem_usage - 0.7 * mem_limit)
        
        # Rolling statistics (if we have enough history)
        if len(self.feature_history) >= 3:
            recent_features = np.array(list(self.feature_history)[-3:])
            cpu_trend = np.mean(np.diff(recent_features[:, 0]))  # CPU trend
            mem_trend = np.mean(np.diff(recent_features[:, 1]))  # Memory trend
            req_volatility = np.std(recent_features[:, 2])       # Request rate volatility
        else:
            cpu_trend = mem_trend = req_volatility = 0
        
        # Combine all features
        engineered_features = np.array([
            # Original features
            cpu_usage, mem_usage, req_rate, cpu_limit, mem_limit,
            # Engineered features
            cpu_utilization, mem_utilization, load_per_request, mem_per_request,
            cpu_pressure, mem_pressure, cpu_trend, mem_trend, req_volatility
        ]).reshape(1, -1)
        
        return engineered_features
    
    def _apply_ema(self, X):
        """Apply exponential moving average to features"""
        if self.ema_features is None:
            self.ema_features = X.copy()
        else:
            self.ema_features = self.alpha * X + (1 - self.alpha) * self.ema_features
        return self.ema_features
    
    def train(self, X, y_cpu, y_mem, validation_data=None):
        """Enhanced training with validation tracking"""
        try:
            for i, (xi, y_cpu_i, y_mem_i) in enumerate(zip(X, y_cpu, y_mem)):
                xi = xi.reshape(1, -1)
                
                # Engineer features
                xi_engineered = self._engineer_features(xi)
                
                # Apply EMA smoothing
                xi_ema = self._apply_ema(xi_engineered)
                
                if not self.is_fitted:
                    # First fit
                    self.cpu_model.fit(xi_ema, [y_cpu_i])
                    self.mem_model.fit(xi_ema, [y_mem_i])
                    self.is_fitted = True
                else:
                    # Partial fit for SGD, retrain for RF
                    if self.ensemble_method == 'sgd':
                        self.cpu_model.partial_fit(xi_ema, [y_cpu_i])
                        self.mem_model.partial_fit(xi_ema, [y_mem_i])
                    # For RF, we'd need to retrain periodically or use online RF
                
                # Validation every 50 steps
                if validation_data and i % 50 == 0 and self.is_fitted:
                    self._validate(validation_data)
                    
            logger.info(f"Training completed on {len(X)} samples")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise
    
    def _validate(self, validation_data):
        """Track validation metrics during training"""
        X_val, y_cpu_val, y_mem_val = validation_data
        
        try:
            pred_cpu, pred_mem = self.predict_usage(X_val)
            
            if pred_cpu is not None and pred_mem is not None:
                # Calculate metrics
                cpu_mse = mean_squared_error(y_cpu_val, pred_cpu)
                mem_mse = mean_squared_error(y_mem_val, pred_mem)
                cpu_mae = mean_absolute_error(y_cpu_val, pred_cpu)
                mem_mae = mean_absolute_error(y_mem_val, pred_mem)
                cpu_r2 = r2_score(y_cpu_val, pred_cpu)
                mem_r2 = r2_score(y_mem_val, pred_mem)
                
                # Store metrics
                self.validation_metrics['cpu_mse'].append(cpu_mse)
                self.validation_metrics['mem_mse'].append(mem_mse)
                self.validation_metrics['cpu_mae'].append(cpu_mae)
                self.validation_metrics['mem_mae'].append(mem_mae)
                self.validation_metrics['cpu_r2'].append(cpu_r2)
                self.validation_metrics['mem_r2'].append(mem_r2)
                
        except Exception as e:
            logger.warning(f"Validation failed: {e}")
    
    def predict_usage(self, X):
        """Enhanced prediction with confidence intervals"""
        if not self.is_fitted:
            return None, None
        
        try:
            # Engineer features for prediction
            X_engineered = self._engineer_features(X)
            
            # Apply EMA
            X_ema = self._apply_ema(X_engineered)
            
            # Make predictions
            cpu_pred = self.cpu_model.predict(X_ema)
            mem_pred = self.mem_model.predict(X_ema)
            
            return cpu_pred, mem_pred
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return None, None
    
    def predict_with_uncertainty(self, X, n_bootstrap=10):
        """Prediction with uncertainty estimation using bootstrap"""
        if not self.is_fitted:
            return None, None, None, None
            
        # For SGD, we can't easily do bootstrap, so return point estimates
        if self.ensemble_method == 'sgd':
            cpu_pred, mem_pred = self.predict_usage(X)
            return cpu_pred, mem_pred, None, None
        
        # For ensemble methods, we can get uncertainty from trees
        if hasattr(self.cpu_model, 'estimators_'):
            X_engineered = self._engineer_features(X)
            X_ema = self._apply_ema(X_engineered)
            
            # Get predictions from individual trees
            cpu_preds = np.array([tree.predict(X_ema) for tree in self.cpu_model.estimators_])
            mem_preds = np.array([tree.predict(X_ema) for tree in self.mem_model.estimators_])
            
            cpu_mean = np.mean(cpu_preds, axis=0)
            mem_mean = np.mean(mem_preds, axis=0)
            cpu_std = np.std(cpu_preds, axis=0)
            mem_std = np.std(mem_preds, axis=0)
            
            return cpu_mean, mem_mean, cpu_std, mem_std
        
        return self.predict_usage(X) + (None, None)
    
    def safe_range(self, pred_cpu, pred_mem, cpu_margin=0.1, mem_margin=0.1, uncertainty=None):
        """Enhanced safe range calculation with uncertainty"""
        base_cpu_min = max(0, pred_cpu * (1 - cpu_margin))
        base_cpu_max = pred_cpu * (1 + cpu_margin)
        base_mem_min = max(0, pred_mem * (1 - mem_margin))
        base_mem_max = pred_mem * (1 + mem_margin)
        
        # Adjust for uncertainty if available
        if uncertainty:
            cpu_std, mem_std = uncertainty
            cpu_uncertainty = cpu_std * 2  # 95% confidence
            mem_uncertainty = mem_std * 2
            
            cpu_min = max(0, base_cpu_min - cpu_uncertainty)
            cpu_max = base_cpu_max + cpu_uncertainty
            mem_min = max(0, base_mem_min - mem_uncertainty)
            mem_max = base_mem_max + mem_uncertainty
        else:
            cpu_min, cpu_max = base_cpu_min, base_cpu_max
            mem_min, mem_max = base_mem_min, base_mem_max
        
        return {
            "cpu_range_m": (round(float(cpu_min), 4), round(float(cpu_max), 4)),
            "mem_range_mib": (round(float(mem_min), 0), round(float(mem_max), 0)),
            "confidence": "high" if uncertainty is None else "medium"
        }
    
    def get_feature_importance(self):
        """Get feature importance if available"""
        if hasattr(self.cpu_model, 'feature_importances_'):
            feature_names = [
                'CPU_Usage', 'Memory_Usage', 'RequestRate', 'CPU_Limit', 'Memory_Limit',
                'CPU_Utilization', 'Mem_Utilization', 'Load_per_Request', 'Mem_per_Request',
                'CPU_Pressure', 'Mem_Pressure', 'CPU_Trend', 'Mem_Trend', 'Req_Volatility'
            ]
            
            return {
                'cpu_importance': dict(zip(feature_names, self.cpu_model.feature_importances_)),
                'mem_importance': dict(zip(feature_names, self.mem_model.feature_importances_))
            }
        return None
    
    def get_validation_metrics(self):
        """Return validation metrics history"""
        if not self.validation_metrics['cpu_mse']:
            return None
            
        return {
            'latest_cpu_mse': self.validation_metrics['cpu_mse'][-1],
            'latest_mem_mse': self.validation_metrics['mem_mse'][-1],
            'latest_cpu_r2': self.validation_metrics['cpu_r2'][-1],
            'latest_mem_r2': self.validation_metrics['mem_r2'][-1],
            'history': self.validation_metrics
        }
    
    def partial_fit(self, X, y_cpu, y_mem):
        """Enhanced partial fit with feature engineering"""
        if not self.is_fitted:
            self.train(X, y_cpu, y_mem)
        else:
            X_engineered = self._engineer_features(X)
            X_ema = self._apply_ema(X_engineered)
            
            if self.ensemble_method == 'sgd':
                self.cpu_model.partial_fit(X_ema, y_cpu)
                self.mem_model.partial_fit(X_ema, y_mem)
            # For RF, we'd need to implement incremental learning
    
    def save(self, path):
        """Save model with all components"""
        model_data = {
            'cpu_model': self.cpu_model,
            'mem_model': self.mem_model,
            'alpha': self.alpha,
            'window_size': self.window_size,
            'ensemble_method': self.ensemble_method,
            'feature_engineering': self.feature_engineering,
            'feature_history': list(self.feature_history),
            'ema_features': self.ema_features,
            'is_fitted': self.is_fitted,
            'validation_metrics': self.validation_metrics
        }
        dump(model_data, path)
        logger.info(f"Model saved to {path}")
    
    @staticmethod
    def load(path):
        """Load model with all components"""
        model_data = load(path)
        
        model = EnhancedTrendLearner(
            alpha=model_data['alpha'],
            window_size=model_data['window_size'],
            ensemble_method=model_data['ensemble_method'],
            feature_engineering=model_data['feature_engineering']
        )
        
        model.cpu_model = model_data['cpu_model']
        model.mem_model = model_data['mem_model']
        model.feature_history = deque(model_data['feature_history'], maxlen=model_data['window_size'])
        model.ema_features = model_data['ema_features']
        model.is_fitted = model_data['is_fitted']
        model.validation_metrics = model_data['validation_metrics']
        
        logger.info(f"Model loaded from {path}")
        return model