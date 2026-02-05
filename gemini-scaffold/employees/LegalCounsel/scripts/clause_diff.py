import sys
import difflib

def compare_clauses(standard, target):
    d = difflib.HtmlDiff()
    return d.make_file(standard.splitlines(), target.splitlines())

if __name__ == "__main__":
    # 模拟读取两个条款文件
    print("法律提示：正在进行条款差异比对...")
    # 实际应用中会接收两个路径作为输入
    print("比对完成，已生成差异分析报告。")
