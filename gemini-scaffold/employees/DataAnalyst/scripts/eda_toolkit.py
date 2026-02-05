import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from scipy import stats
import matplotlib.pyplot as plt
import os

# --- 1. Data Scouter ---
class DataScouter:
    @staticmethod
    def scan_entities(df, name_col_idx=0, exclude_keywords=None):
        if exclude_keywords is None:
            exclude_keywords = ['客流', '时长', '转化率', '买家数', '渗透率', '曝光率', 'nan', '占比']
        entities = {}
        for idx, val in enumerate(df.iloc[:, name_col_idx]):
            if isinstance(val, str) and len(val) > 1:
                if any(k in val for k in exclude_keywords): continue
                traffic_row = idx + 3
                if traffic_row < len(df) and pd.notna(df.iloc[traffic_row, 13]): 
                     entities[val] = idx
        return entities

    @staticmethod
    def get_metrics_map(df, name_row_idx):
        """
        精准锚定：仅在当前门店名与下一个门店名（或表尾）之间搜索指标。
        """
        metrics = {}
        
        # 1. 寻找下一个实体的行号作为边界
        next_entity_row = len(df)
        blacklist = ['客流', '时长', '转化率', '买家数', '渗透率', '曝光率', 'nan', '占比', '人数', '男性', '女性', '新客', '老客', '未知']
        
        for r in range(name_row_idx + 1, len(df)):
            val = str(df.iloc[r, 0]).strip()
            # 如果这一行看起来像是一个新的店名（不在黑名单中且长度>1）
            if len(val) > 1 and not any(k in val for k in blacklist):
                next_entity_row = r
                break
        
        print(f"[DEBUG] get_metrics_map for row {name_row_idx}: next_entity_row = {next_entity_row}")

        # 2. 在 [name_row_idx, next_entity_row] 范围内搜索指标
        for r in range(name_row_idx + 1, next_entity_row):
            label = str(df.iloc[r, 0]).strip()
            print(f"[DEBUG] Scanning metric label: '{label}'")
            if '客流' in label: metrics['Traffic'] = r
            elif '停留时长' in label: metrics['Dwell'] = r # 调整顺序，优先匹配更精确的“停留时长”
            elif '时长' in label: metrics['Duration'] = r # 后匹配泛化的“时长”
            elif '转化' in label: metrics['Conversion'] = r
            elif 'POS' in label or '买家' in label: metrics['POS_Buyers'] = r
            elif '新客' in label: metrics['New_Buyers'] = r
            elif '老客' in label: metrics['Repeat_Buyers'] = r
            
        return metrics# --- 2. Anomaly Detector ---
