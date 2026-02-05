import pandas as pd
import os
from typing import Optional
from order_analysis.src.contracts import TransactionSchema

class DataLoader:
    """
    负责加载和清洗交易流水数据。
    """
    
    # 需要从实物销售分析中剔除的非商品项
    EXCLUDE_SKU_NAMES = [
        "送货服务费",
        "润之家打包袋",
        "线上业务退货上门取货费"
    ]

    COLUMN_MAP = {
        " 小类编码": "小类编码"
    }

    def __init__(self, data_path: str):
        self.data_path = data_path

    def load(self) -> pd.DataFrame:
        """
        从 Excel 加载数据，执行字段清洗、类型转换和基础过滤。
        """
        if not os.path.exists(self.data_path):
            raise FileNotFoundError(f"未找到数据文件: {self.data_path}")

        print(f"正在从 {self.data_path} 加载数据...")
        df = pd.read_excel(self.data_path)
        
        # 1. 清洗列名（去除首尾空格）
        df.columns = [c.strip() for c in df.columns]
        
        # 2. 类型转换与基础清洗
        df['日期'] = pd.to_datetime(df['日期'])
        df['门店编码'] = df['门店编码'].astype(str)
        df['商品编码'] = df['商品编码'].astype(str)
        
        # 3. 数据过滤：剔除非实物商品项
        initial_count = len(df)
        df = df[~df['商品名称'].isin(self.EXCLUDE_SKU_NAMES)]
        filtered_count = initial_count - len(df)
        if filtered_count > 0:
            print(f"已过滤非商品项（如送货费）: {filtered_count} 行")
        
        # 4. 特征工程：计算实收金额
        # 实收金额 = 销售金额 - 折扣金额
        df['实收金额'] = df['销售金额'] - df['折扣金额']
        
        return df

if __name__ == "__main__":
    # Test run
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")
    loader = DataLoader(path)
    df = loader.load()
    print(df.head())
    print(df.dtypes)
