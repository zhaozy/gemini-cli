import pandas as pd
from typing import Dict, Any, List

class TemporalStrategy:
    """
    时空生活嵌入分析
    """
    
    @staticmethod
    def calc_overview(df: pd.DataFrame) -> Dict[str, Any]:
        """
        计算时空基础分布 (日类型 + 时段)
        """
        # 1. 日类型分布
        day_stats = df.groupby('day_type').agg({
            '流水单号': 'nunique',
            '实收金额': 'sum'
        }).reset_index()
        day_stats['order_share'] = day_stats['流水单号'] / day_stats['流水单号'].sum()
        
        # 2. 时段分布
        period_stats = df.groupby('period').agg({
            '流水单号': 'nunique',
            '实收金额': 'sum'
        }).reset_index()
        period_stats['order_share'] = period_stats['流水单号'] / period_stats['流水单号'].sum()
        
        return {
            "day_distribution": day_stats.to_dict('records'),
            "period_distribution": period_stats.to_dict('records')
        }

    @staticmethod
    def calc_fluctuation(df: pd.DataFrame) -> Dict[str, float]:
        """
        计算异动系数
        """
        daily_orders = df.groupby(['日期', 'day_type'])['流水单号'].nunique().reset_index()
        
        avg_weekend = daily_orders[daily_orders['day_type'] == 'Weekend']['流水单号'].mean()
        avg_workday = daily_orders[daily_orders['day_type'] == 'Workday']['流水单号'].mean()
        avg_holiday = daily_orders[daily_orders['day_type'] == 'Holiday']['流水单号'].mean()
        
        # 处理分母为0的情况
        weekend_coef = avg_weekend / avg_workday if avg_workday and avg_workday > 0 else 1.0
        holiday_coef = avg_holiday / avg_workday if avg_workday and avg_workday > 0 else 1.0
        
        return {
            "weekend_coef": float(weekend_coef) if not pd.isna(weekend_coef) else 1.0,
            "holiday_coef": float(holiday_coef) if not pd.isna(holiday_coef) else 1.0
        }

    @staticmethod
    def calc_tgi_heatmap(df: pd.DataFrame) -> Dict[str, List[Dict]]:
        """
        计算各时段 TGI > 150 的 Top 商品
        """
        # 1. 全局占比
        total_gmv = df['实收金额'].sum()
        cat_gmv = df.groupby('小类编码')['实收金额'].sum()
        global_share = cat_gmv / total_gmv
        
        # 商品名称映射
        code_name_map = df.groupby('小类编码')['商品名称'].agg(lambda x: x.mode()[0]).to_dict()
        
        heatmap = {}
        periods = ['1_Morning', '2_Noon', '3_Afternoon', '4_Evening', '5_LateNight']
        
        for p in periods:
            p_df = df[df['period'] == p]
            if p_df.empty: continue
            
            p_total = p_df['实收金额'].sum()
            if p_total == 0: continue
            
            p_cat_gmv = p_df.groupby('小类编码')['实收金额'].sum()
            p_share = p_cat_gmv / p_total
            
            # 计算 TGI
            # TGI = (时段占比 / 全局占比) * 100
            # 只计算在该时段有销量的
            valid_cats = p_share.index
            tgi_series = (p_share / global_share.loc[valid_cats]) * 100
            
            # 筛选 TGI > 100 (放宽) 且在该时段 GMV 占比 > 0.5% (放宽)
            # 或者直接取 Top 3
            high_tgi = tgi_series.sort_values(ascending=False).head(3)
            
            items = []
            for code, tgi_val in high_tgi.items():
                if tgi_val < 100: continue # 至少要大于平均水平
                items.append({
                    "sku": code_name_map.get(code, str(code)),
                    "tgi": float(tgi_val),
                    "share": float(p_share[code])
                })
            
            if items:
                heatmap[p] = items
            
        return heatmap

    @staticmethod
    def find_top_scenarios(df: pd.DataFrame) -> List[Dict]:
        """
        寻找 GMV 最高的 Top 5 场景 (DayType x Period)
        """
        # 聚合
        scenarios = df.groupby(['day_type', 'period']).agg({
            '实收金额': 'sum',
            '流水单号': 'nunique',
            '销售数量': 'sum',
            '折扣金额': 'sum'
        }).reset_index()
        
        scenarios['aov'] = scenarios['实收金额'] / scenarios['流水单号']
        scenarios['upt'] = scenarios['销售数量'] / scenarios['流水单号']
        scenarios['raw_gmv'] = scenarios['实收金额'] + scenarios['折扣金额']
        scenarios['disc_rate'] = scenarios['折扣金额'] / (scenarios['raw_gmv'] + 1e-9)
        
        # 排序
        top5 = scenarios.sort_values('实收金额', ascending=False).head(5)
        
        results = []
        for _, row in top5.iterrows():
            results.append({
                "id": f"{row['day_type']}_{row['period']}",
                "gmv": float(row['实收金额']),
                "features": {
                    "aov": float(row['aov']),
                    "upt": float(row['upt']),
                    "discount_rate": float(row['disc_rate'])
                }
            })
            
        return results
