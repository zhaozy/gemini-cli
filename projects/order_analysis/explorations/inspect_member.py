import pandas as pd
import os
import sys

# Setup path
sys.path.append(os.getcwd())
from order_analysis.src.dal import DataLoader

# Load data
base_dir = os.getcwd()
data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")

try:
    loader = DataLoader(data_path)
    df = loader.load() # This already filters service fees
    
    print("\n=== 会员数据质量 ===")
    total = len(df)
    has_member = df['会员id'].notnull().sum()
    unique_members = df['会员id'].nunique()
    
    print(f"Total Rows: {total}")
    print(f"Rows with Member ID: {has_member} ({has_member/total:.1%})")
    print(f"Unique Member IDs: {unique_members}")
    
    if unique_members > 0:
        # 简单看下复购分布
        orders_per_member = df.groupby('会员id')['流水单号'].nunique()
        print("\nOrders per Member stats:")
        print(orders_per_member.describe())
        
except Exception as e:
    print(e)
