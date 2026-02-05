import pandas as pd
import os
import sys

# Setup path
sys.path.append(os.getcwd())
from order_analysis.src.dal import DataLoader

# Load data
base_dir = os.getcwd()
data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")
loader = DataLoader(data_path)
df = loader.load()

print("\n=== 渠道分布 ===")
print(df['平台触点名称'].value_counts(dropna=False))

print("\n=== 渠道 x 交易时间 (Sample) ===")
print(df[['平台触点名称', '交易时间']].head())
