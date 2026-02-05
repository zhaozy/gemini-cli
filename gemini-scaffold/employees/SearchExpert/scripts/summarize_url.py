#!/usr/bin/env python3
import sys
import json
# 注意：这里假设环境中安装了 requests 和 beautifulsoup4，
# 但为了演示纯净环境，我们用标准库或模拟输出，
# 或者在这个脚本里其实是打印一段 Prompt 提示 Gemini 核心去执行 web_fetch。

# 在 Gemini CLI 语境下，更好的 Skills 是 "Prompt Templates" 或者 "Composite Commands"
# 这里我们演示一个简单的 Shell 封装，打印出标准化的 Prompt 供用户或 Agent 参考。

def main():
    if len(sys.argv) < 2:
        print("Usage: summarize_url <url>")
        sys.exit(1)

    url = sys.argv[1]
    
    # 构造一个结构化的指令，让 Gemini 核心更容易处理
    print(f"ACTION_REQUIRED: Please use 'web_fetch' to retrieve content from {url}")
    print(f"THEN: Summarize the content in 3 bullet points in Chinese.")

if __name__ == "__main__":
    main()
