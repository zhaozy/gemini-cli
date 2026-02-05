import json
import os
import pandas as pd
from datetime import datetime

def format_currency(x):
    return f"¥{x:,.1f}"

def format_pct(x):
    return f"{x:.1%}"

class ReportNarrator:
    """
    负责生成咨询风格的洞察文案
    """
    @staticmethod
    def diagnose_channel(metrics, promo):
        insights = []
        
        # 1. 规模定位
        if metrics['orders'] > 10000:
            insights.append("该渠道属于**高频主力渠道**，承担了主要的流量入口职能。")
        else:
            insights.append("该渠道属于**细分/长尾渠道**，侧重于特定客群的覆盖。")
            
        # 2. 质量诊断
        if metrics['aov'] < 40:
            insights.append("客单价偏低 (Low AOV)，建议通过**连带推荐**或**满减门槛提升**来拉升客单。")
        elif metrics['aov'] > 80:
            insights.append("客单价较高 (High AOV)，拥有优质的高价值客群，应重点维护**服务体验**和**商品品质**。")
            
        # 3. 促销诊断
        uplift = (promo['elasticity'].get('High', {}).get('实收金额', 0) - promo['elasticity'].get('NoPromo', {}).get('实收金额', 0))
        # 简化版 Uplift 计算，直接用 discount_rate 判断
        if metrics['discount_rate'] > 0.15:
            insights.append("促销依赖度极高 (>15%)，需警惕**毛利侵蚀**风险。")
        
        return "\n\n".join([f"> 💡 **专家诊断**: {i}" for i in insights])

