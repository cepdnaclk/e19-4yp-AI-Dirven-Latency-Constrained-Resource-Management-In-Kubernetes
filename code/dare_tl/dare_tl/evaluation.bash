python -c "
from model import TrendLearner
from preprocess import load_and_preprocess
import joblib
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error

# Load data and model
df = load_and_preprocess('data/resource_usage.csv')
model = TrendLearner.load('models/tl_model.pkl')
scaler = joblib.load('models/scaler.pkl')

# Use last 20% as test set
test_start = int(len(df) * 0.8)
test_df = df[test_start:]

X_test = test_df[['CPU_Usage', 'Memory_Usage', 'RequestRate', 'CPU_Limit', 'Memory_Limit']].values
y_cpu_test = test_df['CPU_Usage_Delta'].values
y_mem_test = test_df['Memory_Usage_Delta'].values
X_test_scaled = scaler.transform(X_test)

pred_cpu, pred_mem = model.predict_usage(X_test_scaled)

print(f'CPU MAE: {mean_absolute_error(y_cpu_test, pred_cpu):.6f}')
print(f'Memory MAE: {mean_absolute_error(y_mem_test, pred_mem):.1f} bytes')
print(f'CPU RMSE: {np.sqrt(mean_squared_error(y_cpu_test, pred_cpu)):.6f}')
print(f'Memory RMSE: {np.sqrt(mean_squared_error(y_mem_test, pred_mem)):.1f} bytes')
"