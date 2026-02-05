import os
import sys
import pandas as pd
import json
import numpy as np
from datetime import datetime

# Import Analyzers
from order_analysis.src.dal import DataLoader
from order_analysis.src.core.metrics import MetricEngine
from order_analysis.src.core.channel_analyzer import ChannelAnalyzer
from order_analysis.src.core.distribution_analyzer import DistributionAnalyzer
from order_analysis.src.core.cube_analyzer import CubeAnalyzer
from order_analysis.src.utils.time_utils import get_day_type

# Helper to serialize numpy types
class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer): return int(obj)
        if isinstance(obj, np.floating): return float(obj)
        if isinstance(obj, np.ndarray): return obj.tolist()
        return super(NpEncoder, self).default(obj)

def assign_period(h):
    if 6 <= h < 11: return '1_Morning'
    elif 11 <= h < 14: return '2_Noon'
    elif 14 <= h < 17: return '3_Afternoon'
    elif 17 <= h < 22: return '4_Evening'
    else: return '5_LateNight'

def run_pipeline():
    base_dir = os.getcwd()
    data_path = os.path.join(base_dir, "order_analysis", "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")
    output_dir = os.path.join(base_dir, "order_analysis", "reports", "data")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    print(">>> 1. Loading Data...")
    loader = DataLoader(data_path)
    df = loader.load()
    
    # Preprocessing
    df['day_type'] = df['日期'].apply(get_day_type)
    df['hour'] = df['交易时间'].dt.hour
    df['period'] = df['hour'].apply(assign_period)
    
    # Container for all results
    results = {
        "meta": {
            "generated_at": datetime.now().isoformat(),
            "data_range": [str(df['日期'].min()), str(df['日期'].max())],
            "total_rows": len(df)
        },
        "channels": {}
    }

    print(">>> 2. Analyzing Channels & Cubes...")
    target_channels = ['万家App', '美团外卖', '饿了么', '京东小时购', '万家小程序']
    
    # Global Channel Overview
    ch_overview = ChannelAnalyzer.analyze_overview(df)
    ch_upt = ChannelAnalyzer.analyze_upt(df)
    # Join and convert to dict
    overview_df = ch_overview.join(ch_upt)
    results['global_overview'] = overview_df.reset_index().to_dict(orient='records')

    # Channel Deep Dive
    for ch in target_channels:
        if ch not in df['平台触点名称'].unique(): continue
        
        print(f"   -> Analyzing {ch}...")
        ch_df = df[df['平台触点名称'] == ch]
        
        # 1. Basic Stats
        metrics = MetricEngine.calculate_basic_metrics(ch_df)
        
        # 2. Promo Stats
        promo_df = MetricEngine.analyze_promo_efficiency_by_channel(df) # This returns all channels
        promo_stat = promo_df.loc[ch].to_dict() if ch in promo_df.index else {}
        
        # 3. Top Categories
        top_cats = MetricEngine.get_top_categories_by_channel(ch_df, top_n=5)
        # Fix: get_top_categories_by_channel expects global df usually, but here passing ch_df is fine
        # Re-implement simple top cat for single df to avoid index issues
        top_cats_data = ch_df.groupby('小类编码').agg({
            '商品名称': lambda x: x.mode()[0],
            '实收金额': 'sum',
            '销售数量': 'sum'
        }).sort_values('实收金额', ascending=False).head(5).reset_index().to_dict(orient='records')

        # 4. Cubes (Drill-down)
        cubes = []
        
        # Logic: Find Top Day -> Top Period -> Analyze
        day_stats = ch_df.groupby('day_type')['实收金额'].sum()
        if not day_stats.empty:
            top_day = day_stats.idxmax()
            day_df = ch_df[ch_df['day_type'] == top_day]
            
            period_stats = day_df.groupby('period')['实收金额'].sum()
            if not period_stats.empty:
                top_period = period_stats.idxmax()
                
                # Cube 1: Top Scenario
                slice_df = day_df[day_df['period'] == top_period]
                cube_res = CubeAnalyzer.analyze_slice(slice_df)
                if cube_res:
                    cube_res['slice_name'] = f"{top_day} + {top_period}"
                    cubes.append(cube_res)
        
        # Cube 2: Weekend Evening (Fixed Benchmark)
        alt_df = ch_df[(ch_df['day_type'] == 'Weekend') & (ch_df['period'] == '4_Evening')]
        cube_res_alt = CubeAnalyzer.analyze_slice(alt_df)
        if cube_res_alt:
            cube_res_alt['slice_name'] = "Weekend + 4_Evening"
            cubes.append(cube_res_alt)

        results['channels'][ch] = {
            "metrics": metrics,
            "promo_stat": promo_stat,
            "top_categories": top_cats_data,
            "cubes": cubes
        }

    # Save JSON
    json_path = os.path.join(output_dir, "analysis_data.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, cls=NpEncoder, ensure_ascii=False, indent=2)
    
    print(f">>> Data saved to {json_path}")
    
    # Generate Prompt
    prompt = f"""
    You are a Senior Data Analyst. Based on the data in 'analysis_data.json', write a comprehensive insight report.
    
    Key Focus Areas:
    1. Compare the strategic roles of different channels based on 'global_overview' and 'promo_stat'.
    2. For each channel in 'channels', analyze its 'metrics' and 'top_categories' to define its user persona.
    3. Deep dive into the 'cubes' (Drill-down scenarios). Pay attention to:
       - 'associations': What items are bought together?
       - 'clusters': Is the consumption dominated by 'Low Value' or 'High Value' clusters?
       - 'promo_perf': Is the scenario promotion-driven?
    
    Output Format: Markdown.
    Language: Simplified Chinese.
    """
    
    prompt_path = os.path.join(output_dir, "prompt.txt")
    with open(prompt_path, 'w', encoding='utf-8') as f:
        f.write(prompt)

if __name__ == "__main__":
    run_pipeline()
