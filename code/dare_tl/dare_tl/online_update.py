from .model import TrendLearner
import numpy as np

def update_model_online(model_path, new_data_point):
    model = TrendLearner.load(model_path)

    X = np.array([[
        new_data_point["CPU_Usage"],
        new_data_point["Memory_Usage"],
        new_data_point["RequestRate"],
        new_data_point["CPU_Limit"],
        new_data_point["Memory_Limit"]
    ]])

    y_cpu = np.array([new_data_point["CPU_Usage_Delta"]])
    y_mem = np.array([new_data_point["Memory_Usage_Delta"]])

    model.partial_fit(X, y_cpu, y_mem)
    model.save(model_path)
