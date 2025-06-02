# enhanced_tuning.py
import optuna
from sklearn.model_selection import TimeSeriesSplit

def objective(trial):
    params = {
        'ema_alpha': trial.suggest_float('ema_alpha', 0.1, 0.9),
        'window_size': trial.suggest_int('window_size', 10, 30),
        'n_estimators': trial.suggest_int('n_estimators', 200, 500),
        'max_depth': trial.suggest_int('max_depth', 15, 30),
        'min_samples_split': trial.suggest_int('min_samples_split', 2, 10),
        'min_samples_leaf': trial.suggest_int('min_samples_leaf', 1, 4),
        'max_features': trial.suggest_categorical('max_features', ['sqrt', 'log2', 0.8])
    }
    
    model = EnhancedTrendLearner(**params)
    tscv = TimeSeriesSplit(n_splits=5)
    scores = []
    
    for train_idx, val_idx in tscv.split(X):
        X_train, X_val = X[train_idx], X[val_idx]
        y_train, y_val = y[train_idx], y[val_idx]
        
        model.train(X_train, y_train)
        pred = model.predict(X_val)
        scores.append(r2_score(y_val, pred))
    
    return np.mean(scores)

def optimize():
    study = optuna.create_study(direction='maximize')
    study.optimize(objective, n_trials=100, timeout=3600)
    
    logger.info(f"Best params: {study.best_params}")
    logger.info(f"Best R²: {study.best_value:.4f}")
    
    return study.best_params
