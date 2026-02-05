import sys
import json

def calculate_variance(actual, budget):
    variance = actual - budget
    percent = (variance / budget) * 100 if budget != 0 else 0
    status = "FAVORABLE" if variance <= 0 else "UNFAVORABLE" # 假设是成本分析
    return {
        "abs_variance": round(variance, 2),
        "percent_variance": f"{round(percent, 2)}%",
        "status": status
    }

if __name__ == "__main__":
    # 示例输入: 1200, 1000
    try:
        data = sys.stdin.read().split()
        actual = float(data[0])
        budget = float(data[1])
        print(json.dumps(calculate_variance(actual, budget), indent=2))
    except:
        print("错误：请输入 [实际值] [预算值]")
