import pandas as pd
import os
import sys

# Setup path
sys.path.append(os.getcwd())
from order_analysis.src.dal import DataLoader

# Load raw data (without filtering first to see what's there)
base_dir = os.getcwd()
data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")

print("Loading raw data...")
df = pd.read_excel(data_path)
df.columns = [c.strip() for c in df.columns]

# Filter for suspicious names
keywords = ['费', '打包', '服务', '袋']
mask = df['商品名称'].apply(lambda x: any(k in str(x) for k in keywords))
suspicious = df[mask]

print("\n=== 疑似非商品项统计 ===")
stats = suspicious.groupby('商品名称').agg({
    '销售数量': ['sum', 'mean', 'max'],
    '销售金额': 'sum'
}).sort_values(('销售数量', 'sum'), ascending=False)

print(stats)
