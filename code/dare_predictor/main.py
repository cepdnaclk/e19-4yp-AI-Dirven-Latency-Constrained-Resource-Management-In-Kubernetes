import time
import random
from trend_learner.trainer import TrendLearner
from trend_learner.predictor import get_safe_resource_ranges

# Simulate live streaming metrics
req_rate = 300
tl = TrendLearner()

for t in range(1, 11):  # Simulate 10 intervals
    cpu = 250 + random.randint(-10, 10)  # Slight noise
    mem = 500 + t * 2  # Slowly increasing memory

    cpu_trend, mem_trend = tl.update(req_rate, t, cpu, mem)
    cpu_pred, mem_pred = tl.predict_next(req_rate, t + 1)
    ranges = get_safe_resource_ranges(cpu_pred, mem_pred)

    print(f"Time {t}: CPU={cpu}, MEM={mem}")
    print(f"→ Forecast: CPU={int(cpu_pred)}m, MEM={int(mem_pred)}Mi")
    print(f"→ Suggested Ranges: {ranges}")
    time.sleep(0.5)
