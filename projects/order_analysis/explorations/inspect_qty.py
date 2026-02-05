import pandas as pd
import os

base_dir = os.getcwd()
data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")

print(f"Loading {data_path}...")
df = pd.read_excel(data_path, usecols=['销售数量', '商品名称', '单位'] if '单位' in pd.read_excel(data_path, nrows=1).columns else ['销售数量', '商品名称'])
# Checking if '单位' exists? No, it wasn't in the column list earlier.

print(df['销售数量'].describe())
print("\nTop 10 items by quantity:")
print(df.sort_values('销售数量', ascending=False).head(10))