def generate_html_report(channel_name, data):
    m = data['dashboard']['overview']
    p_dist = data['dashboard']['price_bands']
    
    # 构建 HTML 内容
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>深度经营诊断: {channel_name}</title>
        <style>
            body {{ font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; max-width: 1000px; margin: 0 auto; padding: 40px; color: #24292e; background-color: #f6f8fa; }}
            .container {{ background: white; padding: 40px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.12); }}
            h1 {{ border-bottom: 1px solid #eaecef; padding-bottom: 0.5em; }}
            h2 {{ margin-top: 40px; color: #0366d6; }}
            .metric-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 30px; }}
            .metric-card {{ background: #f1f8ff; padding: 20px; border-radius: 6px; text-align: center; border: 1px solid #c8e1ff; }}
            .metric-val {{ font-size: 24px; font-weight: bold; color: #0366d6; }}
            .metric-label {{ font-size: 14px; color: #586069; margin-top: 5px; }}
            table {{ border-collapse: collapse; width: 100%; margin: 20px 0; font-size: 14px; }}
            th, td {{ padding: 12px; border: 1px solid #e1e4e8; text-align: left; }}
            th {{ background: #f6f8fa; }}
            .insight-box {{ background: #fffbdd; border-left: 5px solid #ffcc00; padding: 15px; margin: 20px 0; font-style: italic; }}
            .scenario-card {{ border: 1px solid #e1e4e8; border-radius: 6px; margin-bottom: 20px; overflow: hidden; }}
            .scenario-header {{ background: #f6f8fa; padding: 10px 20px; font-weight: bold; border-bottom: 1px solid #e1e4e8; display: flex; justify-content: space-between; }}
            .scenario-body {{ padding: 20px; }}
            .tag {{ display: inline-block; padding: 2px 8px; border-radius: 12px; font-size: 12px; font-weight: 600; margin-right: 5px; }}
            .tag-high {{ background: #d73a49; color: white; }}
            .tag-mid {{ background: #ffc107; color: black; }}
            .tag-low {{ background: #28a745; color: white; }}
        </style>
    </head>
    <body>
    <div class="container">
        <h1>渠道经营诊断书: {channel_name}</h1>
        <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        
        {ReportNarrator.diagnose_channel(m, data['scenarios'][0]['promo_structure'])} <!-- Using first scenario promo as proxy for now -->
        
        <h2>1. 全景仪表盘 (Strategic Overview)</h2>
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-val">{format_currency(m['gmv'])}</div>
                <div class="metric-label">GMV 规模</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{format_currency(m['aov'])}</div>
                <div class="metric-label">客单价 (AOV)</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{m['upt']:.1f}</div>
                <div class="metric-label">客件数 (UPT)</div>
            </div>
            <div class="metric-card">
                <div class="metric-val">{format_pct(m['discount_rate'])}</div>
                <div class="metric-label">折扣率</div>
            </div>
        </div>
        
        <h3>价格带分布</h3>
        <table>
            <tr>{"".join([f"<th>{k}</th>" for k in p_dist.keys()])}</tr>
            <tr>{"".join([f"<td>{format_pct(v)}</td>" for v in p_dist.values()])}</tr>
        </table>
        
        <h2>2. 核心客群聚类 (Segmentation)</h2>
        <table>
            <thead><tr><th>人群标签</th><th>占比</th><th>客单特征</th><th>客件特征</th><th>折扣偏好</th></tr></thead>
            <tbody>
    """
    
    for seg in data['clusters']['segments']:
        ft = seg['features']
        html += f"""
            <tr>
                <td><strong>{seg['label']}</strong></td>
                <td>{format_pct(seg['share'])}</td>
                <td>{format_currency(ft['Avg_AOV'])}</td>
                <td>{ft['Avg_Items']:.1f}件</td>
                <td>{format_pct(ft['Avg_Discount'])}</td>
            </tr>
        """
        
    html += """
            </tbody>
        </table>
        
        <h2>3. 黄金场景切片 (Golden Scenarios)</h2>
        <p>以下展示 GMV 贡献最高的 Top 5 时空场景：</p>
    """
    
    # Sort scenarios by GMV
    sorted_scenarios = sorted(data['scenarios'], key=lambda x: x['metrics']['gmv'], reverse=True)[:5]
    
    for s in sorted_scenarios:
        sm = s['metrics']
        drivers = s['drivers']['top_skus'][:3]
        basket = s['basket']['associations'][:2]
        
        driver_html = "".join([f"<li>{d['name']} ({format_currency(d['gmv'])})</li>" for d in drivers])
        basket_html = "".join([f"<li>{' + '.join(b['items'])} ({b['count']}次)</li>" for b in basket]) if basket else "<li>无显著连带</li>"
        
        html += f"""
        <div class="scenario-card">
            <div class="scenario-header">
                <span>{s['id']}</span>
                <span>GMV Contribution: {format_currency(sm['gmv'])}</span>
            </div>
            <div class="scenario-body">
                <div style="display: flex; gap: 20px;">
                    <div style="flex: 1;">
                        <h4>场景画像</h4>
                        <ul>
                            <li><strong>客单</strong>: {format_currency(sm['aov'])}</li>
                            <li><strong>折扣</strong>: {format_pct(sm['discount_rate'])}</li>
                            <li><strong>深度折扣占比</strong>: {format_pct(s['promo_structure']['depth_dist'].get('High', 0))}</li>
                        </ul>
                    </div>
                    <div style="flex: 1;">
                        <h4>核心驱动 (Top SKUs)</h4>
                        <ul>{driver_html}</ul>
                    </div>
                    <div style="flex: 1;">
                        <h4>连带特征</h4>
                        <ul>{basket_html}</ul>
                    </div>
                </div>
            </div>
        </div>
        """

    html += """
    </div>
    </body>
    </html>
    """
    return html

def main():
    base_dir = os.getcwd()
    json_path = os.path.join(base_dir, "order_analysis/reports/data/analysis_cube_v2.json")
    output_dir = os.path.join(base_dir, "order_analysis/reports/channels_v2")
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    with open(json_path, 'r') as f:
        full_data = json.load(f)
        
    for ch_name, ch_data in full_data['channels'].items():
        if not ch_data.get('dashboard'): continue
        
        print(f"Generating V2 report for {ch_name}...")
        html_content = generate_html_report(ch_name, ch_data)
        
        filename = f"report_v2_{ch_name}.html"
        with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
            f.write(html_content)

if __name__ == "__main__":
    main()
