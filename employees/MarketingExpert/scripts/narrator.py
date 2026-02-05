import json
import os
import pandas as pd

class InsightNarrator:
    def __init__(self, report_dir: str, store_name: str):
        self.report_dir = report_dir
        self.store_name = store_name
        self.metrics_data = None
        self.new_old_attr = None
        self.profile_attr = None
        self._load_data()

    def _load_data(self):
        """Loads the three JSON report files."""
        try:
            # --- Load Core Metrics ---
            # This is tricky because the JSON is just an array. We rely on the known execution order.
            # (上海湾, Conversion), (上海湾, Duration), (上海湾, Dwell), (上海湾, POS_Buyers), (上海湾, Traffic)
            # (新江湾, Conversion), ...
            store_map = {
                '上海湾': {'start': 0, 'metrics': ['Conversion', 'Duration', 'Dwell', 'POS_Buyers', 'Traffic']},
                '新江湾': {'start': 5, 'metrics': ['Conversion', 'Duration', 'Dwell', 'POS_Buyers', 'Traffic']}
            }
            if self.store_name in store_map:
                with open(os.path.join(self.report_dir, 'advanced_analysis_results.json'), 'r', encoding='utf-8') as f:
                    all_metrics = json.load(f)
                
                self.metrics_data = {}
                store_info = store_map[self.store_name]
                for i, metric_name in enumerate(store_info['metrics']):
                    record = all_metrics[store_info['start'] + i]
                    # Add metric name to the record for easier lookup
                    record['指标名称'] = metric_name
                    self.metrics_data[metric_name] = record
            
            # --- Load Attribution Data ---
            # These files should contain '门店名称' and can be filtered.
            attr_new_old_path = os.path.join(self.report_dir, 'attribution_new_old_customer.json')
            if os.path.exists(attr_new_old_path):
                with open(attr_new_old_path, 'r', encoding='utf-8') as f:
                    self.new_old_attr = pd.DataFrame(json.load(f))

            attr_profile_path = os.path.join(self.report_dir, 'attribution_customer_profile.json')
            if os.path.exists(attr_profile_path):
                with open(attr_profile_path, 'r', encoding='utf-8') as f:
                    self.profile_attr = pd.DataFrame(json.load(f))

        except FileNotFoundError as e:
            print(f"Error: Could not find a report file. {e}")
            raise
        except Exception as e:
            print(f"Error loading or parsing report files: {e}")
            raise
            
    def _format_metrics_table(self):
        """Formats the main metrics table from the new analysis results."""
        if not self.metrics_data:
            return "核心指标数据缺失。"

        header = "| 指标 (Metric) | 绝对值变化 (门店) | 趋势变化 (门店) | 超额绝对值变化 (Alpha) | 归一化趋势判定 |"
        sep =    "| :--- | :---: | :---: | :---: | :---: |"
        rows = []
        
        # Iterate in a fixed order for consistency
        for m_name in ['Traffic', 'POS_Buyers', 'Conversion', 'Duration', 'Dwell']:
            if m_name not in self.metrics_data:
                continue
            
            data = self.metrics_data[m_name]
            
            def fmt(val, prec=2):
                return f"{val:.{prec}f}" if isinstance(val, (int, float)) else str(val)

            row = (f"| **{m_name}** | "
                   f"{fmt(data.get('门店_绝对值变化'))} | "
                   f"{fmt(data.get('门店_趋势变化'))} | "
                   f"{fmt(data.get('超额_绝对值变化'))} | "
                   f"{data.get('归一化趋势判定', 'N/A')} |")
            rows.append(row)
            
        return "\n".join([header, sep] + rows)

    def _format_attribution_table(self, df: pd.DataFrame, comp_type: str, title: str):
        """Formats an attribution table (either new/old or profile)."""
        rows = [f"**{title}**:", ""]
        if df is None or df.empty or '门店名称' not in df.columns:
             rows.append(f"无法为 {self.store_name} 生成 {title} 归因看板 (数据缺失或格式错误)。")
             return "\n".join(rows)

        # The attribution files might not have the '对比类型' column, so we work with what we have.
        store_df = df[df['门店名称'] == self.store_name].copy()
        if '对比类型' in store_df.columns:
            store_df = store_df[store_df['对比类型'] == comp_type]

        if store_df.empty:
            rows.append(f"{self.store_name} 的 {title} 归因数据 ({comp_type}) 未找到。")
            return "\n".join(rows)
            
        store_df = store_df.sort_values('绝对值变化', ascending=False)
        
        gainers = store_df[store_df['绝对值变化'] > 0].head(3)
        losers = store_df[store_df['绝对值变化'] < 0].tail(3)

        table = ["| 人群 (Segment) | 变动方向 | 绝对增减人数 (Net Change) |",
                 "| :--- | :--- | :--- |"]
        for _, g in gainers.iterrows():
            table.append(f"| **{g['人群标签']}** | 🟢 新增 | +{g['绝对值变化']:.0f} |")
        for _, l in losers.iterrows():
            table.append(f"| **{l['人群标签']}** | 🔴 流失 | {l['绝对值变化']:.0f} |")
        
        if len(gainers) == 0 and len(losers) == 0:
            rows.append("未发现显著的人群数量变化。")
        else:
            rows.extend(table)

        return "\n".join(rows)

    def generate_prompt(self, output_prompt_file):
        """Generates the full narrative prompt from the loaded V2 data."""
        if not self.metrics_data:
            print("错误: 核心指标数据未能加载，无法生成prompt。")
            return
            
        # Extract basic info from the first available metric
        any_metric = next(iter(self.metrics_data.values()))
        reno_month = any_metric.get('reno_month', 'N/A')
        
        prompt = ["# Role: 资深零售数据战略专家", "\n## 任务: 撰写一份【教科书级】的单店深度审计报告。"]
        prompt.append(f"\n# 【{self.store_name}】 全维度深度审计 (Anchor: {reno_month})")
        
        # --- 模块 1: 异常复盘 ---
        prompt.append("\n## 第一部分：历史异常复盘 (Anomaly Review)")
        prompt.append("**1. 分析思路 (Why)**: 识别历史数据中的“噪音”能防止基数偏差误导结论。")
        prompt.append("**2. 数据看板 (Dashboard)**:")
        prompt.append("- *V2分析流程目前不包含独立的异常点检测模块。*")
        prompt.append("\n> **深度解读指令**: 请基于下方核心指标的趋势变化，判断是否存在潜在的基数效应？")

        # --- 模块 2: 趋势与效能诊断 ---
        prompt.append("\n## 第二部分：趋势与效能诊断 (Trend & Efficiency)")
        prompt.append("**1. 分析思路 (Why)**: 我们通过“门店自身 vs. 市场大盘”的双重视角，结合绝对值和趋势斜率两个维度，来评估改造的真实得失。")
        prompt.append("**2. 核心指标说明 (Definitions)**:")
        prompt.append("- **绝对值变化**: 改造后均值 - 改造前均值。反映基础盘的抬升或下降。")
        prompt.append("- **趋势变化**: 改造后斜率 - 改造前斜率。反映增长“加速度”的变化。")
        prompt.append("- **超额绝对值变化 (Alpha)**: 门店绝对值变化 - 大盘绝对值变化。剥离市场影响后的真实效果。")
        prompt.append("- **归一化趋势判定**: 基于门店与大盘的YoY增速差(YoY Gap)的趋势判定。反映相对竞争力的变化趋势。")
        
        prompt.append("**3. 数据看板 (Dashboard)**:")
        table = self._format_metrics_table()
        prompt.append(table)
        
        prompt.append("\n> **深度解读指令**:")
        prompt.append("- **核心矛盾**: `超额绝对值变化`为正，但`归一化趋势判定`为“恶化”，这意味着什么？（提示：可能意味着虽然短期跑赢大盘，但领先的“加速度”正在放缓，相对优势在缩小）。")
        prompt.append("- **量价关系**: 结合客流(Traffic)和买家数(POS_Buyers)的变化，判断是“量价齐升”还是“缩量提价”？")

        # --- 模块 3: 结构归因 ---
        prompt.append("\n## 第三部分：客群结构归因 (Structural Attribution)")
        prompt.append("**1. 分析思路 (Why)**: 总量的变化是由哪些具体人群驱动的？我们坚持使用 **“绝对值 (Headcount)”** 进行归因。")

        # --- New Robust Attribution Logic ---
        # Try for '年内对比' first, if it fails (returns a "not found" message), fall back to '同比佐证'.
        
        # New vs Old Customers
        new_old_table_content = self._format_attribution_table(self.new_old_attr, '年内对比', "数据看板 (Dashboard) - 新老客")
        if "未找到" in new_old_table_content:
            new_old_table_content = self._format_attribution_table(self.new_old_attr, '同比佐证', "数据看板 (Dashboard) - 新老客 (同比佐证)")
        prompt.append(new_old_table_content)

        # Customer Profiles
        profile_table_content = self._format_attribution_table(self.profile_attr, '年内对比', "数据看板 (Dashboard) - 人群画像")
        if "未找到" in profile_table_content:
            profile_table_content = self._format_attribution_table(self.profile_attr, '同比佐证', "数据看板 (Dashboard) - 人群画像 (同比佐证)")
        prompt.append("\n" + profile_table_content)
        
        prompt.append("\n> **深度解读指令**: 结合前面的效能数据，分析这种客群置换是“良性换血”（如高价值客群替换了低价值客群）还是“恶性流失”？")

        with open(output_prompt_file, 'w', encoding='utf-8') as f:
            f.write("\n".join(prompt))
        print(f"V2 Prompt Generated: {output_prompt_file}")


if __name__ == "__main__":
    # Example of how to run this new narrator
    try:
        # Define the target store and report directory
        target_store_name = '上海湾'
        reports_directory = 'data-analysis/reports'
        output_file = os.path.join(reports_directory, f'prompt_for_{target_store_name}.md')

        # Initialize and run
        narrator = InsightNarrator(report_dir=reports_directory, store_name=target_store_name)
        narrator.generate_prompt(output_prompt_file=output_file)
    except Exception as e:
        print(f"An error occurred during prompt generation: {e}")
