import pandas as pd
from datetime import datetime, timedelta

def get_day_type(date_val: datetime) -> str:
    """
    判断日期类型：Workday, Weekend, Holiday
    基于 2025-2026 中国节假日 (简化版)
    """
    d = pd.to_datetime(date_val)
    str_date = d.strftime('%Y-%m-%d')
    
    # 1. 定义法定节假日 (2026 元旦)
    # 假设 2026.1.1 - 1.3 为元旦假期
    holidays = ['2026-01-01', '2026-01-02', '2026-01-03']
    
    if str_date in holidays:
        return 'Holiday'
        
    # 2. 周末 (Saturday=5, Sunday=6)
    if d.dayofweek >= 5:
        # 如果是调休上班日，需剔除 (此处暂忽略调休，假设双休)
        return 'Weekend'
        
    # 3. 工作日
    return 'Workday'

def get_marketing_event(date_val: datetime) -> str:
    """
    识别营销节点
    """
    str_date = date_val.strftime('%Y-%m-%d')
    if str_date == '2025-12-25': return 'Christmas'
    if str_date == '2026-01-01': return 'NewYear'
    return 'Normal'
