from trend_learner.models import OnlineLinearRegressor, EMA

class TrendLearner:
    def __init__(self, use_ema=True):
        self.cpu_model = OnlineLinearRegressor()
        self.mem_model = OnlineLinearRegressor()
        self.use_ema = use_ema
        self.cpu_ema = EMA() if use_ema else None
        self.mem_ema = EMA() if use_ema else None
        
    def update(self, req_rate, timestamp, cpu_usage, mem_usage):
        self.cpu_model.update(req_rate, timestamp, cpu_usage)
        self.mem_model.update(req_rate, timestamp, mem_usage)

        cpu_trend = self.cpu_ema.update(cpu_usage) if self.use_ema else cpu_usage
        mem_trend = self.mem_ema.update(mem_usage) if self.use_ema else mem_usage
        return cpu_trend, mem_trend
    
    def predict_next(self, req_rate, next_time):
        cpu_pred = self.cpu_model.predict(req_rate, next_time)
        mem_pred = self.mem_model.predict(req_rate, next_time)
        return cpu_pred, mem_pred