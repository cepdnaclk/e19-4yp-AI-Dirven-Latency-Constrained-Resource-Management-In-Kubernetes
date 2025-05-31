from trend_learner.models import OnlineLinearRegressor, EMA

class TrendLearner:
    def __init__(self, use_ema=True):
        self.cpu_model = OnlineLinearRegressor()
        self.mem_model = OnlineLinearRegressor()
        self.use_ema = use_ema
        self.cpu_ema = EMA() if use_ema else None
        self.mem_ema = EMA() if use_ema else None