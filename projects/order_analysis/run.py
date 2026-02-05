import os
import sys
import pandas as pd
try:
    import tabulate
except ImportError:
    os.system(f"{sys.executable} -m pip install tabulate")

from order_analysis.src.dal import DataLoader
from order_analysis.src.core.metrics import MetricEngine
from order_analysis.src.core.channel_analyzer import ChannelAnalyzer
from order_analysis.src.core.distribution_analyzer import DistributionAnalyzer
from order_analysis.src.core.cube_analyzer import CubeAnalyzer
from order_analysis.src.core.reporter import MarkdownReporter
from order_analysis.src.utils.time_utils import get_day_type

def assign_period(h):
    if 6 <= h < 11: return '1_Morning'
    elif 11 <= h < 14: return '2_Noon'
    elif 14 <= h < 17: return '3_Afternoon'
    elif 17 <= h < 22: return '4_Evening'
    else: return '5_LateNight'

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, "datas", "K5.交易流水明细表2026-01-13 9_49_12.xlsx")
    report_dir = os.path.join(base_dir, "reports")
    
    print(">>> 1. 加载数据...")
    loader = DataLoader(data_path)
    df = loader.load()
    
    # 预处理：增加维度列
    df['day_type'] = df['日期'].apply(get_day_type)
    df['hour'] = df['交易时间'].dt.hour
    df['period'] = df['hour'].apply(assign_period)
    
    print(">>> 2. 核心素材计算...")
    ch_overview = ChannelAnalyzer.analyze_overview(df)
    ch_upt = ChannelAnalyzer.analyze_upt(df)
    ch_overview = ch_overview.join(ch_upt)
    ch_promo = MetricEngine.analyze_promo_efficiency_by_channel(df)
    ch_cats = MetricEngine.get_top_categories_by_channel(df, top_n=5)
    
    print(">>> 3. 编排立体深度报告...")
    reporter = MarkdownReporter(report_dir)
    reporter.add_header("全维度深度洞察报告：时空场货", level=1)
    
    target_channels = ['万家App', '美团外卖', '饿了么', '京东小时购']
    
    for ch in target_channels:
        if ch not in ch_overview.index: continue
        print(f"   -> Analyzing Cube: {ch}...")
        
        # 3.1 渠道整体
        ch_df = df[df['平台触点名称'] == ch]
        
        # 生成定位文案 (复用之前的逻辑)
        row = ch_overview.loc[ch]
        insights = {
            'position': "N/A", 'context': "N/A", 
            'aov': row['aov'], 'upt': row['avg_upt']
        }
        top_prods = ch_cats[ch_cats['平台触点名称'] == ch]
        promo_stat = ch_promo.loc[ch]
        
        reporter.add_channel_deep_dive(ch, insights, top_prods, promo_stat)
        
        # 3.2 智能下钻 (Smart Drill-down)
        # 策略：找出该渠道 GMV 占比最高的 DayType
        day_type_stats = ch_df.groupby('day_type')['实收金额'].sum()
        if day_type_stats.empty: continue
        top_day = day_type_stats.idxmax()
        
        # 在该 DayType 下，找出 Top Period 和 Low Period (做对比)
        day_df = ch_df[ch_df['day_type'] == top_day]
        period_stats = day_df.groupby('period')['实收金额'].sum()
        if period_stats.empty: continue
        
        top_period = period_stats.idxmax()
        # 找一个有量但非最高的做对比 (或者直接找第二高)
        # 这里简单找个 Top 1
        
        # 执行 Cube 分析：Top Day + Top Period
        slice_name = f"{top_day} + {top_period} (核心场景)"
        slice_df = day_df[day_df['period'] == top_period]
        cube_result = CubeAnalyzer.analyze_slice(slice_df)
        reporter.add_cube_slice_analysis(slice_name, cube_result)
        
        # 执行 Cube 分析：Top Day + LateNight (如果有量，分析夜间经济)
        # 或者是 Weekend (如果 Top 是 Workday)
        # 让我们固定分析一下 "周末晚市" (Weekend Evening) 作为一个通用观察点
        if top_day != 'Weekend' or top_period != '4_Evening':
            alt_name = "Weekend + 4_Evening (周末晚市)"
            alt_df = ch_df[(ch_df['day_type'] == 'Weekend') & (ch_df['period'] == '4_Evening')]
            if len(alt_df) > 50:
                cube_result_alt = CubeAnalyzer.analyze_slice(alt_df)
                reporter.add_cube_slice_analysis(alt_name, cube_result_alt)

    reporter.save()
    print(">>> 完成.")

if __name__ == "__main__":
    main()
