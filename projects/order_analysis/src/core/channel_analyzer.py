import pandas as pd
import numpy as np
from order_analysis.src.utils.time_utils import get_day_type

class ChannelAnalyzer:
    @staticmethod
    def analyze_overview(df: pd.DataFrame) -> pd.DataFrame:
        """
        渠道概览：GMV, 订单量, AOV, 件单价
        """
        # 填充空渠道
        df = df.copy()
        df['平台触点名称'] = df['平台触点名称'].fillna('Unknown')
        
        agg_funcs = {
            '实收金额': 'sum',
            '流水单号': 'nunique',
            '销售数量': 'sum'
        }
        res = df.groupby('平台触点名称').agg(agg_funcs)
        res.columns = ['gmv', 'order_count', 'total_items']
        
        res['aov'] = res['gmv'] / res['order_count']
        res['avg_price'] = res['gmv'] / res['total_items'] # 件单价
        
        # 计算 GMV 占比
        res['gmv_share'] = res['gmv'] / res['gmv'].sum()
        
        return res.sort_values('gmv', ascending=False)

    @staticmethod
    def analyze_time_preference(df: pd.DataFrame) -> pd.DataFrame:
        """
        时间偏好：各渠道在不同时段的订单占比
        """
        df = df.copy()
        df['hour'] = df['交易时间'].dt.hour
        
        def assign_period(h):
            if 6 <= h < 11: return '1_Morning (06-11)'
            elif 11 <= h < 14: return '2_Noon (11-14)'
            elif 14 <= h < 17: return '3_Afternoon (14-17)'
            elif 17 <= h < 22: return '4_Evening (17-22)'
            else: return '5_LateNight (22-06)'
            
        df['period'] = df['hour'].apply(assign_period)
        
        # 聚合：渠道 x 时段 的订单量
        # 注意：需要去重订单号
        orders = df[['平台触点名称', '流水单号', 'period']].drop_duplicates()
        pivot = pd.crosstab(orders['平台触点名称'], orders['period'])
        
        # 转为百分比 (行归一化)
        pivot_pct = pivot.div(pivot.sum(axis=1), axis=0)
        
        return pivot_pct

    @staticmethod
    def analyze_discount_sensitivity(df: pd.DataFrame) -> pd.DataFrame:
        """
        折扣偏好：各渠道的平均折扣率
        折扣率 = 总折扣金额 / (总实收金额 + 总折扣金额)
        """
        agg = df.groupby('平台触点名称')[['实收金额', '折扣金额']].sum()
        agg['discount_rate'] = agg['折扣金额'] / (agg['实收金额'] + agg['折扣金额'])
        return agg[['discount_rate']].sort_values('discount_rate', ascending=False)

    @staticmethod
    def analyze_upt(df: pd.DataFrame) -> pd.DataFrame:
        """
        客件数 (UPT) 分布
        """
        # 按订单聚合件数
        order_items = df.groupby(['平台触点名称', '流水单号'])['销售数量'].sum().reset_index()
        return order_items.groupby('平台触点名称')['销售数量'].mean().sort_values(ascending=False).to_frame(name='avg_upt')

    @staticmethod
    def analyze_calendar_effect(df: pd.DataFrame) -> pd.DataFrame:
        """
        日历效应：分析 工作日/周末/节假日 的表现差异
        """
        df = df.copy()
        df['day_type'] = df['日期'].apply(get_day_type)
        
        # 聚合：渠道 x DayType
        # Metrics: 日均 GMV (因为天数不同，总量不可比), AOV
        
        # 1. 先按 日期 x 渠道 算出日 GMV/订单数
        daily = df.groupby(['日期', 'day_type', '平台触点名称']).agg({
            '实收金额': 'sum',
            '流水单号': 'nunique'
        }).reset_index()
        
        # 2. 再按 DayType x 渠道 算日均
        summary = daily.groupby(['平台触点名称', 'day_type']).agg({
            '实收金额': 'mean', # 日均 GMV
            '流水单号': 'mean'  # 日均单量
        }).reset_index()
        
        # 3. 计算 AOV (总 GMV / 总订单，或者用日均除以日均)
        # 这里用日均值相除
        summary['aov'] = summary['实收金额'] / summary['流水单号']
        
        # Pivot 表格便于展示: Index=渠道, Col=DayType, Value=日均GMV
        pivot = summary.pivot(index='平台触点名称', columns='day_type', values='实收金额')
        
        # 计算 Weekend/Holiday 相对 Workday 的 Uplift
        if 'Workday' in pivot.columns:
            if 'Weekend' in pivot.columns:
                pivot['weekend_uplift'] = (pivot['Weekend'] - pivot['Workday']) / pivot['Workday']
            if 'Holiday' in pivot.columns:
                pivot['holiday_uplift'] = (pivot['Holiday'] - pivot['Workday']) / pivot['Workday']
                
        return pivot.sort_values('Workday', ascending=False)
