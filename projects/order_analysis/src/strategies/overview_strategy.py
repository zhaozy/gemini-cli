import pandas as pd
import numpy as np
from typing import Dict, Any

class OverviewStrategy:
    """
    负责整体业务效果与渠道效率的计算 (v4.1) - 统计自适应版
    """
    
    @staticmethod
    def calc_business_overview(df: pd.DataFrame) -> Dict[str, Any]:
        if df.empty: return {}
        gmv = df['实收金额'].sum()
        raw_gmv = gmv + df['折扣金额'].sum()
        orders = df['流水单号'].nunique()
        items = df['销售数量'].sum()
        discount = df['折扣金额'].sum()
        promo_orders = df[df['折扣金额'] > 0]['流水单号'].nunique()
        
        active_promo_types = ['p-普通促销', 'E-标签促销', 'q-数量促销', 'C-加价换购']
        promo_volume = df[df['折扣类型'].isin(active_promo_types)]['销售数量'].sum()
        sku_promo_penetration = promo_volume / items if items > 0 else 0
        
        active_skus = df['商品编码'].nunique()
        days = df['日期'].nunique()
        daily_orders = orders / days if days > 0 else 0
        
        return {
            "gmv_total": float(gmv),
            "order_total": int(orders),
            "daily_avg_orders": float(daily_orders),
            "active_skus": int(active_skus),
            "discount_rate": float(discount / raw_gmv) if raw_gmv > 0 else 0.0,
            "promo_penetration": float(promo_orders / orders) if orders > 0 else 0.0,
            "sku_promo_penetration": float(sku_promo_penetration),
            "aov": float(gmv / orders) if orders > 0 else 0.0,
            "upt": float(items / orders) if orders > 0 else 0.0
        }

    @staticmethod
    def calc_channel_efficiency(df: pd.DataFrame) -> Dict[str, Any]:
        """
        使用 Z-Score 自动判定生态位
        """
        # 1. 订单级数据聚合
        orders = df.groupby(['平台触点名称', '流水单号']).agg({
            '实收金额': 'sum', 
            '销售数量': 'sum', 
            '折扣金额': 'sum'
        }).reset_index()
        orders['raw_gmv'] = orders['实收金额'] + orders['折扣金额']
        orders['has_promo'] = orders['折扣金额'] > 0
        
        # 2. 渠道汇总
        ch_stats = orders.groupby('平台触点名称').agg({
            '实收金额': 'sum', 
            '流水单号': 'count', 
            '销售数量': 'sum', 
            '折扣金额': 'sum', 
            'raw_gmv': 'sum',
            'has_promo': 'sum'
        })
        
        ch_metrics = pd.DataFrame(index=ch_stats.index)
        ch_metrics['aov'] = ch_stats['实收金额'] / ch_stats['流水单号']
        ch_metrics['upt'] = ch_stats['销售数量'] / ch_stats['流水单号']
        ch_metrics['disc_rate'] = ch_stats['折扣金额'] / ch_stats['raw_gmv']
        ch_metrics['promo_pen'] = ch_stats['has_promo'] / ch_stats['流水单号']
        
        # 3. 统计基准
        aov_mean, aov_std = ch_metrics['aov'].mean(), ch_metrics['aov'].std()
        disc_mean, disc_std = ch_metrics['disc_rate'].mean(), ch_metrics['disc_rate'].std()
        upt_mean, upt_std = ch_metrics['upt'].mean(), ch_metrics['upt'].std()
        
        ecological_niche = {}
        rankings = {"gmv_share": {}, "aov": {}, "upt": {}, "discount_rate": {}, "promo_penetration": {}}
        price_bands = {}
        total_gmv = ch_stats['实收金额'].sum()
        
        for ch, row in ch_metrics.iterrows():
            tags = []
            if (row['aov'] - aov_mean) > 0.5 * aov_std: tags.append("高客单")
            elif (row['aov'] - aov_mean) < -0.5 * aov_std: tags.append("低客单")
            if (row['disc_rate'] - disc_mean) > 0.5 * disc_std: tags.append("强促销")
            elif (row['disc_rate'] - disc_mean) < -0.5 * disc_std: tags.append("低价格敏感")
            if (row['upt'] - upt_mean) > 0.5 * upt_std: tags.append("囤货型")
            elif (row['upt'] - upt_mean) < -0.5 * upt_std: tags.append("补缺/便利")
            
            ecological_niche[ch] = " + ".join(tags) if tags else "均衡型"
            
            rankings["gmv_share"][ch] = float(ch_stats.loc[ch, '实收金额'] / total_gmv)
            rankings["aov"][ch] = float(row['aov'])
            rankings["upt"][ch] = float(row['upt'])
            rankings["discount_rate"][ch] = float(row['disc_rate'])
            rankings["promo_penetration"][ch] = float(row['promo_pen'])
            
            ch_orders = orders[orders['平台触点名称'] == ch]
            all_aov = orders['实收金额']
            bins = [0, np.percentile(all_aov, 20), np.percentile(all_aov, 50), np.percentile(all_aov, 80), 10000]
            labels = ['VeryLow', 'Low', 'Mid-High', 'Premium']
            price_bands[ch] = pd.cut(ch_orders['实收金额'], bins=bins, labels=labels).value_counts(normalize=True).to_dict()

        # 商品贡献 Top/Bottom (Global)
        sku_gmv = df.groupby('商品名称')['实收金额'].sum().sort_values(ascending=False)
        top_10_gmv = sku_gmv.head(10).to_dict()
        bottom_10_gmv = sku_gmv[sku_gmv > 0].tail(10).to_dict()

        return {
            "rankings": rankings,
            "price_bands": price_bands,
            "ecological_niche": ecological_niche,
            "benchmarks": {"aov_avg": float(aov_mean), "disc_avg": float(disc_mean)},
            "global_top_10_gmv": top_10_gmv,
            "global_bottom_10_gmv": bottom_10_gmv
        }
