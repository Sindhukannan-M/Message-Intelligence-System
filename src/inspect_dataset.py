import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
data_path = ROOT / "data" / "raw" / "messages.csv"

df = pd.read_csv(data_path)