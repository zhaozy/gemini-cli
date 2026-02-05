import pandas as pd
import os
import sys

# Add root to sys.path to ensure we can import if needed, though not strictly necessary for this script
sys.path.append(os.getcwd())

# Define path
# Assuming we run from root, but let's be robust
# File is at order_analysis/explorations/inspect_data.py
# Data is at order_analysis/datas/
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_path = os.path.join(base_dir, "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")

print(f"Loading: {data_path}")

try:
    # Attempt to read
    df = pd.read_excel(data_path, nrows=5)
    
    print("\n=== Data Info ===")
    print(f"Columns: {df.columns.tolist()}")
    
    print("\n=== Sample Data ===")
    print(df.head(3).T)  # Transpose for easier reading of many columns
    
except Exception as e:
    print(f"Error loading data: {e}")
