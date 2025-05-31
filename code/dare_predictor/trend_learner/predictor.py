def suggest_safe_range(predicted_value, tolerance_pct=20):
    lower = predicted_value * (1 + -tolerance_pct / 100)
    upper = predicted_value * (1 + tolerance_pct / 100)
    return round(lower, 2), round(upper, 2)