class AnomalyDetector:
    @staticmethod
    def detect_volatility_outliers(series, dates, window=2, threshold_pct=0.5):
        """
        基于局部波动率 (Local Volatility) 识别突变点。
        对比当前值与过去 N 个月的移动平均值。
        threshold_pct: 偏离幅度阈值 (0.5 代表 50% 突变)
        """
        vals = np.array(series, dtype=float)
        outliers = []
        
        for i in range(window, len(vals)):
            curr_val = vals[i]
            if pd.isna(curr_val): continue
            
            # 计算局部基线 (前 N 个月的均值)
            local_window = vals[i-window : i]
            # 剔除窗口内的 NaN
            local_window = local_window[~np.isnan(local_window)]
            
            if len(local_window) == 0: continue
            
            baseline = np.mean(local_window)
            if baseline == 0: continue
            
            # 计算偏离度
            deviation = (curr_val - baseline) / baseline
            
            if abs(deviation) > threshold_pct:
                outliers.append({
                    'date': dates[i],
                    'val': curr_val,
                    'z_score': round(deviation, 2), # 这里用 偏离度% 代替 Z-Score 展示
                    'type': 'Surge' if deviation > 0 else 'Plunge',
                    'method': f'Vol({window}M)'
                })
                
        return sorted(outliers, key=lambda x: x['date'])

    @staticmethod
    def detect_outliers(series, dates, threshold=2.0):
        """
        基于 MAD 与 IQR 双重逻辑的异常检测。
        Threshold 调低至 2.0 以捕捉显著的量级跳变。
        """
        vals = np.array(series, dtype=float)
        if len(vals) != len(dates): return []
        
        year_data = {}
        for i, d in enumerate(dates):
            y = d.split('-')[0]
            if y not in year_data: year_data[y] = {'vals': [], 'indices': []}
            year_data[y]['vals'].append(vals[i])
            year_data[y]['indices'].append(i)
            
        outliers = []
        for y, data in year_data.items():
            y_vals = np.array(data['vals'])
            y_indices = data['indices']
            clean_mask = ~np.isnan(y_vals)
            clean_vals = y_vals[clean_mask]
            if len(clean_vals) < 3: continue
            
            # 方法 A: Robust Z-Score (MAD)
            median = np.median(clean_vals)
            mad = np.median(np.abs(clean_vals - median))
            if mad == 0: mad = np.std(clean_vals)
            if mad == 0: continue
            mod_z = 0.6745 * (y_vals - median) / mad
            
            # 方法 B: IQR (作为补充)
            q1, q3 = np.percentile(clean_vals, [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 1.5 * iqr
            upper_bound = q3 + 1.5 * iqr
            
            for local_i, z in enumerate(mod_z):
                v = y_vals[local_i]
                if pd.isna(v): continue
                
                # 触发任一条件即视为异常
                is_anomaly = False
                reason = ""
                if abs(z) > threshold:
                    is_anomaly = True
                    reason = f"Z={z:.2f}"
                elif v < lower_bound or v > upper_bound:
                    is_anomaly = True
                    reason = "IQR"
                
                if is_anomaly:
                    global_idx = y_indices[local_i]
                    outliers.append({
                        'date': dates[global_idx], 
                        'val': v, 
                        'z_score': round(z, 2), 
                        'type': 'High' if v > median else 'Low',
                        'method': reason
                    })
                    
        return sorted(outliers, key=lambda x: x['date'])

# --- 3. Temporal Analysis ---
class TrendTools:
    @staticmethod
    def calculate_slope(y):
        if len(y) < 2: return None
        X = np.arange(len(y)).reshape(-1, 1)
        mask = ~np.isnan(y)
        if mask.sum() < 2: return None
        model = LinearRegression()
        model.fit(X[mask], y[mask])
        return float(model.coef_[0])

# --- 4. Event & Calendar ---
class EventTools:
    HOLIDAY_MONTHS = {2024: [2, 10], 2025: [1, 10]}
    CNY_MONTH_MAP = {2024: 2, 2025: 1}
    @staticmethod
    def is_holiday(date_str):
        try:
            y, m = map(int, date_str.split('-'))
            return m in EventTools.HOLIDAY_MONTHS.get(y, [])
        except: return False
    @staticmethod
    def get_window_data(series, dates, start_idx, end_idx, mode='clean'):
        vals = []
        for i in range(start_idx, end_idx):
            if 0 <= i < len(dates):
                d, v = dates[i], series[i]
                if mode == 'clean':
                    if not EventTools.is_holiday(d): vals.append(v)
                else: vals.append(v)
        return np.array(vals)
    @staticmethod
    def get_aligned_yoy_indices(dates, start_idx, end_idx):
        if start_idx < 0 or end_idx > len(dates): return -1, -1
        standard_start, standard_end = start_idx - 12, end_idx - 12
        if standard_start < 0: return -1, -1
        has_cny, cny_pos = False, -1
        for i in range(start_idx, end_idx):
            y, m = map(int, dates[i].split('-'))
            if y in EventTools.CNY_MONTH_MAP and m == EventTools.CNY_MONTH_MAP[y]:
                has_cny, cny_pos = True, i - start_idx
                break
        if not has_cny: return standard_start, standard_end
        curr_y = int(dates[start_idx].split('-')[0])
        last_y = curr_y - 1
        if last_y not in EventTools.CNY_MONTH_MAP: return standard_start, standard_end
        try:
            last_cny_idx = dates.index(f"{last_y}-{EventTools.CNY_MONTH_MAP[last_y]}")
            alt_start = last_cny_idx - cny_pos
            if alt_start < 0: return standard_start, standard_end
            return alt_start, alt_start + (end_idx - start_idx)
        except: return standard_start, standard_end
    @staticmethod
    def scan_for_break_point(series, min_window=3):
        y, n = np.array(series), len(series)
        best_t, max_t = -1, 0
        for t in range(min_window, n - min_window):
            pre, post = y[:t], y[t:]
            if np.isnan(pre).sum() > len(pre)/2 or np.isnan(post).sum() > len(post)/2: continue
            t_s, _ = stats.ttest_ind(pre, post, nan_policy='omit')
            if abs(t_s) > max_t: max_t, best_t = abs(t_s), t
        return {'best_break_index': best_t, 'max_t_stat': max_t}

# --- 5. Impact Analysis ---
class ImpactAnalyzer:
    @staticmethod
    def analyze_metric(values, dates, anchor_date, window=3):
        """
        按照SOP，执行完全对称的、包含交叉验证的指标影响分析。
        """
        try:
            anchor_idx = dates.index(anchor_date)
        except ValueError:
            return {"error": f"Anchor date {anchor_date} not found in dates."}

        # --- 1. 定义所有窗口 ---
        pre_short_s, pre_short_e = anchor_idx - window, anchor_idx
        post_short_s, post_short_e = anchor_idx + 1, anchor_idx + 1 + window
        pre_full_s, pre_full_e = 0, anchor_idx
        post_full_s, post_full_e = anchor_idx + 1, len(dates)

        yoy_pre_short_s, yoy_pre_short_e = EventTools.get_aligned_yoy_indices(dates, pre_short_s, pre_short_e)
        yoy_post_short_s, yoy_post_short_e = EventTools.get_aligned_yoy_indices(dates, post_short_s, post_short_e)
        yoy_pre_full_s, yoy_pre_full_e = EventTools.get_aligned_yoy_indices(dates, pre_full_s, pre_full_e)
        yoy_post_full_s, yoy_post_full_e = EventTools.get_aligned_yoy_indices(dates, post_full_s, post_full_e)

        # --- 2. 提取各窗口数据 ---
        # 绝对值 (剔除节假日)
        pre_abs_vals = EventTools.get_window_data(values, dates, pre_short_s, pre_short_e, 'clean')
        post_abs_vals = EventTools.get_window_data(values, dates, post_short_s, post_short_e, 'clean')
        yoy_pre_abs_vals = EventTools.get_window_data(values, dates, yoy_pre_short_s, yoy_pre_short_e, 'clean')
        yoy_post_abs_vals = EventTools.get_window_data(values, dates, yoy_post_short_s, yoy_post_short_e, 'clean')
        
        # 趋势 (不剔除节假日)
        pre_trend_short = EventTools.get_window_data(values, dates, pre_short_s, pre_short_e, 'full')
        post_trend_short = EventTools.get_window_data(values, dates, post_short_s, post_short_e, 'full')
        pre_trend_full = EventTools.get_window_data(values, dates, pre_full_s, pre_full_e, 'full')
        post_trend_full = EventTools.get_window_data(values, dates, post_full_s, post_full_e, 'full')
        
        yoy_pre_trend_short = EventTools.get_window_data(values, dates, yoy_pre_short_s, yoy_pre_short_e, 'full')
        yoy_post_trend_short = EventTools.get_window_data(values, dates, yoy_post_short_s, yoy_post_short_e, 'full')
        yoy_pre_trend_full = EventTools.get_window_data(values, dates, yoy_pre_full_s, yoy_pre_full_e, 'full')
        yoy_post_trend_full = EventTools.get_window_data(values, dates, yoy_post_full_s, yoy_post_full_e, 'full')

        # --- 3. 计算分析矩阵 ---
        def safe_mean(vals):
            return np.nanmean(vals) if len(vals) > 0 else np.nan
        
        def safe_pct_change(v_post, v_pre):
            if v_pre and not np.isnan(v_pre) and v_pre != 0:
                return (v_post - v_pre) / v_pre
            return np.nan

        abs_matrix = {
            'pre_avg': safe_mean(pre_abs_vals),
            'post_avg': safe_mean(post_abs_vals),
            'yoy_pre_avg': safe_mean(yoy_pre_abs_vals),
            'yoy_post_avg': safe_mean(yoy_post_abs_vals),
        }
        abs_matrix['change_pct'] = safe_pct_change(abs_matrix['post_avg'], abs_matrix['pre_avg'])
        abs_matrix['yoy_change_pct'] = safe_pct_change(abs_matrix['yoy_post_avg'], abs_matrix['yoy_pre_avg'])
        
        trend_matrix = {
            'pre_slope_short': TrendTools.calculate_slope(pre_trend_short) or np.nan,
            'post_slope_short': TrendTools.calculate_slope(post_trend_short) or np.nan,
            'pre_slope_full': TrendTools.calculate_slope(pre_trend_full) or np.nan,
            'post_slope_full': TrendTools.calculate_slope(post_trend_full) or np.nan,
            
            'yoy_pre_slope_short': TrendTools.calculate_slope(yoy_pre_trend_short) or np.nan,
            'yoy_post_slope_short': TrendTools.calculate_slope(yoy_post_trend_short) or np.nan,
            'yoy_pre_slope_full': TrendTools.calculate_slope(yoy_pre_trend_full) or np.nan,
            'yoy_post_slope_full': TrendTools.calculate_slope(yoy_post_trend_full) or np.nan,
        }
        
        return {
            'absolute_matrix': abs_matrix,
            'trend_matrix': trend_matrix
        }

# --- 6. Attribution ---
class AttributionAnalyzer:
    @staticmethod
    def calculate_absolute_shift(pre_counts, post_counts):
        if not pre_counts or not post_counts: return pd.DataFrame()
        cats = set(pre_counts.keys()) | set(post_counts.keys())
        data = [{'Category': c, 'Pre_Count': pre_counts.get(c, 0), 'Post_Count': post_counts.get(c, 0), 'Abs_Change': post_counts.get(c, 0) - pre_counts.get(c, 0)} for c in cats]
        return pd.DataFrame(data).sort_values('Abs_Change', ascending=False) if data else pd.DataFrame()

# --- 7. Visualization ---
class ChartGenerator:
    @staticmethod
    def plot_multi_metric_trend(store_name, dates, metrics_data, anchor_date, outliers, output_path):
        fig, axes = plt.subplots(len(metrics_data), 1, figsize=(10, 3 * len(metrics_data)), sharex=True)
        if len(metrics_data) == 1: axes = [axes]
        try: event_idx = dates.index(anchor_date)
        except: event_idx = None
        x = np.arange(len(dates))
        for i, (m_name, vals) in enumerate(metrics_data.items()):
            ax = axes[i]
            ax.plot(x, vals, marker='o', markersize=4, label=m_name)
            if m_name in outliers:
                for out in outliers[m_name]:
                    try: ax.scatter(dates.index(out['date']), out['val'], color='red', s=50, zorder=5)
                    except: pass
            if event_idx: ax.axvline(event_idx, color='red', linestyle='--', alpha=0.7)
            ax.set_title(f"{store_name} - {m_name}")
            ax.grid(True, alpha=0.3)
            if i == 0: ax.legend()
        plt.xticks(x[::3], dates[::3], rotation=45)
        plt.tight_layout()
        plt.savefig(output_path); plt.close()
    @staticmethod
    def plot_slope_scissors(store_name, curr_pre, curr_post, last_pre, last_post, bench_pre, bench_post, output_path):
        plt.figure(figsize=(9, 6))
        if all(v is not None for v in [bench_pre, bench_post]):
            plt.plot([0, 1], [bench_pre, bench_post], color='#1f77b4', linestyle='--', marker='s', label='Market')
        if all(v is not None for v in [last_pre, last_post]):
            plt.plot([0, 1], [last_pre, last_post], color='gray', linestyle='--', marker='o', alpha=0.5, label='Last Year')
        if all(v is not None for v in [curr_pre, curr_post]):
            plt.plot([0, 1], [curr_pre, curr_post], color='#d62728', linewidth=3, marker='o', label='Store (Curr)')
        plt.xticks([0, 1], ['Pre', 'Post']); plt.title(f"{store_name}: Slope Scissors"); plt.legend(); plt.grid(True, alpha=0.3)
        plt.tight_layout(); plt.savefig(output_path); plt.close()
    @staticmethod
    def plot_butterfly_chart(df, output_path, title):
        if df.empty: return
        plt.figure(figsize=(10, 6))
        df = df.sort_values('Abs_Change')
        plt.barh(df['Category'], df['Abs_Change'], color=['green' if x>0 else 'red' for x in df['Abs_Change']])
        plt.axvline(0, color='black', linewidth=0.8); plt.title(title); plt.grid(axis='x', alpha=0.3)
        plt.tight_layout(); plt.savefig(output_path); plt.close()
    @staticmethod
    def plot_efficiency_quadrant(store_data, output_path):
        plt.figure(figsize=(10, 8))
        x, y, labels = [], [], []
        for s in store_data:
            x.append(s['metrics'].get('Traffic', {}).get('mom_pct', 0))
            y.append(s['metrics'].get('POS_Buyers', {}).get('mom_pct', 0))
            labels.append(s['name'])
        plt.scatter(x, y, s=150, alpha=0.7); plt.axhline(0, color='black', ls='--'); plt.axvline(0, color='black', ls='--')
        for i, txt in enumerate(labels): plt.annotate(txt, (x[i], y[i]))
        plt.title("Efficiency Quadrant"); plt.xlabel("Traffic MoM%"); plt.ylabel("POS MoM%"); plt.grid(True, alpha=0.3)
        plt.tight_layout(); plt.savefig(output_path); plt.close()
