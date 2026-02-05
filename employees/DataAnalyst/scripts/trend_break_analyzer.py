import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import argparse
import os

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def analyze_trend_break(file_path, date_col, value_col, event_date, output_dir, window_months=6):
    """
    通用趋势断点分析工具
    """
    print(f"Loading data from {file_path}...")
    df = pd.read_csv(file_path)
    
    # 简单的日期处理，假设传入的是 Month 索引或者 Date 字符串
    # 这里为了通用性，我们假设数据已经按时间排序，且有一个标识时间的列
    # 如果 date_col 是数字（如 1-12月），直接用。如果是日期字符串，转 datetime
    
    try:
        df['dt_numeric'] = pd.to_numeric(df[date_col])
        is_numeric_date = True
    except:
        df['dt_obj'] = pd.to_datetime(df[date_col])
        df = df.sort_values('dt_obj')
        df['dt_numeric'] = np.arange(len(df)) # Create a sequence 0, 1, 2...
        is_numeric_date = False

    # 确定 Event Date 的位置
    if is_numeric_date:
        event_idx = df[df[date_col] == float(event_date)].index[0]
        event_val_numeric = float(event_date)
    else:
        # 假设 event_date 是 'YYYY-MM-DD'
        target_ts = pd.to_datetime(event_date)
        # Find closest date
        event_idx = (df['dt_obj'] - target_ts).abs().idxmin()
        event_val_numeric = df.loc[event_idx, 'dt_numeric']

    print(f"Event detected at index {event_idx} (Value: {event_date})")

    # 定义拟合窗口 (Pre-Event)
    # 选取 event 之前的 window_months 个点
    start_fit_idx = max(0, event_idx - window_months)
    end_fit_idx = event_idx # 不包含 event 当点，或者包含视业务定义。这里不包含，作为测试集
    
    fit_data = df.iloc[start_fit_idx : end_fit_idx]
    
    if len(fit_data) < 2:
        print("Error: Not enough data points before event to fit a trend.")
        return

    X_fit = fit_data['dt_numeric'].values.reshape(-1, 1)
    y_fit = fit_data[value_col].values
    
    model = LinearRegression()
    model.fit(X_fit, y_fit)
    
    slope = model.coef_[0]
    intercept = model.intercept_
    r_squared = model.score(X_fit, y_fit)
    
    print(f"Pre-event Trend Slope: {slope:.4f}")
    print(f"Model R^2: {r_squared:.4f}")

    # 预测 (Project) - 预测范围：从拟合开始到数据结束
    X_all = df['dt_numeric'].values.reshape(-1, 1)
    df['predicted_inertia'] = model.predict(X_all)
    
    # 计算 Post-Event 的统计量
    post_data = df.iloc[event_idx:]
    if len(post_data) > 0:
        # Saved Loss / Excess Gain
        post_data = post_data.copy()
        post_data['diff'] = post_data[value_col] - post_data['predicted_inertia']
        total_saved = post_data['diff'].sum()
        avg_saved = post_data['diff'].mean()
        
        # Trend Reversal Rate (TRR)
        # Fit a new line for post data
        if len(post_data) >= 2:
            X_post = post_data['dt_numeric'].values.reshape(-1, 1)
            y_post = post_data[value_col].values
            model_post = LinearRegression()
            model_post.fit(X_post, y_post)
            slope_post = model_post.coef_[0]
            trr = slope_post - slope
        else:
            slope_post = np.nan
            trr = np.nan
    else:
        total_saved = 0
        trr = np.nan

    # --- Visualization ---
    plt.figure(figsize=(12, 6))
    
    # Plot Actual
    plt.plot(df[date_col], df[value_col], 'o-', label='Actual Data', color='#1f77b4', linewidth=2.5)
    
    # Plot Inertia (Prediction)
    plt.plot(df[date_col], df['predicted_inertia'], '--', label=f'Inertia Trend (Slope={slope:.2f})', color='gray', alpha=0.7)
    
    # Mark Event
    plt.axvline(x=event_idx, color='red', linestyle=':', linewidth=2, label='Intervention Event')
    
    # Highlight Scissor Gap
    # Only fill after event
    x_fill = df[date_col].iloc[event_idx:]
    y1_fill = df[value_col].iloc[event_idx:]
    y2_fill = df['predicted_inertia'].iloc[event_idx:]
    
    # Determine color based on gain or loss
    fill_color = 'green' if total_saved > 0 else 'red'
    label_gap = f"{ 'Saved' if total_saved > 0 else 'Lost' }: {abs(total_saved):.0f}"
    
    plt.fill_between(x_fill, y1_fill, y2_fill, alpha=0.15, color=fill_color, label=label_gap)
    
    plt.title(f'Trend Break Analysis: {value_col}\nTRR (Trend Reversal Rate): {trr:.4f}', fontsize=14)
    plt.xlabel(date_col)
    plt.ylabel(value_col)
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.3)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    out_file = os.path.join(output_dir, f'trend_break_{value_col}.png')
    plt.savefig(out_file)
    print(f"Chart saved to {out_file}")
    
    # --- Generate Report Snippet ---
    report_file = os.path.join(output_dir, f'trend_break_report.md')
    with open(report_file, 'w') as f:
        f.write(f"## Trend Break Analysis for {value_col}\n")
        f.write(f"- **Event Date**: {event_date}\n")
        f.write(f"- **Pre-Event Trend**: Slope = {slope:.4f} (R2={r_squared:.2f})\n")
        f.write(f"- **Post-Event Trend**: Slope = {slope_post:.4f}\n")
        f.write(f"- **Trend Reversal Rate (TRR)**: {trr:.4f}\n")
        f.write(f"- **Cumulative Impact (Saved/Gained)**: {total_saved:.2f}\n")
        
    print("Analysis complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='General Trend Break Analyzer')
    parser.add_argument('--input', required=True, help='Path to CSV file')
    parser.add_argument('--date_col', required=True, help='Column name for date/time')
    parser.add_argument('--value_col', required=True, help='Column name for metric value')
    parser.add_argument('--event_date', required=True, help='Value in date_col representing the event')
    parser.add_argument('--output', required=True, help='Output directory')
    parser.add_argument('--window', type=int, default=6, help='Months/periods to fit before event')
    
    args = parser.parse_args()
    
    analyze_trend_break(args.input, args.date_col, args.value_col, args.event_date, args.output, args.window)
