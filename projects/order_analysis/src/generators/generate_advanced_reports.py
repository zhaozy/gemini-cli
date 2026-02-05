import json
import os
import pandas as pd
from datetime import datetime

def fmt_c(x): return f"¥{x:,.1f}"
def fmt_p(x): return f"{x:.1%}"

def get_report_markdown(ch, data):
    # 提取模块
    pm = data['product_strategy']
    pd = data['pricing_diagnosis']
    bq = data['basket_quality']
    ti = data['temporal_insight']
    
    lines = []
    lines.append(f"# 全链路经营诊断报告 (V3): {ch}")
    lines.append(f"> 分析深度: 数据科学家 + 咨询顾问级 | 日期: {datetime.now().strftime('%Y-%m-%d')}")
    lines.append("")

    # --- 1. 商品战略人格 ---
    lines.append("## 一、商品战略人格 (Product Strategy Matrix)")
    lines.append("> **指标口径**:")
    lines.append("> - **渗透率**: 包含该SKU的订单数 / 总订单数。反映流量深度。")
    lines.append("> - **带动系数**: 订单总件数 - 1。反映该SKU拉动关联消费的能力。")
    lines.append("> - **刺客 (Assassin)**: 低件单价且带动能力低于中位数的流量品，消耗履约成本。")
    lines.append("")
    
    lines.append("| 商品名称 | 渗透率 | 带动系数 | 件单价 | 战略人格 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for item in pm[:15]:
        lines.append(f"| {item['sku']} | {fmt_p(item['penetration'])} | {item['affinity']:.2f} | {fmt_c(item['avg_price'])} | {item['role']} |")
    lines.append("")
    
    top_affinity = ", ".join([i['sku'] for i in sorted(pm, key=lambda x: x['affinity'], reverse=True)[:3]])
    has_assassin = "有" if any("Assassin" in i['role'] for i in pm[:5]) else "无"
    lines.append(f"> 💡 **客观解读**: 该渠道渗透率排名前五的单品中，**{has_assassin}** 显著的“履约刺客”现象。带动系数最高的前三位商品分别为: {top_affinity}。")
    lines.append("")

    # --- 2. 价格引力 ---
    lines.append("## 二、价格引力与偏态 (Pricing Skewness)")
    lines.append("> **指标口径**:")
    lines.append("> - **偏态系数 (Skewness)**: (均值 - 众数) / 标准差。正值越大，说明被低客单订单“拖累”越严重。")
    lines.append("> - **促销效率 (Proxy)**: 深折单AOV / 正价单AOV。")
    lines.append("")
    
    lines.append("| 指标 | 均值 (Mean) | 中位数 (Median) | 众数 (Mode) | 偏态系数 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    lines.append(f"| 客单价 (AOV) | {fmt_c(pd['stats']['mean'])} | {fmt_c(pd['stats']['median'])} | {fmt_c(pd['stats']['mode'])} | {pd['skewness_index']:.2f} |")
    lines.append("")
    
    skew_desc = "正偏态" if pd['skewness_index'] > 0 else "负偏态"
    mode_desc = "众数显著低于均值，说明存在大量低价值小单。" if pd['stats']['mode'] < pd['stats']['mean'] else "分布相对均衡。"
    lines.append(f"> 💡 **客观解读**: AOV 呈现 **{skew_desc}** 分布。{mode_desc} 深折订单客单价为正价订单的 **{pd['promo_elasticity_proxy']:.2f}倍**。")
    lines.append("")

    # --- 3. 篮筐品质 ---
    lines.append("## 三、篮筐品质与订单指纹 (Basket Analysis)")
    lines.append("> **指标口径**:")
    lines.append("> - **孤儿单率**: 仅包含1件商品的订单比例。反映配送成本风险。")
    lines.append("> - **3D 聚类**: 基于 [件数, 类目数, GMV] 进行的无监督空间划分。")
    lines.append("")
    
    lines.append(f"- **孤儿单占比**: {fmt_p(bq['orphan_ratio'])}")
    culprits_str = ", ".join([f"{k} ({fmt_p(v)})" for k,v in list(bq['culprits'].items())[:3]])
    lines.append(f"- **孤儿单元凶 Top 3**: {culprits_str}")
    lines.append("")
    
    lines.append("| 客群指纹 | 占比 | 平均件数 | 平均类目数 | 平均客单 |")
    lines.append("| :--- | :--- | :--- | :--- | :--- |")
    for seg in bq['segments']:
        lines.append(f"| {seg['label']} | {fmt_p(seg['share'])} | {seg['avg_items']:.1f} | {seg['avg_cats']:.1f} | {fmt_c(seg['avg_aov'])} |")
    lines.append("")

    # --- 4. 时空生活 ---
    lines.append("## 四、时空生活嵌入 (Temporal TGI)")
    lines.append("> **指标口径**:")
    lines.append("> - **TGI 指数**: (时段内品类占比 / 全天该品类占比) * 100。>100 表示该时段对该品类有显著偏好。")
    lines.append("")
    
    lines.append("| 时段 (Period) | 心智商品 (High TGI SKUs) |")
    lines.append("| :--- | :--- |")
    for period, items in ti['period_tgi'].items():
        item_str = ", ".join([f"{i['name']} (TGI {i['tgi']:.0f})" for i in items])
        lines.append(f"| {period} | {item_str} |")
    lines.append("")
    
    weekend_type = "工作区/补缺型" if ti['weekend_fluctuation'] < 1 else "生活/囤货型"
    lines.append(f"> 💡 **客观解读**: 周末异动系数为 **{ti['weekend_fluctuation']:.2f}**。该仓具有明显的‘**{weekend_type}**’特征。")
    
    return "\n".join(lines)

def get_report_html(ch, md_content):
    # 简单转换，保留 CSS 样式
    import markdown
    html_body = markdown.markdown(md_content, extensions=['tables'])
    
    html = f"""
    <html>
    <head>
        <meta charset="utf-8"><title>V3诊断: {ch}</title>
        <style>
            body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; max-width: 1000px; margin: 0 auto; padding: 40px; color: #24292e; background-color: #f6f8fa; }}
            h1, h2, h3 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
            th, td {{ padding: 10px; border: 1px solid #dfe2e5; }}
            th {{ background: #f6f8fa; }}
            blockquote {{ border-left: 4px solid #dfe2e5; color: #6a737d; padding-left: 1em; margin: 20px 0; }}
            code {{ background-color: rgba(27,31,35,.05); padding: .2em .4em; border-radius: 3px; }}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return html

def main():
    base_dir = os.getcwd()
    json_path = os.path.join(base_dir, "order_analysis/reports/data/analysis_cube_v3.json")
    output_dir = os.path.join(base_dir, "order_analysis/reports/diagnostics_v3")
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    
    with open(json_path, 'r') as f:
        data = json.load(f)
    for ch, ch_data in data['channels'].items():
        print(f"Generating V3 Diagnostic for {ch}...")
        
        # 1. Generate Markdown
        md_content = get_report_markdown(ch, ch_data)
        md_path = os.path.join(output_dir, f"diagnostic_{ch}.md")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(md_content)
            
        # 2. Generate HTML
        html_content = get_report_html(ch, md_content)
        html_path = os.path.join(output_dir, f"diagnostic_{ch}.html")
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__": main()