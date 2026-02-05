import pandas as pd
import numpy as np
from typing import Dict, Any, List

class ProductStrategy:
    """
    商品效率分析 (v4.1) - 统计自适应版
    """
    
    @staticmethod
    def calc_penetration_affinity(df: pd.DataFrame) -> Dict[str, Any]:
        total_orders = df['流水单号'].nunique()
        if total_orders == 0: return {}
        
        # 1. 计算全站基准 (Global Benchmarks)
        total_items = df['销售数量'].sum()
        global_avg_upt = total_items / total_orders
        global_affinity_base = global_avg_upt - 1 # 全站平均带动水平
        
        # 2. 订单级件数映射
        order_items_dict = df.groupby('流水单号')['销售数量'].sum().to_dict()
        
        # 3. SKU 级指标计算
        # 只分析有规模的商品 (GMV 前 300)
        sku_stats = df.groupby('商品名称').agg({
            '流水单号': 'nunique',
            '实收金额': 'sum',
            '销售数量': 'sum'
        })
        top_skus = sku_stats.sort_values('实收金额', ascending=False).head(300).index
        
        results = []
        sku_order_map = df[df['商品名称'].isin(top_skus)].groupby('商品名称')['流水单号'].apply(list).to_dict()
        
        for sku in top_skus:
            oids = sku_order_map.get(sku, [])
            penetration = len(oids) / total_orders
            
            # 带动系数
            basket_sizes = [order_items_dict[o] for o in oids]
            affinity = np.mean(basket_sizes) - 1 if basket_sizes else 0
            
            # 单价
            row = sku_stats.loc[sku]
            avg_price = row['实收金额'] / row['销售数量'] if row['销售数量'] > 0 else 0
            
            results.append({
                "sku": sku,
                "penetration": float(penetration),
                "affinity": float(affinity),
                "avg_price": float(avg_price)
            })
            
        df_res = pd.DataFrame(results)
        if df_res.empty: return {}
        
        # 4. 动态确定阈值 (基于分位数)
        # 高渗透: Top 20%
        p_threshold = np.percentile(df_res['penetration'], 80)
        # 高带动: 必须优于全站平均
        a_threshold = global_affinity_base
        # 低价线: 中位数 (Median) - 扩大刺客打击面
        price_q1 = np.percentile(df_res['avg_price'], 50)
        
        quadrants = {"Hooks": [], "Islands": [], "Bundlers": [], "Assassins": []}
        
        for _, row in df_res.iterrows():
            p, a, price = row['penetration'], row['affinity'], row['avg_price']
            item = row.to_dict()
            
            if p >= p_threshold and a >= a_threshold:
                quadrants["Hooks"].append(item)
            elif p >= p_threshold and a < a_threshold:
                if price <= price_q1:
                    quadrants["Assassins"].append(item)
                else:
                    quadrants["Islands"].append(item)
            elif p < p_threshold and a >= a_threshold:
                quadrants["Bundlers"].append(item)
            
        return {
            "benchmarks": {
                "p_threshold": float(p_threshold),
                "a_threshold": float(a_threshold),
                "price_q1": float(price_q1),
                "global_avg_upt": float(global_avg_upt)
            },
            "quadrants": quadrants
        }

    @staticmethod
    def calc_abc_xyz(df: pd.DataFrame) -> Dict[str, Any]:
        """
        ABC-XYZ 矩阵 (自适应阈值)
        """
        sku_gmv = df.groupby('商品名称')['实收金额'].sum().sort_values(ascending=False).reset_index()
        total_gmv = sku_gmv['实收金额'].sum()
        sku_gmv['cumsum'] = sku_gmv['实收金额'].cumsum()
        sku_gmv['share'] = sku_gmv['cumsum'] / total_gmv
        
        # ABC 分类 (保持工业标准的 80/15/5)
        def get_abc(x):
            if x <= 0.8: return 'A'
            elif x <= 0.95: return 'B'
            else: return 'C'
        sku_gmv['class_abc'] = sku_gmv['share'].apply(get_abc)
        
        # XYZ 分类 (自适应变异系数分位数)
        daily = df.groupby(['商品名称', '日期'])['销售数量'].sum().reset_index()
        sku_cv = daily.groupby('商品名称')['销售数量'].agg(['mean', 'std']).reset_index()
        sku_cv['cv'] = sku_cv['std'] / sku_cv['mean']
        
        # 仅对 A 类商品的 CV 进行分位数划分，确保 X 确实是相对最稳的
        cv_clean = sku_cv['cv'].dropna()
        if cv_clean.empty:
            x_line, y_line = 0.5, 1.0
        else:
            x_line = np.percentile(cv_clean, 33)
            y_line = np.percentile(cv_clean, 66)
        
        def get_xyz(x):
            if pd.isna(x): return 'Z'
            if x <= x_line: return 'X'
            elif x <= y_line: return 'Y'
            else: return 'Z'
        sku_cv['class_xyz'] = sku_cv['cv'].apply(get_xyz)
        
        merged = pd.merge(sku_gmv, sku_cv[['商品名称', 'class_xyz', 'cv']], on='商品名称', how='left')
        merged['class_xyz'] = merged['class_xyz'].fillna('Z')
        merged['matrix'] = merged['class_abc'] + merged['class_xyz']
        
        matrix_result = {}
        for cls in merged['matrix'].unique():
            matrix_result[cls] = merged[merged['matrix'] == cls]['商品名称'].head(5).tolist()
            
        pareto_list = merged[merged['class_abc'] == 'A'][['商品名称', '实收金额', 'share']].head(10).to_dict(orient='records')
        
        return {
            "matrix_abc_xyz": matrix_result,
            "pareto_list": pareto_list,
            "thresholds": {"cv_x_line": float(x_line), "cv_y_line": float(y_line)}
        }