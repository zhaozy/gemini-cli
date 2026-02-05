import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List

class BasketStrategy:
    """
    篮筐特征分析
    """
    
    @staticmethod
    def analyze_complexity(df: pd.DataFrame) -> List[Dict]:
        """
        篮筐复杂度聚类 (单价, 件数, 类目数)
        """
        basket = df.groupby('流水单号').agg({
            '实收金额': 'sum',
            '销售数量': 'sum',
            '小类编码': 'nunique'
        }).reset_index()
        
        # 至少要有一定样本量
        if len(basket) < 50: return []
        
        X = basket[['实收金额', '销售数量', '小类编码']].copy()
        # 清洗
        X = X[X['实收金额'] < 2000]
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        kmeans = KMeans(n_clusters=3, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        basket['cluster'] = labels
        
        profiles = []
        for cid in range(3):
            c_data = basket[basket['cluster'] == cid]
            if len(c_data) == 0: continue
            
            avg_aov = c_data['实收金额'].mean()
            avg_items = c_data['销售数量'].mean()
            avg_cats = c_data['小类编码'].mean()
            
            # 打标
            label = "标准篮筐"
            if avg_items > 8 and avg_cats > 3: label = "囤货指纹"
            elif avg_items < 2: label = "补缺指纹"
            elif avg_aov > 100: label = "高值指纹"
            
            profiles.append({
                "label": label,
                "share": len(c_data) / len(basket),
                "features": {
                    "items": float(avg_items),
                    "categories": float(avg_cats),
                    "aov": float(avg_aov)
                }
            })
            
        return sorted(profiles, key=lambda x: x['share'], reverse=True)

    @staticmethod
    def analyze_orphans(df: pd.DataFrame) -> Dict[str, Any]:
        """
        孤儿单诊断
        """
        # 订单级
        order_items = df.groupby('流水单号')['销售数量'].sum()
        orphans = order_items[order_items == 1].index
        
        ratio = len(orphans) / len(order_items)
        
        # 找出元凶 SKU
        if len(orphans) > 0:
            orphan_df = df[df['流水单号'].isin(orphans)]
            culprits = orphan_df['商品名称'].value_counts(normalize=True).head(5).to_dict()
        else:
            culprits = {}
            
        return {
            "ratio": float(ratio),
            "culprits": culprits
        }
