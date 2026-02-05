import markdown
import os

md_path = "order_analysis/reports/analysis_report_v2.md"
html_path = "order_analysis/reports/analysis_report_v2.html"

with open(md_path, "r", encoding="utf-8") as f:
    md_text = f.read()

html_body = markdown.markdown(md_text, extensions=['tables'])

css = """
<style>
    body { font-family: -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 20px; color: #24292e; }
    h1, h2, h3 { border-bottom: 1px solid #eaecef; padding-bottom: .3em; }
    table { border-collapse: collapse; width: 100%; margin: 15px 0; }
    th, td { border: 1px solid #dfe2e5; padding: 6px 13px; }
    th { background-color: #f6f8fa; font-weight: 600; }
    tr:nth-child(2n) { background-color: #f6f8fa; }
    code { background-color: rgba(27,31,35,.05); padding: .2em .4em; border-radius: 3px; }
    .metric-box { display: inline-block; padding: 10px; margin: 5px; background: #f1f8ff; border-radius: 5px; border: 1px solid #c8e1ff; }
</style>
"""

full_html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>深度洞察报告 v2</title>
    {css}
</head>
<body>
    {html_body}
</body>
</html>
"""

with open(html_path, "w", encoding="utf-8") as f:
    f.write(full_html)

print(f"HTML saved to {html_path}")
