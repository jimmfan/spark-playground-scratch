import pandas as pd
import numpy as np

# Example data
df = pd.DataFrame({
    "event_flag": np.random.choice([0, 1], size=10000, p=[0.9, 0.1]),
    "event_date": pd.date_range("2024-01-01", periods=10000, freq="H"),
    "amount": np.random.rand(10000) * 1000,
})

# Split events vs non-events
events = df.query("event_flag == 1")
non_events = df.query("event_flag == 0")

# Sample ~50% of non-events (you can adjust the fraction)
non_events_sampled = non_events.sample(frac=0.5, random_state=42)

# Combine back together
sampled_df = pd.concat([events, non_events_sampled], ignore_index=True)
