import json
import os
import pandas as pd

def format_currency(x):
    return f"¥{x:,.1f}"

def format_pct(x):
    return f"{x:.1%}"

def generate_single_channel_report(channel_name, data):
    lines = []
    lines.append(f"# 渠道深度诊断报告：{channel_name}")
    lines.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")
    
    # 1. 核心指标看板
    m = data['metrics']
    p = data['promo_stat']
    lines.append("## 1. 核心经营指标 (Key Metrics)")
    lines.append("| 指标维度 | 数值 | 行业参考/含义 |")
    lines.append("| :--- | :--- | :--- |")
    lines.append(f"| **GMV 规模** | {format_currency(m['gmv'])} | 渠道总实收金额 |")
    lines.append(f"| **客单价 (AOV)** | {format_currency(m['aov'])} | 平均每单支付金额 |")
    lines.append(f"| **客件数 (UPT)** | {m['total_items']/m['order_count']:.1f} 件 | 平均每单商品数 |")
    lines.append(f"| **折扣率** | {format_pct(p['discount_rate'])} | 促销力度 |")
    lines.append(f"| **促销渗透率** | {format_pct(p['promo_order_ratio'])} | 多少订单用了促销 |")
    lines.append(f"| **促销效率 (Uplift)** | {format_pct(p['promo_uplift'])} | 促销单对比正价单的客单溢价 |")
    lines.append("")
    
    # 2. 货品结构
    lines.append("## 2. 货品结构分析 (Merchandise)")
    lines.append("### 2.1 头部贡献 (Top 5 Categories)")
    lines.append("| 品类编码 | 商品名称 (Top SKU) | 销售额贡献 | 销量 |")
    lines.append("| :--- | :--- | :--- | :--- |")
    for item in data['top_categories']:
        lines.append(f"| {item['小类编码']} | {item['商品名称']} | {format_currency(item['实收金额'])} | {item['销售数量']} |")
    lines.append("")
    
    # 3. 场景下钻 (Cubes)
    lines.append("## 3. 场景切片下钻 (Scenario Drill-down)")
    
    for cube in data['cubes']:
        slice_name = cube.get('slice_name', 'Unknown Slice')
        lines.append(f"### 场景: {slice_name}")
        
        # Cube Metrics
        cm = cube['metrics']
        lines.append(f"**场景画像**: AOV {format_currency(cm['aov'])} | UPT {cm['total_items']/cm['order_count']:.1f} | 样本量 {cm['order_count']}单")
        
        # Clustering
        lines.append("\n**消费模式构成 (Clustering)**:")
        for c in cube['clusters']:
            lines.append(f"- **{c['label']}**: 占比 {format_pct(c['share'])}")
            
        # Products
        lines.append("\n**核心爆品 (Top Drivers)**:")
        for name, gmv in list(cube['top_items'].items())[:5]:
            lines.append(f"- {name}: {format_currency(gmv)}")
            
        # Associations
        if cube['associations']:
            lines.append("\n**连带特征 (Co-occurrence)**:")
            for assoc in cube['associations']:
                lines.append(f"- {assoc}")
        
        lines.append("\n---\n")

    return "\n".join(lines)

import sys
from datetime import datetime

def main():
    base_dir = os.getcwd()
    json_path = os.path.join(base_dir, "order_analysis/reports/data/analysis_data.json")
    output_dir = os.path.join(base_dir, "order_analysis/reports/channels")
    
    with open(json_path, 'r') as f:
        full_data = json.load(f)
        
    for ch_name, ch_data in full_data['channels'].items():
        if not ch_data['metrics']: continue # Skip empty
        
        print(f"Generating report for {ch_name}...")
        report_content = generate_single_channel_report(ch_name, ch_data)
        
        filename = f"report_{ch_name}.md"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(report_content)

if __name__ == "__main__":
    main()
