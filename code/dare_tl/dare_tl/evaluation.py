import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import matplotlib.pyplot as plt
from preprocess import load_and_preprocess
from model import TrendLearner
import joblib

def calculate_accuracy_metrics(y_true, y_pred, metric_name=""):
    """Calculate various accuracy metrics"""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    
    # Mean Absolute Percentage Error (MAPE)
    mape = np.mean(np.abs((y_true - y_pred) / np.maximum(np.abs(y_true), 1e-8))) * 100
    
    # R² Score
    r2 = r2_score(y_true, y_pred)
    
    # Custom accuracy (percentage of predictions within acceptable range)
    tolerance = 0.1  # 10% tolerance
    within_tolerance = np.mean(np.abs(y_true - y_pred) <= tolerance * np.abs(y_true)) * 100
    
    return {
        f'{metric_name}_MAE': mae,
        f'{metric_name}_MSE': mse,
        f'{metric_name}_RMSE': rmse,
        f'{metric_name}_MAPE': mape,
        f'{metric_name}_R2': r2,
        f'{metric_name}_Accuracy_10pct': within_tolerance
    }

def evaluate_model_holdout(train_ratio=0.8):
    """Evaluate model using train/test split"""
    # Load data
    df = load_and_preprocess("data/resource_usage.csv")
    
    # Split data
    split_idx = int(len(df) * train_ratio)
    train_df = df[:split_idx]
    test_df = df[split_idx:]
    
    print(f"Training samples: {len(train_df)}")
    print(f"Testing samples: {len(test_df)}")
    
    # Prepare training data
    X_train = train_df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu_train = train_df["CPU_Usage_Delta"].values
    y_mem_train = train_df["Memory_Usage_Delta"].values
    
    # Scale features
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    # Train model
    model = TrendLearner()
    model.train(X_train_scaled, y_cpu_train, y_mem_train)
    
    # Prepare test data
    X_test = test_df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu_test = test_df["CPU_Usage_Delta"].values
    y_mem_test = test_df["Memory_Usage_Delta"].values
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    pred_cpu, pred_mem = model.predict_usage(X_test_scaled)
    
    # Calculate metrics
    cpu_metrics = calculate_accuracy_metrics(y_cpu_test, pred_cpu, "CPU")
    mem_metrics = calculate_accuracy_metrics(y_mem_test, pred_mem, "Memory")
    
    return {**cpu_metrics, **mem_metrics}, (y_cpu_test, pred_cpu, y_mem_test, pred_mem)

def evaluate_model_timeseries():
    """Evaluate model using time series validation (more realistic)"""
    df = load_and_preprocess("data/resource_usage.csv")
    
    # Use first 70% for training, next 20% for validation, last 10% for testing
    n = len(df)
    train_end = int(n * 0.7)
    val_end = int(n * 0.9)
    
    train_df = df[:train_end]
    val_df = df[train_end:val_end]
    test_df = df[val_end:]
    
    print(f"Train: {len(train_df)}, Validation: {len(val_df)}, Test: {len(test_df)}")
    
    # Train model
    X_train = train_df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu_train = train_df["CPU_Usage_Delta"].values
    y_mem_train = train_df["Memory_Usage_Delta"].values
    
    from sklearn.preprocessing import StandardScaler
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    
    model = TrendLearner()
    model.train(X_train_scaled, y_cpu_train, y_mem_train)
    
    # Test on validation set
    X_val = val_df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu_val = val_df["CPU_Usage_Delta"].values
    y_mem_val = val_df["Memory_Usage_Delta"].values
    X_val_scaled = scaler.transform(X_val)
    
    pred_cpu_val, pred_mem_val = model.predict_usage(X_val_scaled)
    
    # Calculate validation metrics
    cpu_metrics = calculate_accuracy_metrics(y_cpu_val, pred_cpu_val, "CPU_Val")
    mem_metrics = calculate_accuracy_metrics(y_mem_val, pred_mem_val, "Memory_Val")
    
    return {**cpu_metrics, **mem_metrics}, model, scaler

def evaluate_existing_model():
    """Evaluate your already trained model"""
    # Load test data (use recent portion of data as test set)
    df = load_and_preprocess("data/resource_usage.csv")
    
    # Use last 20% as test set
    test_start = int(len(df) * 0.8)
    test_df = df[test_start:]
    
    # Load your trained model and scaler
    model = TrendLearner.load("models/tl_model.pkl")
    scaler = joblib.load("models/scaler.pkl")
    
    # Prepare test data
    X_test = test_df[["CPU_Usage", "Memory_Usage", "RequestRate", "CPU_Limit", "Memory_Limit"]].values
    y_cpu_test = test_df["CPU_Usage_Delta"].values
    y_mem_test = test_df["Memory_Usage_Delta"].values
    X_test_scaled = scaler.transform(X_test)
    
    # Make predictions
    pred_cpu, pred_mem = model.predict_usage(X_test_scaled)
    
    # Calculate metrics
    cpu_metrics = calculate_accuracy_metrics(y_cpu_test, pred_cpu, "CPU")
    mem_metrics = calculate_accuracy_metrics(y_mem_test, pred_mem, "Memory")
    
    return {**cpu_metrics, **mem_metrics}

def plot_predictions(y_true_cpu, pred_cpu, y_true_mem, pred_mem):
    """Plot actual vs predicted values"""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # CPU predictions
    ax1.scatter(y_true_cpu, pred_cpu, alpha=0.6)
    ax1.plot([y_true_cpu.min(), y_true_cpu.max()], [y_true_cpu.min(), y_true_cpu.max()], 'r--', lw=2)
    ax1.set_xlabel('Actual CPU Delta')
    ax1.set_ylabel('Predicted CPU Delta')
    ax1.set_title('CPU Delta: Actual vs Predicted')
    ax1.grid(True)
    
    # Memory predictions
    ax2.scatter(y_true_mem, pred_mem, alpha=0.6)
    ax2.plot([y_true_mem.min(), y_true_mem.max()], [y_true_mem.min(), y_true_mem.max()], 'r--', lw=2)
    ax2.set_xlabel('Actual Memory Delta')
    ax2.set_ylabel('Predicted Memory Delta')
    ax2.set_title('Memory Delta: Actual vs Predicted')
    ax2.grid(True)
    
    plt.tight_layout()
    plt.savefig('model_predictions.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("=== Evaluating Existing Model ===")
    try:
        metrics = evaluate_existing_model()
        print("\nModel Performance Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        print("\n=== Interpretation Guide ===")
        print("MAE (Mean Absolute Error): Lower is better, shows average prediction error")
        print("RMSE (Root Mean Square Error): Lower is better, penalizes large errors more")
        print("MAPE (Mean Absolute Percentage Error): Lower is better, shows error as percentage")
        print("R² Score: Higher is better (max 1.0), shows how well model explains variance")
        print("Accuracy_10pct: Higher is better, % of predictions within 10% tolerance")
        
    except Exception as e:
        print(f"Error evaluating existing model: {e}")
        print("Make sure you have trained the model first by running train_offline.py")
    
    print("\n=== Running Holdout Validation ===")
    try:
        metrics, predictions = evaluate_model_holdout()
        print("\nHoldout Validation Metrics:")
        for metric, value in metrics.items():
            print(f"{metric}: {value:.4f}")
        
        # Plot results
        y_cpu_test, pred_cpu, y_mem_test, pred_mem = predictions
        plot_predictions(y_cpu_test, pred_cpu, y_mem_test, pred_mem)
        
    except Exception as e:
        print(f"Error in holdout validation: {e}")