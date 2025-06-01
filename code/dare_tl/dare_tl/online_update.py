from .model import TrendLearner
import numpy as np

def update_model_online(model_path, scaler_path, new_data_point):
    """
    Update the model with a new data point online
    
    Args:
        model_path: Path to the saved model
        scaler_path: Path to the saved scaler
        new_data_point: Dictionary with keys matching your CSV columns
    """
    try:
        # Load model and scaler
        model = TrendLearner.load(model_path)
        scaler = joblib.load(scaler_path)
        
        # Prepare input features in the correct order
        X = np.array([[
            new_data_point["CPU_Usage"],
            new_data_point["Memory_Usage"], 
            new_data_point["RequestRate"],
            new_data_point["CPU_Limit"],
            new_data_point["Memory_Limit"]
        ]])
        
        # Scale the features
        X_scaled = scaler.transform(X)
        
        # Target values (deltas)
        y_cpu = np.array([new_data_point["CPU_Usage_Delta"]])
        y_mem = np.array([new_data_point["Memory_Usage_Delta"]])
        
        # Update model
        model.partial_fit(X_scaled, y_cpu, y_mem)
        
        # Save updated model
        model.save(model_path)
        
        print(f"Model updated successfully with new data point")
        return True
        
    except Exception as e:
        print(f"Error updating model: {e}")
        return False
    
def update_model_batch(model_path, scaler_path, new_data_points):
    """
    Update the model with multiple new data points
    
    Args:
        model_path: Path to the saved model
        scaler_path: Path to the saved scaler  
        new_data_points: List of dictionaries with new data
    """
    try:
        model = TrendLearner.load(model_path)
        scaler = joblib.load(scaler_path)
        
        for data_point in new_data_points:
            X = np.array([[
                data_point["CPU_Usage"],
                data_point["Memory_Usage"],
                data_point["RequestRate"], 
                data_point["CPU_Limit"],
                data_point["Memory_Limit"]
            ]])
            
            X_scaled = scaler.transform(X)
            y_cpu = np.array([data_point["CPU_Usage_Delta"]])
            y_mem = np.array([data_point["Memory_Usage_Delta"]])
            
            model.partial_fit(X_scaled, y_cpu, y_mem)
        
        model.save(model_path)
        print(f"Model updated with {len(new_data_points)} new data points")
        return True
        
    except Exception as e:
        print(f"Error in batch update: {e}")
        return False
