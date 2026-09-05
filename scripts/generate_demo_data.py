from pathlib import Path

import numpy as np
import pandas as pd

Path("data").mkdir(exist_ok=True)
np.random.seed(42)
df = pd.DataFrame(
    {
        "ma_sv": [f"SV{i:04d}" for i in range(1, 301)],
        "diem": np.random.normal(6.5, 1.8, 300).clip(0, 10),
        "lop": np.random.choice(["L01", "L02", "L03"], 300),
        "gio_hoc": np.random.exponential(5, 300).clip(0, 20),
    }
)
# Inject issues
idx = np.random.choice(300, 20, replace=False)
df.loc[idx, "diem"] = np.nan
df = pd.concat([df, df.sample(10)], ignore_index=True)  # duplicates
df.loc[np.random.choice(len(df), 5), "diem"] = 15  # outliers
df.to_csv("data/demo_sinhvien.csv", index=False)
print("Generated data/demo_sinhvien.csv", len(df))
