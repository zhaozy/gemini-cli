import sys
import collections
import re

def audit_copy(text):
    # 1. 检查禁止词汇 (示例)
    banned = ["绝对", "第一", "最", "万能"]
    found_banned = [w for w in banned if w in text]
    
    # 2. 关键字密度
    words = re.findall(r'\w+', text.lower())
    total = len(words)
    counts = collections.Counter(words)
    top_keywords = {w: f"{round(c/total*100, 2)}%" for w, c in counts.most_common(3)}
    
    return {
        "banned_words_found": found_banned,
        "keyword_density": top_keywords,
        "readability_score": "PASS" if total > 20 else "TOO_SHORT"
    }

if __name__ == "__main__":
    text = sys.stdin.read()
    print(audit_copy(text))
