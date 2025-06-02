# enhanced_model.py
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
from joblib import dump, load
import logging
from collections import deque

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedTrendLearner:
    def __init__(self, 
                 ema_alpha=0.263,
                 window_size=15,
                 feature_engineering=True,
                 n_estimators=300,  # Increased from 170
                 max_depth=20,      # Increased from 10
                 min_samples_split=6,
                 min_samples_leaf=1,  # Reduced from 4
                 max_features='sqrt'):
        
        self.feature_engineering = feature_engineering
        self.window_size = window_size
        self.feature_history = deque(maxlen=window_size)
        
        # Optimized Random Forest parameters
        self.cpu_model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            random_state=42,
            n_jobs=-1
        )
        
        self.mem_model = RandomForestRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            min_samples_split=min_samples_split,
            min_samples_leaf=min_samples_leaf,
            max_features=max_features,
            random_state=42,
            n_jobs=-1
        )

    def _engineer_features(self, X):
        """Enhanced feature engineering with temporal features"""
        if not self.feature_engineering:
            return X
            
        X_engineered = X.copy()
        self.feature_history.append(X_engineered[0])
        
        # Base features
        cpu_usage, mem_usage, req_rate, cpu_limit, mem_limit = X_engineered[0]
        
        # Temporal features
        temporal_features = []
        if len(self.feature_history) >= 3:
            recent = np.array(list(self.feature_history)[-3:])
            temporal_features.extend([
                np.mean(np.diff(recent[:, 0])),  # CPU trend
                np.mean(np.diff(recent[:, 1])),  # Memory trend
                np.std(recent[:, 2]),            # Request volatility
                np.mean(recent[:, 0])            # 3-period CPU mean
            ])
        
        # Resource pressure features
        pressure_features = [
            max(0, cpu_usage - 0.7 * cpu_limit),
            max(0, mem_usage - 0.7 * mem_limit),
            cpu_usage / max(cpu_limit, 1e-6),
            mem_usage / max(mem_limit, 1e-6)
        ]
        
        # Combine all features
        return np.concatenate([
            X_engineered,
            np.array(pressure_features).reshape(1, -1),
            np.array(temporal_features).reshape(1, -1) if temporal_features else np.zeros((1,4))
        ], axis=1)

    def train(self, X, y_cpu, y_mem):
        """Enhanced training with temporal cross-validation"""
        try:
            # Temporal split validation
            train_size = int(len(X) * 0.8)
            X_train, X_val = X[:train_size], X[train_size:]
            y_cpu_train, y_cpu_val = y_cpu[:train_size], y_cpu[train_size:]
            y_mem_train, y_mem_val = y_mem[:train_size], y_mem[train_size:]
            
            # Feature engineering
            X_train_fe = np.array([self._engineer_features(x.reshape(1,-1))[0] for x in X_train])
            X_val_fe = np.array([self._engineer_features(x.reshape(1,-1))[0] for x in X_val])
            
            # Train models
            self.cpu_model.fit(X_train_fe, y_cpu_train)
            self.mem_model.fit(X_train_fe, y_mem_train)
            
            # Validate
            cpu_pred = self.cpu_model.predict(X_val_fe)
            mem_pred = self.mem_model.predict(X_val_fe)
            
            logger.info(f"Validation Metrics:")
            logger.info(f"CPU R²: {r2_score(y_cpu_val, cpu_pred):.4f}")
            logger.info(f"Memory R²: {r2_score(y_mem_val, mem_pred):.4f}")
            
        except Exception as e:
            logger.error(f"Training failed: {e}")
            raise

    def predict_usage(self, X):
        """Predict with engineered features"""
        X_fe = np.array([self._engineer_features(x.reshape(1,-1))[0] for x in X])
        return self.cpu_model.predict(X_fe), self.mem_model.predict(X_fe)

    def get_feature_importance(self):
        """Get enhanced feature importance"""
        feature_names = [
            'CPU_Usage', 'Memory_Usage', 'RequestRate', 'CPU_Limit', 'Memory_Limit',
            'CPU_Pressure', 'Mem_Pressure', 'CPU_Utilization', 'Mem_Utilization',
            'CPU_Trend', 'Mem_Trend', 'Req_Volatility', 'CPU_3MA'
        ]
        return {
            'cpu_importance': dict(zip(feature_names, self.cpu_model.feature_importances_)),
            'mem_importance': dict(zip(feature_names, self.mem_model.feature_importances_))
        }

