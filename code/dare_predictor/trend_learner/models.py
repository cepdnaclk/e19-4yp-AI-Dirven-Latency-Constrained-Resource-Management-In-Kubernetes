import numpy as np

class OnlineLinearRegressor:
    def __init__(self, learning_rate=0.001):
        self.weights = np.zeros(3)  # [bias, req_rate, time]
        self.learning_rate = learning_rate
        
    def predict(self, req_rate, t):
        x = np.array([1, req_rate, t])
        return np.dot(self.weights, x)
    
    def update(self, req_rate, t, usage):
        x = np.array([1, req_rate, t])
        y_pred = np.dot(self.weights, x)
        error = usage - y_pred
        self.weights += self.learning_rate * error * x