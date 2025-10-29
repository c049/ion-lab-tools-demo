import pandas as pd

REQUIRED = ["timestamp","rb_fidelity","rabi_freq","lock_error","temperature"]

def load_csv(path):
    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns: {missing}")
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df
