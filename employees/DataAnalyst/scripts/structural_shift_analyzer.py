import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

# 设置绘图风格
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'SimHei', 'PingFang SC']
plt.rcParams['axes.unicode_minus'] = False

def analyze_structural_shift(input_file, period_col, category_col, value_col, pre_label, post_label, output_dir):
    """
    结构变迁分析工具：生成瀑布图和贡献度表
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    
    # 过滤出只包含 Pre 和 Post 标签的数据
    df_filtered = df[df[period_col].isin([pre_label, post_label])].copy()
    
    # 聚合数据 (Group by Period + Category)
    # 确保 Category 是唯一的
    agg_df = df_filtered.groupby([period_col, category_col])[value_col].sum().reset_index()
    
    # 转 Pivot Table: Index=Category, Columns=Period
    pivot = agg_df.pivot(index=category_col, columns=period_col, values=value_col).fillna(0)
    
    if pre_label not in pivot.columns or post_label not in pivot.columns:
        print(f"Error: Specified periods '{pre_label}' or '{post_label}' not found in data.")
        return

    # 计算变动
    pivot['Pre'] = pivot[pre_label]
    pivot['Post'] = pivot[post_label]
    pivot['Diff'] = pivot['Post'] - pivot['Pre']
    pivot['Abs_Diff'] = pivot['Diff'].abs()
    
    # 计算贡献度 (Contribution %)
    total_pre = pivot['Pre'].sum()
    total_post = pivot['Post'].sum()
    total_diff = total_post - total_pre
    
    # 排序：按绝对变动量倒序，找出影响最大的因子
    pivot = pivot.sort_values('Abs_Diff', ascending=False)
    
    # 保存分析表格
    out_csv = os.path.join(output_dir, 'structural_shift_analysis.csv')
    pivot.to_csv(out_csv)
    print(f"Analysis data saved to {out_csv}")
    
    print("\n--- Top Contributors to Change ---")
    print(pivot[['Pre', 'Post', 'Diff']].head())
    print(f"\nTotal Pre: {total_pre:.2f}")
    print(f"Total Post: {total_post:.2f}")
    print(f"Total Change: {total_diff:.2f}")

    # --- Visualization: Waterfall Chart ---
    # 瀑布图逻辑：
    # Bar 1: Pre Total
    # Bar 2..N: Top Categories Diffs
    # Bar N+1: Others Diffs (if many categories)
    # Bar Last: Post Total
    
    # 为了图表清晰，只取 Top 10 变动最大的，其他的归为 "Others"
    top_n = 10
    if len(pivot) > top_n:
        top_cats = pivot.iloc[:top_n]
        others_diff = pivot.iloc[top_n:]['Diff'].sum()
        
        # 构建绘图数据
        plot_data = []
        plot_data.append({'Label': f"{pre_label} Total", 'Value': total_pre, 'Type': 'Total'})
        
        for cat, row in top_cats.iterrows():
            plot_data.append({'Label': cat, 'Value': row['Diff'], 'Type': 'Delta'})
            
        plot_data.append({'Label': 'Others', 'Value': others_diff, 'Type': 'Delta'})
        plot_data.append({'Label': f"{post_label} Total", 'Value': total_post, 'Type': 'Total'})
        
    else:
        # 少于 10 个，全部展示
        plot_data = []
        plot_data.append({'Label': f"{pre_label} Total", 'Value': total_pre, 'Type': 'Total'})
        
        for cat, row in pivot.iterrows():
            plot_data.append({'Label': cat, 'Value': row['Diff'], 'Type': 'Delta'})
            
        plot_data.append({'Label': f"{post_label} Total", 'Value': total_post, 'Type': 'Total'})
        
    # 绘制瀑布图
    plt.figure(figsize=(14, 8))
    
    # 计算每个柱子的底部位置 (running total)
    running_total = 0
    xticks = []
    xlabels = []
    
    # 第一个柱子：Pre Total
    plt.bar(0, plot_data[0]['Value'], color='gray', label='Total')
    running_total = plot_data[0]['Value']
    xticks.append(0)
    xlabels.append(plot_data[0]['Label'])
    
    # 中间的柱子
    for i, item in enumerate(plot_data[1:-1]):
        val = item['Value']
        x = i + 1
        color = 'green' if val >= 0 else 'red'
        
        # 瀑布图的核心：柱子悬空
        # 如果是正增长，底部是之前的 total
        # 如果是负增长，顶部是之前的 total (所以底部是 total + val)
        if val >= 0:
            bottom = running_total
        else:
            bottom = running_total + val
            
        plt.bar(x, abs(val), bottom=bottom, color=color)
        
        # 更新 running total
        running_total += val
        
        xticks.append(x)
        xlabels.append(item['Label'])
        
        # 标注数值
        plt.text(x, bottom + abs(val) + (total_pre * 0.01), f"{val:+.0f}", ha='center', fontsize=9)
        
    # 最后一个柱子：Post Total
    last_idx = len(plot_data) - 1
    plt.bar(last_idx, plot_data[-1]['Value'], color='gray')
    xticks.append(last_idx)
    xlabels.append(plot_data[-1]['Label'])
    
    # 画连接线
    # (省略复杂连接线，保持简洁)
    
    plt.xticks(xticks, xlabels, rotation=45, ha='right')
    plt.ylabel(value_col)
    plt.title(f'Structural Shift Waterfall: {pre_label} -> {post_label}\nNet Change: {total_diff:+.2f}', fontsize=14)
    plt.grid(axis='y', linestyle='--', alpha=0.3)
    
    out_img = os.path.join(output_dir, 'structural_shift_waterfall.png')
    plt.tight_layout()
    plt.savefig(out_img)
    print(f"Chart saved to {out_img}")
    
    # --- Generate Report ---
    report_file = os.path.join(output_dir, 'structural_shift_report.md')
    with open(report_file, 'w') as f:
        f.write(f"# Structural Shift Analysis\n")
        f.write(f"## Overview\n")
        f.write(f"- **{pre_label}**: {total_pre:,.2f}\n")
        f.write(f"- **{post_label}**: {total_post:,.2f}\n")
        f.write(f"- **Net Change**: {total_diff:+,.2f} ({(total_diff/total_pre)*100:+.1f}%)\n")
        
        f.write(f"\n## Top Contributors to Change\n")
        f.write("| Category | Pre | Post | Change | Status |\n")
        f.write("| :--- | :--- | :--- | :--- | :--- |\n")
        for cat, row in pivot.head(5).iterrows():
            status = "GROWTH" if row['Diff'] > 0 else "DECLINE"
            f.write(f"| **{cat}** | {row['Pre']:,.0f} | {row['Post']:,.0f} | **{row['Diff']:+,.0f}** | {status} |\n")
            
    print("Analysis complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Structural Shift Analyzer')
    parser.add_argument('--input', required=True, help='Path to CSV file (Long Format)')
    parser.add_argument('--period_col', required=True, help='Column name for Period (e.g., Year, Month)')
    parser.add_argument('--category_col', required=True, help='Column name for Category/Segment')
    parser.add_argument('--value_col', required=True, help='Column name for Value (e.g., Traffic, Sales)')
    parser.add_argument('--pre_label', required=True, help='Label of the Pre period (e.g., "2024")')
    parser.add_argument('--post_label', required=True, help='Label of the Post period (e.g., "2025")')
    parser.add_argument('--output', required=True, help='Output directory')
    
    args = parser.parse_args()
    
    analyze_structural_shift(args.input, args.period_col, args.category_col, args.value_col, args.pre_label, args.post_label, args.output)
