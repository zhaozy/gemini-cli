import pandas as pd
from typing import Dict, Any

class MetricEngine:
    @staticmethod
    def calculate_basic_metrics(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculates aggregate metrics for the given dataframe.
        """
        gmv = df['实收金额'].sum()
        orders = df['流水单号'].nunique()
        qty = df['销售数量'].sum()
        
        return {
            "gmv": float(gmv),
            "order_count": int(orders),
            "aov": float(gmv / orders) if orders > 0 else 0.0,
            "total_items": int(qty)
        }

    @staticmethod
    def aggregate_by_time(df: pd.DataFrame, freq: str = 'D') -> pd.DataFrame:
        """
        Aggregates metrics by time frequency.
        freq: 'D' (Day), 'W' (Week), 'M' (Month)
        """
        df = df.copy()
        df['period'] = df['日期'].dt.to_period(freq).dt.start_time
        
        # Aggregation logic
        agg_funcs = {
            '实收金额': 'sum',
            '流水单号': 'nunique',
            '销售数量': 'sum'
        }
        
        res = df.groupby('period').agg(agg_funcs)
        res.columns = ['gmv', 'order_count', 'total_items']
        
        res['aov'] = res['gmv'] / res['order_count']
        
        return res.sort_index()

    @staticmethod
    def analyze_category_performance(df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
        """
        按品类（小类编码）聚合销售表现，返回 GMV 最高的 Top N 品类。
        """
        # 确保包含品类名称（如果数据中有）
        group_cols = ['小类编码']
        
        agg_funcs = {
            '实收金额': 'sum',
            '销售数量': 'sum',
            '流水单号': 'nunique' # 购买该品类的订单数
        }
        
        res = df.groupby(group_cols).agg(agg_funcs)
        res.columns = ['gmv', 'total_items', 'order_count']
        
        # 计算渗透率 (需要在外部计算总订单数，这里先算简单的份额)
        total_gmv = res['gmv'].sum()
        res['gmv_share'] = res['gmv'] / total_gmv
        
        return res.sort_values('gmv', ascending=False).head(top_n)

    @staticmethod
    def get_top_categories_by_channel(df: pd.DataFrame, channel_col: str = '平台触点名称', top_n: int = 5) -> pd.DataFrame:
        """
        按渠道分组，找出每个渠道 GMV 最高的 Top N 品类
        """
        # 1. 聚合
        agg = df.groupby([channel_col, '小类编码']).agg({
            '实收金额': 'sum',
            '销售数量': 'sum',
            '商品名称': lambda x: x.mode()[0] if not x.mode().empty else 'Unknown' # 取众数名称
        }).reset_index()
        
        # 2. 排序并取 Top N
        agg = agg.sort_values([channel_col, '实收金额'], ascending=[True, False])
        
        return agg.groupby(channel_col).head(top_n)

    @staticmethod
    def analyze_promo_efficiency_by_channel(df: pd.DataFrame) -> pd.DataFrame:
        """
        分析各渠道的促销效率：
        - 折扣率
        - 有折扣订单占比
        - 折扣订单 vs 无折扣订单的 AOV 对比 (Promo Uplift)
        """
        # 标记订单是否有折扣
        order_promo = df.groupby(['平台触点名称', '流水单号']).agg({
            '实收金额': 'sum',
            '折扣金额': 'sum'
        }).reset_index()
        
        order_promo['has_promo'] = order_promo['折扣金额'] > 0
        order_promo['gmv_raw'] = order_promo['实收金额'] + order_promo['折扣金额']
        
        # 聚合统计
        def calc_stats(x):
            total_orders = len(x)
            promo_orders = x['has_promo'].sum()
            promo_ratio = promo_orders / total_orders if total_orders > 0 else 0
            
            total_gmv = x['实收金额'].sum()
            total_discount = x['折扣金额'].sum()
            discount_rate = total_discount / (total_gmv + total_discount) if (total_gmv + total_discount) > 0 else 0
            
            # AOV 对比
            aov_promo = x[x['has_promo']]['实收金额'].mean() if promo_orders > 0 else 0
            aov_normal = x[~x['has_promo']]['实收金额'].mean() if (total_orders - promo_orders) > 0 else 0
            
            return pd.Series({
                'discount_rate': discount_rate,
                'promo_order_ratio': promo_ratio,
                'aov_promo': aov_promo,
                'aov_normal': aov_normal,
                'promo_uplift': (aov_promo - aov_normal) / aov_normal if aov_normal > 0 else 0
            })
            
        return order_promo.groupby('平台触点名称').apply(calc_stats).sort_values('discount_rate', ascending=False)
