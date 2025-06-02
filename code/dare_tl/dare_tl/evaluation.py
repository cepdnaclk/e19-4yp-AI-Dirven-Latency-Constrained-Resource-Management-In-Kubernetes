from model import TrendLearner
import joblib
import numpy as np

model_path = "./models/tl_model.pkl"
scaler_path = "./models/scaler.pkl"

model = TrendLearner.load(model_path)
scaler = joblib.load(scaler_path)
