def suggest_safe_range(predicted_value, tolerance_pct=20):
    lower = predicted_value * (1 + -tolerance_pct / 100)
    upper = predicted_value * (1 + tolerance_pct / 100)
    return round(lower, 2), round(upper, 2)

def get_safe_resource_ranges(cpu_pred, mem_pred):
    cpu_min, cpu_max = suggest_safe_range(cpu_pred)
    mem_min, mem_max = suggest_safe_range(mem_pred)
    return {
        "cpu_millicores": {"min": int(cpu_min), "max": int(cpu_max)},
        "memory_mib": {"min": int(mem_min), "max": int(mem_max)}
    }