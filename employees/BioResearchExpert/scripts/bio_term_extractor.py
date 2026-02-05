import sys
import re

def extract_terms(text):
    # 模拟从文献中提取基因、蛋白质或化合物
    patterns = {
        "Genes/Proteins": r"\b[A-Z0-9]{3,}\b",
        "Compounds": r"\b[A-Za-z]+[0-9]+[A-Za-z]*\b"
    }
    results = {}
    for category, p in patterns.items():
        results[category] = list(set(re.findall(p, text)))
    return results

if __name__ == "__main__":
    text = sys.stdin.read()
    print(extract_terms(text))
