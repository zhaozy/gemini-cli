import markdown
import os
import glob

def convert_all():
    base_dir = os.getcwd()
    reports_dir = os.path.join(base_dir, "order_analysis", "reports", "channels")
    
    # CSS
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
    
    for md_file in glob.glob(os.path.join(reports_dir, "*.md")):
        with open(md_file, 'r', encoding='utf-8') as f:
            text = f.read()
            
        html_body = markdown.markdown(text, extensions=['tables'])
        
        full_html = f"<!DOCTYPE html><html><head><meta charset='utf-8'><title>Report</title>{css}</head><body>{html_body}</body></html>"
        
        html_file = md_file.replace(".md", ".html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(full_html)
            
        print(f"Converted {os.path.basename(md_file)} -> HTML")

if __name__ == "__main__":
    convert_all()
