import os
import sys
import pandas as pd
import json
import numpy as np
from datetime import datetime

from order_analysis.src.dal import DataLoader
from order_analysis.src.strategies.overview_strategy import OverviewStrategy
from order_analysis.src.strategies.product_strategy import ProductStrategy
from order_analysis.src.strategies.pricing_strategy import PricingStrategy
from order_analysis.src.strategies.temporal_strategy import TemporalStrategy
from order_analysis.src.strategies.basket_strategy import BasketStrategy
from order_analysis.src.utils.time_utils import get_day_type

# Helper to serialize numpy types
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super(NpEncoder, self).default(obj)

def run_strategic_pipeline():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")
    output_dir = os.path.join(base_dir, "reports", "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(">>> 🚀 [Strategic Pipeline] Loading Data...")
    loader = DataLoader(data_path)
    df = loader.load()
    
    # Preprocessing
    df['day_type'] = df['日期'].apply(get_day_type)
    
    def assign_period(h):
        if 6 <= h < 11: return '1_Morning'
        elif 11 <= h < 14: return '2_Noon'
        elif 14 <= h < 17: return '3_Afternoon'
        elif 17 <= h < 22: return '4_Evening'
        else: return '5_LateNight'
        
    df['hour'] = df['交易时间'].dt.hour
    df['period'] = df['hour'].apply(assign_period)
    
    final_output = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "data_range": [str(df['日期'].min()), str(df['日期'].max())]
        },
        "global": {},
        "channels": {}
    }
    
    # === Phase 1: Global Overview ===
    print(">>> Phase 1: Calculating Overview...")
    final_output["global"]["business_overview"] = OverviewStrategy.calc_business_overview(df)
    final_output["global"]["channel_efficiency"] = OverviewStrategy.calc_channel_efficiency(df)
    
    # === Phase 2: Product & Pricing ===
    print(">>> Phase 2: Product & Pricing Strategy...")
    final_output["global"]["product_efficiency"] = {
        "penetration_affinity": ProductStrategy.calc_penetration_affinity(df),
        "abc_xyz": ProductStrategy.calc_abc_xyz(df)
    }
    final_output["global"]["pricing_efficiency"] = {
        "elasticity": PricingStrategy.calc_elasticity(df),
        "skewness": PricingStrategy.calc_skewness(df),
        "promo_dist": PricingStrategy.calc_promo_dist(df)
    }
    
    # === Phase 3: Context & Basket ===
    print(">>> Phase 3: Temporal & Basket Strategy...")
    final_output["global"]["spatio_temporal"] = {
        "overview": TemporalStrategy.calc_overview(df),
        "fluctuation": TemporalStrategy.calc_fluctuation(df),
        "tgi_heatmap": TemporalStrategy.calc_tgi_heatmap(df),
        "top_scenarios": TemporalStrategy.find_top_scenarios(df)
    }
    final_output["global"]["basket_features"] = {
        "complexity_clusters": BasketStrategy.analyze_complexity(df),
        "orphan_orders": BasketStrategy.analyze_orphans(df)
    }
    
    # 分渠道 Overview (复用逻辑)
    target_channels = ['万家App', '美团外卖', '饿了么', '京东小时购', '万家小程序']
    for ch in target_channels:
        if ch not in df['平台触点名称'].unique(): continue
        print(f"   -> Channel Deep Dive: {ch}")
        ch_df = df[df['平台触点名称'] == ch]
        
        # 计算该渠道的详细商品排名 (Top/Bottom x GMV/Qty)
        sku_stats = ch_df.groupby('商品名称').agg({'实收金额': 'sum', '销售数量': 'sum'})
        
        top_10_gmv = sku_stats.sort_values('实收金额', ascending=False).head(10)[['实收金额']].to_dict()['实收金额']
        bottom_10_gmv = sku_stats[sku_stats['实收金额']>0].sort_values('实收金额', ascending=True).head(10)[['实收金额']].to_dict()['实收金额']
        
        top_10_qty = sku_stats.sort_values('销售数量', ascending=False).head(10)[['销售数量']].to_dict()['销售数量']
        bottom_10_qty = sku_stats[sku_stats['销售数量']>0].sort_values('销售数量', ascending=True).head(10)[['销售数量']].to_dict()['销售数量']

        final_output["channels"][ch] = {
            "product_rankings": {
                "top_10_gmv": top_10_gmv,
                "bottom_10_gmv": bottom_10_gmv,
                "top_10_qty": top_10_qty,
                "bottom_10_qty": bottom_10_qty
            },
            "business_overview": OverviewStrategy.calc_business_overview(ch_df),
            "product_efficiency": {
                "penetration_affinity": ProductStrategy.calc_penetration_affinity(ch_df),
                "abc_xyz": ProductStrategy.calc_abc_xyz(ch_df)
            },
            "pricing_efficiency": {
                "elasticity": PricingStrategy.calc_elasticity(ch_df),
                "skewness": PricingStrategy.calc_skewness(ch_df),
                "promo_dist": PricingStrategy.calc_promo_dist(ch_df)
            },
            "spatio_temporal": {
                "overview": TemporalStrategy.calc_overview(ch_df),
                "fluctuation": TemporalStrategy.calc_fluctuation(ch_df),
                "tgi_heatmap": TemporalStrategy.calc_tgi_heatmap(ch_df),
                "top_scenarios": TemporalStrategy.find_top_scenarios(ch_df)
            },
            "basket_features": {
                "complexity_clusters": BasketStrategy.analyze_complexity(ch_df),
                "orphan_orders": BasketStrategy.analyze_orphans(ch_df)
            }
        }

    # Save
    out_path = os.path.join(output_dir, "analysis_v4_full.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_output, f, cls=NpEncoder, ensure_ascii=False, indent=2)
        
    print(f">>> ✅ Phase 1 Complete. Saved to {out_path}")

if __name__ == "__main__":
    run_strategic_pipeline()
