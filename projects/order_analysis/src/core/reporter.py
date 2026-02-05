import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any
import markdown

class MarkdownReporter:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        self.report_path = os.path.join(output_dir, f"analysis_report_{datetime.now().strftime('%Y%m%d')}.md")
        self.content = []
        
        # 初始化标题
        self.add_header(f"交易分析报告 ({datetime.now().strftime('%Y-%m-%d')})", level=1)

    def add_header(self, text: str, level: int = 2):
        self.content.append(f"{'#' * level} {text}\n")

    def add_text(self, text: str):
        self.content.append(f"{text}\n")

    def add_metrics_summary(self, metrics: Dict[str, Any]):
        self.add_header("1. 核心指标概览", level=2)
        table = (
            "| 指标 | 数值 |\n"
            "| :--- | :--- |\n"
            f"| **GMV (实收)** | ¥{metrics['gmv']:,.2f} |\n"
            f"| **订单量** | {metrics['order_count']:,} |\n"
            f"| **客单价 (AOV)** | ¥{metrics['aov']:.2f} |\n"
            f"| **销售件数** | {metrics['total_items']:,} |\n"
        )
        self.content.append(table)

    def add_trend_section(self, trend_df: pd.DataFrame):
        self.add_header("2. 日度销售趋势 (前 5 日)", level=2)
        # 格式化表格
        fmt_df = trend_df.head().reset_index()
        fmt_df['period'] = fmt_df['period'].dt.strftime('%Y-%m-%d')
        fmt_df['gmv'] = fmt_df['gmv'].apply(lambda x: f"{x:,.2f}")
        fmt_df['aov'] = fmt_df['aov'].apply(lambda x: f"{x:.2f}")
        
        self.content.append(fmt_df.to_markdown(index=False))
        self.content.append("\n")

    def add_category_section(self, cat_df: pd.DataFrame):
        self.add_header("3. Top 10 品类分析 (按 GMV)", level=2)
        # 格式化
        fmt_df = cat_df.reset_index()
        fmt_df['gmv'] = fmt_df['gmv'].apply(lambda x: f"{x:,.2f}")
        fmt_df['gmv_share'] = fmt_df['gmv_share'].apply(lambda x: f"{x:.2%}")
        
        self.content.append(fmt_df.to_markdown(index=False))
        self.content.append("\n")

    def add_channel_overview(self, df: pd.DataFrame):
        self.add_header("4. 渠道深度洞察", level=2)
        self.add_header("4.1 渠道概览", level=3)
        
        fmt_df = df.reset_index()
        fmt_df['gmv'] = fmt_df['gmv'].apply(lambda x: f"¥{x:,.0f}")
        fmt_df['gmv_share'] = fmt_df['gmv_share'].apply(lambda x: f"{x:.1%}")
        fmt_df['aov'] = fmt_df['aov'].apply(lambda x: f"¥{x:.1f}")
        fmt_df['avg_price'] = fmt_df['avg_price'].apply(lambda x: f"¥{x:.1f}")
        
        self.content.append(fmt_df.to_markdown(index=False))
        self.content.append("\n")

    def add_channel_time_pref(self, df: pd.DataFrame):
        self.add_header("4.2 交易时间段偏好 (订单占比)", level=3)
        # 格式化百分比
        fmt_df = df.map(lambda x: f"{x:.1%}")
        self.content.append(fmt_df.to_markdown())
        self.content.append("\n")

    def add_channel_discount(self, df: pd.DataFrame):
        self.add_header("4.3 折扣敏感度 (平均折扣率)", level=3)
        fmt_df = df.map(lambda x: f"{x:.1%}")
        self.content.append(fmt_df.to_markdown())
        self.content.append("\n")

    def add_channel_upt(self, df: pd.DataFrame):
        self.add_header("4.4 客件数 (UPT)", level=3)
        fmt_df = df.map(lambda x: f"{x:.1f}")
        self.content.append(fmt_df.to_markdown())
        self.content.append("\n")

    def add_calendar_analysis(self, df: pd.DataFrame):
        self.add_header("4.5 日历效应 (日均 GMV)", level=3)
        # 格式化
        fmt_df = df.copy()
        for col in fmt_df.columns:
            if 'uplift' in col:
                fmt_df[col] = fmt_df[col].map(lambda x: f"{x:+.1%}" if pd.notnull(x) else "-")
            else:
                fmt_df[col] = fmt_df[col].map(lambda x: f"¥{x:,.0f}" if pd.notnull(x) else "-")
        
        self.content.append(fmt_df.to_markdown())
        self.content.append("\n")

    def add_distribution_analysis(self, aov_dist: pd.DataFrame, cluster_profile: pd.DataFrame, channel_cluster: pd.DataFrame):
        self.add_header("5. 订单结构分布 (无监督聚类)", level=2)
        
        self.add_header("5.1 客单价区间分布 (AOV Bins)", level=3)
        fmt_aov = aov_dist.map(lambda x: f"{x:.1%}")
        self.content.append(fmt_aov.to_markdown())
        self.content.append("\n")
        
        self.add_header("5.2 消费模式聚类特征 (K-Means K=4)", level=3)
        fmt_prof = cluster_profile.reset_index()
        fmt_prof['实收金额'] = fmt_prof['实收金额'].apply(lambda x: f"¥{x:.1f}")
        fmt_prof['销售数量'] = fmt_prof['销售数量'].apply(lambda x: f"{x:.1f}件")
        fmt_prof['share'] = fmt_prof['share'].apply(lambda x: f"{x:.1%}")
        self.content.append(fmt_prof[['label', '实收金额', '销售数量', 'count', 'share']].to_markdown(index=False))
        self.content.append("\n")

        self.add_header("5.3 渠道消费模式构成", level=3)
        fmt_cc = channel_cluster.map(lambda x: f"{x:.1%}")
        self.content.append(fmt_cc.to_markdown())
        self.content.append("\n")

    def add_channel_deep_dive(self, channel_name: str, insights: Dict[str, Any], top_products: pd.DataFrame, promo_stats: pd.Series):
        """
        生成单个渠道的深度画像章节
        """
        self.add_header(f"渠道洞察: {channel_name}", level=3)
        
        # 1. 核心画像 (Text Summary)
        summary = (
            f"- **定位**: {insights.get('position', 'N/A')}\n"
            f"- **消费场景**: {insights.get('context', 'N/A')}\n"
            f"- **客单特征**: AOV ¥{insights.get('aov', 0):.1f} / UPT {insights.get('upt', 0):.1f}件\n"
            f"- **促销依赖**: 折扣率 {promo_stats['discount_rate']:.1%} (订单渗透率 {promo_stats['promo_order_ratio']:.1%})\n"
        )
        self.content.append(summary)
        
        # 2. Top 商品
        self.content.append(f"**核心驱动品类 (Top 5)**:")
        fmt_prod = top_products[['小类编码', '商品名称', '实收金额', '销售数量']].copy()
        fmt_prod['实收金额'] = fmt_prod['实收金额'].apply(lambda x: f"¥{x:,.0f}")
        self.content.append(fmt_prod.to_markdown(index=False))
        self.content.append("\n")

    def add_cube_slice_analysis(self, slice_name: str, data: Dict[str, Any]):
        """
        展示一个特定切片（如 美团-周末-晚市）的深度分析
        """
        if not data: return
        
        self.add_header(f"-> 下钻场景: {slice_name}", level=4)
        
        # 1. 核心指标行
        m = data['metrics']
        self.content.append(f"**指标**: AOV ¥{m['aov']:.1f} | UPT {m.get('total_items',0)/m.get('order_count',1):.1f}件 | GMV ¥{m['gmv']:,.0f}")
        
        # 2. 促销特征
        pd = data['promo_dist']
        pp = data['promo_perf']
        promo_txt = []
        for ptype, share in pd.items():
            perf = pp.get(ptype, {})
            promo_txt.append(f"{ptype}({share:.0%}): AOV ¥{perf.get('实收金额',0):.0f}")
        self.content.append(f"**促销结构**: {', '.join(promo_txt)}")
        
        # 3. 消费聚类
        clusters = [f"{c['label']}({c['share']:.0%})" for c in data['clusters']]
        self.content.append(f"**主力客群**: {', '.join(clusters)}")
        
        # 4. 货品特征
        top_str = ", ".join([f"{k}" for k in list(data['top_items'].keys())[:3]])
        self.content.append(f"**Top爆品**: {top_str}")
        
        if data['associations']:
            self.content.append(f"**高频连带**: {data['associations'][0]}")
            
        self.content.append("\n")

    def save(self):
        # 1. Save Markdown
        md_content = "\n".join(self.content)
        with open(self.report_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        print(f"Report saved to: {self.report_path}")
        
        # 2. Save HTML
        html_path = self.report_path.replace(".md", ".html")
        self._save_html(md_content, html_path)
        
    def _save_html(self, md_text: str, output_path: str):
        # Convert MD to HTML
        html_body = markdown.markdown(md_text, extensions=['tables', 'fenced_code'])
        
        # Simple CSS (GitHub-like)
        css = """
        <style>
            body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #24292e; }
            h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
            table { border-collapse: collapse; width: 100%; margin: 15px 0; }
            th, td { border: 1px solid #dfe2e5; padding: 6px 13px; }
            th { background-color: #f6f8fa; font-weight: 600; }
            tr:nth-child(2n) { background-color: #f6f8fa; }
            code { background-color: rgba(27,31,35,.05); padding: .2em .4em; border-radius: 3px; }
        </style>
        """
        
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>Analysis Report</title>
            {css}
        </head>
        <body>
            {html_body}
        </body>
        </html>
        """
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(full_html)
        print(f"HTML Report saved to: {output_path}")
