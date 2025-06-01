from dare_tl.preprocess import load_and_preprocess
from dare_tl.model import TrendLearner
import numpy as np

df = load_and_preprocess("data/resource_usage.csv")

features = df[[ "CPU Limit", "Memory Limit", "CPU Usage", "Memory Usage", "Request Rate"]].values
y_cpu = df["CPU_Usage_Delta"].values
y_mem = df["Memory_Usage_Delta"].values

tl = TrendLearner()
tl.train(features, y_cpu, y_mem)
tl.save("models/tl_model.pkl")
print("Offline training complete and model saved.")
