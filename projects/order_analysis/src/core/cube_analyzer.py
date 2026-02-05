import pandas as pd
from order_analysis.src.core.metrics import MetricEngine
from order_analysis.src.core.distribution_analyzer import DistributionAnalyzer
from order_analysis.src.core.basket_analyzer import BasketAnalyzer
from typing import Dict, Any

class CubeAnalyzer:
    @staticmethod
    def analyze_slice(df_slice: pd.DataFrame) -> Dict[str, Any]:
        """
        对给定的数据切片进行全维度分析
        """
        if len(df_slice) < 50: # 样本过少不分析
            return None
            
        # 1. 基础指标
        metrics = MetricEngine.calculate_basic_metrics(df_slice)
        
        # 2. 折扣分析 (正价 vs 折扣)
        # 订单级
        orders = df_slice.groupby('流水单号').agg({
            '实收金额': 'sum',
            '折扣金额': 'sum',
            '销售数量': 'sum'
        })
        orders['discount_rate'] = orders['折扣金额'] / (orders['实收金额'] + orders['折扣金额'] + 1e-9)
        
        # 分布：无折(0), 浅折(<10%), 深折(>=10%)
        def disc_label(r):
            if r == 0: return 'No Promo'
            if r < 0.1: return 'Low Promo'
            return 'High Promo'
        
        orders['promo_type'] = orders['discount_rate'].apply(disc_label)
        promo_dist = orders['promo_type'].value_counts(normalize=True).to_dict()
        
        # 交叉统计: 不同折扣深度的 AOV/UPT
        promo_perf = orders.groupby('promo_type').agg({
            '实收金额': 'mean', # AOV
            '销售数量': 'mean'  # UPT
        }).to_dict('index')
        
        # 3. 聚类 (消费模式)
        # 简化版聚类，直接返回 profile
        try:
            cluster_prof, _ = DistributionAnalyzer.perform_clustering(df_slice, n_clusters=3)
            clusters = cluster_prof[['label', 'share']].to_dict('records')
        except:
            clusters = []

        # 4. 商品分析
        # Top 5 动销
        top_items = df_slice.groupby('商品名称')['实收金额'].sum().sort_values(ascending=False).head(5)
        top_items_dict = top_items.to_dict()
        
        # 连带率 (只取 Top 3 pair)
        associations = BasketAnalyzer.analyze_associations(df_slice, top_n=3)
        assoc_list = []
        if not associations.empty:
            for _, row in associations.iterrows():
                assoc_list.append(f"{row['item_a']} + {row['item_b']} (共{row['co_occurrence']}次)")
                
        return {
            'metrics': metrics,
            'promo_dist': promo_dist,
            'promo_perf': promo_perf,
            'clusters': clusters,
            'top_items': top_items_dict,
            'associations': assoc_list
        }
