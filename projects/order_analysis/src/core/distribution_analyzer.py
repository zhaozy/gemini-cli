import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

class DistributionAnalyzer:
    @staticmethod
    def analyze_aov_distribution(df: pd.DataFrame) -> pd.DataFrame:
        """
        按价格区间统计各渠道的订单占比
        """
        # 聚合到订单层级
        orders = df.groupby(['平台触点名称', '流水单号'])['实收金额'].sum().reset_index()
        
        bins = [0, 20, 50, 80, 120, 10000]
        labels = ['1_<20', '2_20-50', '3_50-80', '4_80-120', '5_>120']
        
        orders['price_range'] = pd.cut(orders['实收金额'], bins=bins, labels=labels)
        
        # 交叉表：渠道 x 价格区间
        pivot = pd.crosstab(orders['平台触点名称'], orders['price_range'])
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0)
        
        return pivot_pct

    @staticmethod
    def perform_clustering(df: pd.DataFrame, n_clusters: int = 4) -> tuple[pd.DataFrame, pd.DataFrame]:
        """
        使用 K-Means 对订单进行分类
        Returns:
            cluster_profiles: 每个聚类的中心点特征 (Mean GMV, Mean Items)
            channel_dist: 各渠道在不同聚类中的占比
        """
        # 1. 准备数据：订单层级 (GMV, Items)
        orders = df.groupby(['平台触点名称', '流水单号']).agg({
            '实收金额': 'sum',
            '销售数量': 'sum'
        }).reset_index()
        
        # 剔除极端的异常订单（如 > 500元）以免干扰聚类中心
        # 仅用于训练模型，预测时可包含
        train_data = orders[orders['实收金额'] < 1000].copy()
        
        X = train_data[['实收金额', '销售数量']]
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # 2. 训练模型
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        kmeans.fit(X_scaled)
        
        # 3. 预测所有数据
        X_all = orders[['实收金额', '销售数量']]
        X_all_scaled = scaler.transform(X_all)
        orders['cluster'] = kmeans.predict(X_all_scaled)
        
        # 4. 分析聚类特征 (Profile)
        profile = orders.groupby('cluster').agg({
            '实收金额': 'mean',
            '销售数量': 'mean',
            '流水单号': 'count'
        }).rename(columns={'流水单号': 'count'})
        
        profile['share'] = profile['count'] / profile['count'].sum()
        profile = profile.sort_values('实收金额')
        
        # 给聚类起名 (基于中心点相对位置的动态命名)
        # 计算全局均值用于对比
        global_avg_price = orders['实收金额'].mean()
        global_avg_items = orders['销售数量'].mean()
        
        def generate_label(row):
            price_factor = row['实收金额'] / global_avg_price
            item_factor = row['销售数量'] / global_avg_items
            
            # 定义价格标签
            if price_factor < 0.6: p_label = "低客单"
            elif price_factor < 1.5: p_label = "中客单"
            else: p_label = "高客单"
            
            # 定义件数标签
            if item_factor < 0.8: i_label = "少件"
            elif item_factor < 1.5: i_label = "中件"
            else: i_label = "多件"
            
            # 组合场景
            if p_label == "高客单" and i_label == "多件": return f"囤货大单 (¥{row['实收金额']:.0f}/{row['销售数量']:.1f}件)"
            if p_label == "高客单" and i_label == "少件": return f"品质精选 (¥{row['实收金额']:.0f}/{row['销售数量']:.1f}件)"
            if p_label == "低客单" and i_label == "多件": return f"凑单小件 (¥{row['实收金额']:.0f}/{row['销售数量']:.1f}件)"
            if p_label == "低客单" and i_label == "少件": return f"便利补给 (¥{row['实收金额']:.0f}/{row['销售数量']:.1f}件)"
            
            return f"标准购物 (¥{row['实收金额']:.0f}/{row['销售数量']:.1f}件)"
            
        profile['label'] = profile.apply(generate_label, axis=1)
        
        # 5. 渠道分布
        channel_dist = pd.crosstab(orders['平台触点名称'], orders['cluster'])
        channel_dist_pct = channel_dist.div(channel_dist.sum(axis=1), axis=0)
        
        # 映射列名为可读标签
        label_map = profile['label'].to_dict()
        channel_dist_pct = channel_dist_pct.rename(columns=label_map)
        
        return profile, channel_dist_pct
