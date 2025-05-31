def moving_average(values, alpha=0.3):
    smoothed = []
    last = None
    for val in values:
        if last is None:
            last = val
        else:
            last = alpha * val + (1 - alpha) * last
        smoothed.append(last)
    return smoothed
