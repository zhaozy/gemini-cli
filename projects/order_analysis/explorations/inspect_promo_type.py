import pandas as pd
import os
import sys

# Setup path
sys.path.append(os.getcwd())
from order_analysis.src.dal import DataLoader

base_dir = os.getcwd()
data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")

loader = DataLoader(data_path)
df = loader.load()

print("\n=== 折扣类型分布 ===")
print(df['折扣类型'].value_counts(dropna=False))

print("\n=== 折扣类型 x 折扣金额 (均值) ===")
print(df.groupby('折扣类型')['折扣金额'].describe())
