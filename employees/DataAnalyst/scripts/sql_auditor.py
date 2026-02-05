import sys
import re

def audit_sql(sql_query):
    findings = []
    # 1. 检查危险操作
    if re.search(r"\b(DROP|TRUNCATE|DELETE)\b", sql_query, re.I):
        findings.append("[CRITICAL] 发现潜在的破坏性操作 (DROP/TRUNCATE/DELETE)")
    
    # 2. 检查 SELECT *
    if re.search(r"SELECT\s+\*", sql_query, re.I):
        findings.append("[WARNING] 建议避免使用 SELECT *，请明确列名以提高性能")
    
    # 3. 检查是否有限流
    if not re.search(r"LIMIT\s+\d+", sql_query, re.I):
        findings.append("[ADVICE] 未发现 LIMIT 限制，大数据量下可能导致超时")
        
    return findings

if __name__ == "__main__":
    query = sys.stdin.read()
    results = audit_sql(query)
    if results:
        print("
".join(results))
    else:
        print("SQL 静态审计通过。")
