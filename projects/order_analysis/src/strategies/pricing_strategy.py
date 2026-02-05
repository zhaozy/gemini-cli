import pandas as pd
import numpy as np
from typing import Dict, Any

class PricingStrategy:
    """
    负责价格与促销效率分析 (v4.3) - 样本自适应回退版
    """
    
    @staticmethod
    def _compute_uplift(df_slice: pd.DataFrame) -> pd.DataFrame:
        """内部计算逻辑"""
        # 聚合：SKU x 日期 x 是否促销
        daily_sku = df_slice.groupby(['商品名称', '日期', 'is_promo'])['销售数量'].sum().reset_index()
        sku_perf = daily_sku.groupby(['商品名称', 'is_promo'])['销售数量'].mean().unstack()
        
        if 1 not in sku_perf.columns or 0 not in sku_perf.columns:
            return pd.DataFrame()
            
        sku_perf.columns = ['Q_base', 'Q_promo']
        sku_perf = sku_perf.dropna()
        sku_perf['uplift'] = (sku_perf['Q_promo'] - sku_perf['Q_base']) / sku_perf['Q_base']
        return sku_perf

    @staticmethod
    def calc_elasticity(df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算折扣弹性 (基于 '折扣类型' 字段)
        """
        # 1. 筛选清洁基准期 (Workday)
        base_df = df[df['day_type'] == 'Workday'].copy()
        if base_df.empty: return {}
        
        # 2. 精准定义促销状态
        # n-无折扣促销 -> 基准
        # p-普通促销, E-标签促销, q-数量促销 -> 促销
        def get_promo_status(t):
            if t == 'n-无折扣促销': return 0
            if t in ['p-普通促销', 'E-标签促销', 'q-数量促销', 'o-满M减N促销']: return 1
            return -1 # Ignore others
            
        base_df['is_promo'] = base_df['折扣类型'].apply(get_promo_status)
        base_df = base_df[base_df['is_promo'] != -1]
        
        # 3. 价格稳定性审计与样本量校验 (Price Audit & Sample Validation)
        sku_stats = base_df.groupby(['商品名称', 'is_promo'])['流水单号'].nunique().unstack(fill_value=0)
        sku_stats.columns = ['days_base', 'days_promo']
        
        sku_promo_counts = base_df.groupby('商品名称')['is_promo'].agg(['sum', 'count'])
        sku_promo_counts['promo_rate'] = sku_promo_counts['sum'] / sku_promo_counts['count']
        
        # 合并样本量数据
        sku_promo_counts = sku_promo_counts.join(sku_stats)
        
        audit_res = {
            "total_active_skus": int(len(sku_promo_counts)),
            "always_full_price_count": int(len(sku_promo_counts[sku_promo_counts['promo_rate'] == 0])),
            "always_promo_count": int(len(sku_promo_counts[sku_promo_counts['promo_rate'] == 1])),
            "price_active_count": int(len(sku_promo_counts[(sku_promo_counts['promo_rate'] > 0) & (sku_promo_counts['promo_rate'] < 1)])),
            "insignificant_sample_count": int(len(sku_promo_counts[(sku_promo_counts['days_promo'] < 3) | (sku_promo_counts['days_base'] < 3)]))
        }
        
        # 4. 弹性计算 (仅针对 price_active 且 样本量充足 的商品)
        # 设置最小样本天数为 3 (考虑到这是日分析)
        valid_skus = sku_promo_counts[
            (sku_promo_counts['promo_rate'] > 0) & 
            (sku_promo_counts['promo_rate'] < 1) &
            (sku_promo_counts['days_promo'] >= 3) &
            (sku_promo_counts['days_base'] >= 3)
        ].index
        
        if len(valid_skus) == 0:
            return {"audit": audit_res, "inelastic_skus": [], "elastic_skus": [], "method": "Workday (Sample-Validated)"}
            
        target_df = base_df[base_df['商品名称'].isin(valid_skus)]
        
        # 聚合：SKU x 是否促销
        sku_perf = target_df.groupby(['商品名称', 'is_promo'])['销售数量'].mean().unstack()
        
        if 1 not in sku_perf.columns or 0 not in sku_perf.columns:
            return {"audit": audit_res, "inelastic_skus": [], "elastic_skus": [], "method": "Workday (Type-based)"}
            
        sku_perf.columns = ['Q_base', 'Q_promo']
        sku_perf = sku_perf.dropna()
        sku_perf['uplift'] = (sku_perf['Q_promo'] - sku_perf['Q_base']) / sku_perf['Q_base']
        
        u_low = np.percentile(sku_perf['uplift'], 25)
        u_high = np.percentile(sku_perf['uplift'], 75)
        
        inelastic = sku_perf[sku_perf['uplift'] <= u_low].sort_values('uplift').head(10).index.tolist()
        elastic = sku_perf[sku_perf['uplift'] >= u_high].sort_values('uplift', ascending=False).head(10).index.tolist()
        
        return {
            "audit": audit_res,
            "inelastic_skus": inelastic,
            "elastic_skus": elastic,
            "thresholds": {"uplift_low": float(u_low), "uplift_high": float(u_high)},
            "method": "Workday (Type-based)"
        }

    @staticmethod
    def calc_skewness(df: pd.DataFrame) -> Dict[str, Any]:
        order_gmv = df.groupby('流水单号')['实收金额'].sum()
        if order_gmv.empty: return {}
        
        mean, median, std = order_gmv.mean(), order_gmv.median(), order_gmv.std()
        mode = order_gmv.round(0).mode()[0] if not order_gmv.empty else 0
        skew_val = order_gmv.skew()
        
        diagnosis = "均衡"
        if skew_val > 1: diagnosis = "重度正偏 (低客单严重拖累)"
        elif skew_val > 0.5: diagnosis = "轻度正偏"
        elif skew_val < -0.5: diagnosis = "负偏 (高客单为主)"
        
        return {
            "mean": float(mean), "median": float(median), "mode": float(mode),
            "skewness_index": float(skew_val) if not pd.isna(skew_val) else 0,
            "diagnosis": diagnosis
        }

    @staticmethod
    def calc_promo_dist(df: pd.DataFrame) -> Dict[str, Any]:
        orders = df.groupby('流水单号').agg({'实收金额': 'sum', '折扣金额': 'sum'})
        raw = orders['实收金额'] + orders['折扣金额']
        orders['rate'] = orders['折扣金额'] / (raw + 1e-9)
        bins = [-0.01, 0.001, 0.1, 0.2, 0.3, 0.4, 0.5, 1.0]
        labels = ['NoPromo', '0-10%', '10-20%', '20-30%', '30-40%', '40-50%', '50%+']
        dist = pd.cut(orders['rate'], bins=bins, labels=labels).value_counts(normalize=True).to_dict()
        return {"depth_dist": dist}