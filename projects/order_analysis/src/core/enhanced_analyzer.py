import pandas as pd
import numpy as np
from collections import Counter
from itertools import combinations
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from typing import Dict, Any, List

class EnhancedAnalyzer:
    """
    数据科学家级的分析引擎
    """

    @staticmethod
    def calc_metrics(df: pd.DataFrame) -> Dict[str, float]:
        if df.empty: return {}
        
        gmv = df['实收金额'].sum()
        orders = df['流水单号'].nunique()
        items = df['销售数量'].sum()
        discount = df['折扣金额'].sum()
        raw_gmv = gmv + discount
        
        return {
            "gmv": float(gmv),
            "orders": int(orders),
            "aov": float(gmv / orders) if orders > 0 else 0.0,
            "upt": float(items / orders) if orders > 0 else 0.0,
            "discount_rate": float(discount / raw_gmv) if raw_gmv > 0 else 0.0,
            "avg_price": float(gmv / items) if items > 0 else 0.0
        }

    @staticmethod
    def analyze_price_bands(df: pd.DataFrame) -> Dict[str, float]:
        """价格带分布"""
        order_gmv = df.groupby('流水单号')['实收金额'].sum()
        bins = [0, 20, 50, 80, 120, 10000]
        labels = ['0-20', '20-50', '50-80', '80-120', '120+']
        cats = pd.cut(order_gmv, bins=bins, labels=labels)
        return cats.value_counts(normalize=True).to_dict()

    @staticmethod
    def analyze_drivers(df: pd.DataFrame, top_n=10) -> Dict[str, List]:
        """商品驱动力"""
        # SKU Level
        sku_stats = df.groupby('商品名称').agg({
            '实收金额': 'sum',
            '销售数量': 'sum'
        }).sort_values('实收金额', ascending=False).head(top_n)
        
        top_skus = []
        for name, row in sku_stats.iterrows():
            top_skus.append({
                "name": name,
                "gmv": float(row['实收金额']),
                "qty": int(row['销售数量']),
                "price": float(row['实收金额']/row['销售数量']) if row['销售数量']>0 else 0
            })
            
        # Category Level
        cat_stats = df.groupby('小类编码').agg({
            '实收金额': 'sum',
            '商品名称': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown'
        }).sort_values('实收金额', ascending=False).head(5)
        
        top_cats = []
        total_gmv = df['实收金额'].sum()
        for cat_code, row in cat_stats.iterrows():
            top_cats.append({
                "code": str(cat_code),
                "name": row['商品名称'], # 用该类目下最热单品代表
                "gmv": float(row['实收金额']),
                "share": float(row['实收金额']/total_gmv) if total_gmv > 0 else 0
            })
            
        return {"top_skus": top_skus, "top_categories": top_cats}

    @staticmethod
    def analyze_basket(df: pd.DataFrame, min_support=5) -> List[Dict]:
        """购物篮连带 (简化版)"""
        basket = df.groupby('流水单号')['商品名称'].apply(list)
        basket = basket[basket.apply(len) > 1]
        if len(basket) < 10: return []
        
        pair_counts = Counter()
        for items in basket:
            unique_items = sorted(list(set(items)))
            for pair in combinations(unique_items, 2):
                pair_counts[pair] += 1
                
        results = []
        for (a, b), count in pair_counts.most_common(5):
            if count < min_support: break
            results.append({
                "items": [a, b],
                "count": count
            })
        return results

    @staticmethod
    def analyze_promo_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """促销结构与弹性"""
        orders = df.groupby('流水单号').agg({
            '实收金额': 'sum',
            '折扣金额': 'sum',
            '销售数量': 'sum'
        })
        orders['raw_gmv'] = orders['实收金额'] + orders['折扣金额']
        orders['rate'] = orders['折扣金额'] / (orders['raw_gmv'] + 1e-9)
        
        def label_promo(r):
            if r == 0: return 'NoPromo'
            if r < 0.15: return 'Low'
            return 'High'
            
        orders['type'] = orders['rate'].apply(label_promo)
        
        # 分布
        dist = orders['type'].value_counts(normalize=True).to_dict()
        
        # 弹性 (各分层的 AOV/UPT)
        perf = orders.groupby('type').agg({
            '实收金额': 'mean',
            '销售数量': 'mean'
        }).to_dict('index')
        
        return {"depth_dist": dist, "elasticity": perf}

    @staticmethod
    def perform_clustering(df: pd.DataFrame) -> List[Dict]:
        """3D 聚类: AOV, UPT, Discount"""
        orders = df.groupby('流水单号').agg({
            '实收金额': 'sum',
            '销售数量': 'sum',
            '折扣金额': 'sum'
        }).reset_index()
        
        if len(orders) < 50: return []
        
        orders['raw_gmv'] = orders['实收金额'] + orders['折扣金额']
        orders['disc_rate'] = orders['折扣金额'] / (orders['raw_gmv'] + 1e-9)
        
        # Features: AOV, UPT, Discount
        X = orders[['实收金额', '销售数量', 'disc_rate']].copy()
        # 简单清洗异常值
        X = X[X['实收金额'] < 1000]
        
        if len(X) < 10: return []
        
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # K=4
        kmeans = KMeans(n_clusters=4, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        
        X['cluster'] = labels
        
        # Profile
        profiles = []
        total_count = len(X)
        
        for cid in range(4):
            c_data = X[X['cluster'] == cid]
            if len(c_data) == 0: continue
            
            avg_aov = c_data['实收金额'].mean()
            avg_upt = c_data['销售数量'].mean()
            avg_disc = c_data['disc_rate'].mean()
            
            # 自动打标
            label = "标准"
            if avg_disc > 0.15: label = "薅羊毛"
            elif avg_aov > 100 and avg_upt > 5: label = "囤货"
            elif avg_aov > 80: label = "品质"
            elif avg_upt < 2: label = "便利"
            
            profiles.append({
                "label": label,
                "share": len(c_data) / total_count,
                "features": {
                    "Avg_AOV": float(avg_aov),
                    "Avg_Items": float(avg_upt),
                    "Avg_Discount": float(avg_disc)
                }
            })
            
        return sorted(profiles, key=lambda x: x['share'], reverse=True)
