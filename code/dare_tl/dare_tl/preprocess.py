import pandas as pd

def load_and_preprocess(path):
    df = pd.read_csv(path, parse_dates=["Timestamp"])
    df = df.sort_values("Timestamp")

    df["CPU_Usage_Delta"] = df["CPU Usage"].diff().fillna(0)
    df["Memory_Usage_Delta"] = df["Memory Usage"].diff().fillna(0)
    df["RequestRate_Delta"] = df["Request Rate"].diff().fillna(0)

    df = df.dropna()
    return df
