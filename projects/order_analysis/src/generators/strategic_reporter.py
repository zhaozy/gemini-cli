import json
import os
import pandas as pd
from datetime import datetime

def fmt_c(x): return f"¥{x:,.1f}" if pd.notnull(x) else "-"
def fmt_p(x): return f"{x:.1%}" if pd.notnull(x) else "-"
def fmt_f(x): return f"{x:.2f}" if pd.notnull(x) else "-"

class StrategicReporter:
    def __init__(self, channel_name, data, global_benchmarks=None):
        self.ch = channel_name
        self.data = data
        self.benchmarks = global_benchmarks or {}
        self.lines = []
        
    def add_header(self, text, level=1):
        self.lines.append(f"{ '#' * level} {text}\n")
        
    def add_quote(self, text):
        self.lines.append(f"> {text}\n")
        
    def add_table(self, headers, rows):
        self.lines.append("| " + " | ".join(headers) + " |")
        self.lines.append("| " + " | ".join(['---'] * len(headers)) + " |")
        for row in rows:
            self.lines.append("| " + " | ".join([str(r) for r in row]) + " |")
        self.lines.append("")

    def render_overview(self):
        bo = self.data['business_overview']
        self.add_header("1. 整体业务效果呈现", 2)
        
        aov_bench = self.benchmarks.get('aov_avg', 0)
        upt_bench = self.benchmarks.get('upt_avg', 0)
        aov_ctx, upt_ctx = "", ""
        
        if self.ch != "全渠道总览" and aov_bench > 0:
            a_diff = (bo['aov'] - aov_bench) / aov_bench
            u_diff = (bo['upt'] - upt_bench) / upt_bench
            aov_ctx = f" ({'+' if a_diff>0 else ''}{fmt_p(a_diff)})"
            upt_ctx = f" ({'+' if u_diff>0 else ''}{fmt_p(u_diff)})"
            
        row_data = [
            fmt_c(bo['gmv_total']), bo['order_total'], fmt_f(bo['daily_avg_orders']), 
            bo['active_skus'], fmt_p(bo['discount_rate']), fmt_p(bo['promo_penetration']), 
            fmt_p(bo.get('sku_promo_penetration', 0)),
            fmt_c(bo['aov']) + aov_ctx, fmt_f(bo['upt']) + upt_ctx
        ]
        self.add_table(["GMV", "订单总数", "日均单量", "动销SKU", "折扣率", "订单促销渗透", "商品促销渗透", "客单价", "客件数"], [row_data])

    def render_product_efficiency(self):
        pe = self.data['product_efficiency']
        self.add_header("2. 商品效率呈现 (渗透-带动矩阵)", 2)
        pa = pe['penetration_affinity']
        if 'quadrants' in pa:
            bench = pa.get('benchmarks', {})
            self.add_quote(
                "**指标详解 (Glossary)**:<br>"
                "- **渗透率**: `含该商品订单数 / 总订单数`。代表流量获取能力。<br>"
                "- **带动系数**: `该商品所在订单平均件数 - 1`。代表连带能力。<br>"
                "- **角色定义**: **Hooks (钩子)**: 高渗透+高带动；**Islands (孤岛)**: 高渗透+低带动；**Assassins (刺客)**: 低价+低带动。"
            )
            self.add_quote(f"**动态阈值说明**: 渗透Top20%={fmt_p(bench.get('p_threshold',0))}, 带动均值={fmt_f(bench.get('a_threshold',0))}")
            
            rows = []
            for k in ['Hooks', 'Bundlers', 'Islands', 'Assassins']:
                for item in pa['quadrants'].get(k, [])[:5]:
                    rows.append([item['sku'], fmt_p(item['penetration']), fmt_f(item['affinity']), fmt_c(item['avg_price']), k])
            self.add_table(["商品名称", "渗透率", "带动系数", "件单价", "战略角色"], rows)
            
            assassin_count = len(pa['quadrants'].get('Assassins', []))
            if assassin_count > 0:
                self.add_quote(f"💡 **经营诊断**: 发现 {assassin_count} 个‘履约刺客’商品。建议通过捆绑销售或提升起购量来对冲配送成本。")

    def render_pricing_efficiency(self):
        pe = self.data['pricing_efficiency']
        self.add_header("3. 价格与促销效率呈现", 2)
        
        sk = pe['skewness']
        self.add_header("3.1 订单价格带偏态分析", 3)
        self.add_quote("**指标详解**: 偏态系数衡量客单价分布的不对称性。正偏越大，说明低客单订单占比越高。")
        row_sk = [fmt_c(sk['mean']), fmt_c(sk['median']), fmt_c(sk.get('mode', 0)), fmt_f(sk['skewness_index']), sk['diagnosis']]
        self.add_table(["均值", "中位数", "众数", "偏态系数", "诊断"], [row_sk])
        
        el = pe['elasticity']
        self.add_header("3.2 价格稳定性审计与折扣弹性", 3)
        audit = el.get('audit', {})
        if audit:
            self.add_quote(f"**价格稳定性审计**: 始终原价销售商品 {audit['always_full_price_count']}个, 始终促销商品 {audit['always_promo_count']}个。")
        
        has_data = False
        if el.get('inelastic_skus'):
            self.add_header("❌ 折扣黑榜：无弹性/低敏感 (Top 10)", 4)
            self.add_quote("诊断：此类商品打折无销量增量，纯粹损失毛利。")
            self.add_table(["商品名称"], [[s] for s in el['inelastic_skus'][:10]])
            has_data = True
        if el.get('elastic_skus'):
            self.add_header("✅ 折扣红榜：高弹性/高敏感 (Top 10)", 4)
            self.add_quote("诊断：此类商品对促销极度敏感，建议作为引流主打。")
            self.add_table(["商品名称"], [[s] for s in el['elastic_skus'][:10]])
            has_data = True
        if not has_data:
            self.add_quote("⚠️ **客观结论**: 观测期内绝大多数商品价格未变动，无法进行有效的折扣弹性测算。")

    def render_spatio_temporal(self):
        st = self.data['spatio_temporal']
        self.add_header("4. 时空生活嵌入呈现", 2)
        ov = st.get('overview', {})
        if ov:
            self.add_header("4.1 时空基础分布 (Overview)", 3)
            day_rows = [[d['day_type'], d['流水单号'], fmt_c(d['实收金额']), fmt_p(d['order_share'])] for d in ov['day_distribution']]
            self.add_table(["日类型", "订单量", "GMV", "占比"], day_rows)
            per_rows = [[p['period'], p['流水单号'], fmt_c(p['实收金额']), fmt_p(p['order_share'])] for p in ov['period_distribution']]
            self.add_table(["时段", "订单量", "GMV", "占比"], per_rows)
        
        fl = st['fluctuation']
        self.add_header("4.2 异动系数", 3)
        self.add_quote("**指标详解**: 异动系数 > 1.2 通常代表社区/生活型商圈特征。")
        row_fl = ["周末", fmt_f(fl['weekend_coef']), "生活型" if fl['weekend_coef']>1.2 else "办公型"]
        self.add_table(["类型", "异动系数", "商圈推断"], [row_fl])
        
        self.add_header("4.3 TGI 时段心智商品", 3)
        self.add_quote("**指标详解**: TGI > 100 代表该时段对该品类有显著偏好。")
        tgi_rows = []
        for p, items in st['tgi_heatmap'].items():
            item_str = ", ".join([f"{i['sku']}({i['tgi']:.0f})" for i in items])
            tgi_rows.append([p, item_str])
        self.add_table(["时段", "高 TGI 商品 (Top 3)"], tgi_rows)

    def render_basket(self):
        bf = self.data['basket_features']
        self.add_header("5. 购物篮特征呈现", 2)
        
        orphan = bf['orphan_orders']
        self.add_header("5.1 孤儿单诊断", 3)
        self.add_quote("**指标详解**: 孤儿单即仅含1件商品的订单，代表极高的履约成本占比。")
        self.lines.append(f"**孤儿单占比**: {fmt_p(orphan['ratio'])}\n")
        if orphan['culprits']:
            self.add_header("孤儿单元凶 Top 10", 4)
            self.add_table(["商品名称", "占比"], [[k, fmt_p(v)] for k,v in list(orphan['culprits'].items())[:10]])
        
        self.add_header("5.2 购物篮复杂度聚类", 3)
        self.add_quote("**指标详解**: 基于件数、类目数、金额进行聚类，还原用户购买指纹。")
        rows = []
        for seg in bf['complexity_clusters']:
            ft = seg['features']
            rows.append([seg['label'], fmt_p(seg['share']), fmt_f(ft['items']), fmt_f(ft['categories']), fmt_c(ft['aov'])])
        self.add_table(["指纹类型", "占比", "平均件数", "跨类目数", "平均客单"], rows)

    def generate(self):
        self.lines.append(f"# 全链路经营诊断报告: {self.ch}\n")
        self.lines.append(f"> 分析模式: 统计自适应 | 诊断级别: 数据科学家 | 日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        self.render_overview()
        self.render_product_efficiency()
        self.render_pricing_efficiency()
        self.render_spatio_temporal()
        self.render_basket()
        return "\n".join(self.lines)

class GlobalStrategicReporter(StrategicReporter):
    def __init__(self, channel_name, global_data, all_channels_data, benchmarks):
        super().__init__(channel_name, global_data, benchmarks)
        self.all_channels = all_channels_data

    def generate(self):
        self.lines.append("# 全渠道经营大盘总览 (Global Overview)\n")
        self.lines.append(f"> 诊断级别: 经营专家 | 日期: {datetime.now().strftime('%Y-%m-%d')}\n")
        self.render_overview()
        self.render_channel_efficiency_matrix()
        self.render_channel_product_matrix()
        self.render_global_product_efficiency()
        return "\n".join(self.lines)

    def render_channel_efficiency_matrix(self):
        ce = self.data['channel_efficiency']
        rank = ce['rankings']
        self.add_header("2. 渠道效率呈现 (Channel Matrix)", 2)
        channels = sorted(rank['gmv_share'].keys(), key=lambda x: rank['gmv_share'][x], reverse=True)
        rows = []
        for ch in channels:
            row = [
                ch, fmt_p(rank['gmv_share'][ch]), fmt_c(rank['aov'][ch]), 
                fmt_f(rank['upt'][ch]), fmt_p(rank['discount_rate'][ch]), 
                fmt_p(rank['promo_penetration'][ch]), ce['ecological_niche'].get(ch, '-')
            ]
            rows.append(row)
        self.add_table(["渠道", "GMV贡献", "客单价", "客件数", "折扣率", "促销渗透", "生态位判定"], rows)
        
        pb = ce['price_bands']
        bands = list(next(iter(pb.values())).keys()) if pb else []
        self.add_header("2.2 渠道价格带分布对比", 3)
        rows_pb = []
        for ch in channels:
            if ch in pb: rows_pb.append([ch] + [fmt_p(pb[ch].get(b, 0)) for b in bands])
        self.add_table(["渠道"] + bands, rows_pb)

    def render_channel_product_matrix(self):
        self.add_header("2.3 渠道商品驱动力对比透视", 3)
        rows = []
        for ch_name, ch_data in self.all_channels.items():
            r = ch_data.get('product_rankings', {})
            if not r: continue
            fmt_sku = lambda d: "<br>".join([f"{k} ({fmt_c(v)})" for k,v in list(d.items())[:3]])
            rows.append([ch_name, fmt_sku(r.get('top_10_gmv', {})), fmt_sku(r.get('top_10_qty', {})), fmt_sku(r.get('bottom_10_gmv', {}))])
        self.add_table(["渠道", "GMV Top 3", "销量 Top 3", "长尾 Bottom 3"], rows)

    def render_global_product_efficiency(self):
        ce = self.data['channel_efficiency']
        self.add_header("3. 全网商品效率 (Global Top/Bottom)", 2)
        top10 = ce.get('global_top_10_gmv', {})
        self.add_table(["商品名称", "销售金额 (GMV)"], [[k, fmt_c(v)] for k, v in top10.items()])

def get_report_html(title, md_content):
    import markdown
    html = markdown.markdown(md_content, extensions=['tables'])
    css = "<style>body{font-family:sans-serif;max-width:1000px;margin:40px auto;padding:20px;line-height:1.6;color:#24292e;background:#f6f8fa}.container{background:white;padding:40px;border-radius:8px;box-shadow:0 1px 3px rgba(0,0,0,0.12)}h1,h2,h3{border-bottom:1px solid #eaecef;padding-bottom:0.3em}table{border-collapse:collapse;width:100%;margin:20px 0}th,td{border:1px solid #dfe2e5;padding:10px;text-align:left}th{background:#f6f8fa}blockquote{border-left:4px solid #0366d6;background:#f1f8ff;padding:15px;margin:20px 0}</style>"
    return f"<html><head><meta charset='utf-8'><title>{title}</title>{css}</head><body><div class='container'>{html}</div></body></html>"

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    json_path = os.path.join(base_dir, "reports", "data", "analysis_v4_full.json")
    output_dir = os.path.join(base_dir, "reports", "diagnostics_v5")
    if not os.path.exists(output_dir): os.makedirs(output_dir)
    with open(json_path, 'r') as f: full_data = json.load(f)
    gb = full_data['global']['business_overview']
    benchmarks = {"aov_avg": gb['aov'], "upt_avg": gb['upt']}
    
    print("Generating Global Report...")
    global_rep = GlobalStrategicReporter("全渠道总览", full_data['global'], full_data['channels'], benchmarks)
    md = global_rep.generate()
    with open(os.path.join(output_dir, "report_global_v4.md"), 'w') as f: f.write(md)
    with open(os.path.join(output_dir, "report_global_v4.html"), 'w') as f: f.write(get_report_html("Global Overview", md))
    
    for ch, data in full_data['channels'].items():
        print(f"Generating Detailed Report for {ch}...")
        rep = StrategicReporter(ch, data, benchmarks)
        md_text = reporter_md = rep.generate()
        with open(os.path.join(output_dir, f"report_{ch}_v4.md"), 'w') as f: f.write(md_text)
        with open(os.path.join(output_dir, f"report_{ch}_v4.html"), 'w') as f: f.write(get_report_html(ch, md_text))

if __name__ == "__main__":
    main()