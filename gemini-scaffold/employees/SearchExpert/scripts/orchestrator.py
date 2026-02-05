import sys
import json
import subprocess
import os

# 路径配置
SKILL_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(SKILL_ROOT, "scripts")
VENV_PYTHON = os.path.abspath(os.path.join(SKILL_ROOT, "../../.venv/bin/python"))

def run_script(script_name, args):
    cmd = [VENV_PYTHON, os.path.join(SCRIPTS_DIR, script_name)] + args
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Script execution failed: {e.stderr}"}
    except json.JSONDecodeError:
        return {"status": "error", "message": "Invalid JSON output from script"}

def main(url):
    print(f"🔍 [Orchestrator] Starting deep research for: {url}")
    
    # 1. 无论如何，先抓取元数据 (L1)
    metadata = run_script("fetch_metadata.py", [url])
    title = metadata.get("title", "Unknown Title")
    print(f"📄 [Metadata] Title: {title}")

    # 2. 尝试获取字幕 (L2)
    transcript_data = run_script("fetch_transcript.py", [url])
    
    context_source = ""
    context_content = ""

    if transcript_data.get("status") == "success":
        print("✅ [Transcript] Successfully extracted video transcript.")
        context_source = "Transcript"
        context_content = transcript_data.get("transcript")
    else:
        print(f"⚠️ [Transcript] Failed/Unavailable: {transcript_data.get('message')}")
        print("🔄 [Fallback] Switching to Metadata + Search Strategy...")
        
        # 3. 降级策略 (L3)
        context_source = "Metadata_and_Search"
        context_content = f"Title: {title}\nDescription: {metadata.get('description')}\n"
        
        # 可以在这里提示主 Agent 去搜索，或者直接返回指令让主 Agent 去搜
        # 为了简单，我们这里返回一个特殊的标志，告诉主 Agent "我尽力了，剩下的你来搜"

    # 4. 生成给主 Agent 的最终指令
    final_output = {
        "skill": "WebResearcher",
        "target_url": url,
        "primary_source": context_source,
        "content_preview": context_content[:500] + "...", # 预览
        "full_content": context_content,
        "instruction_to_agent": ""
    }

    if context_source == "Transcript":
        final_output["instruction_to_agent"] = (
            f"Please analyze the following transcript for the video '{title}'. "
            "Focus on extracting key technical details, code examples, and the core argument. "
            "Ignore conversational fillers."
        )
    else:
        final_output["instruction_to_agent"] = (
            f"The video '{title}' has no subtitles. "
            f"Based on the description: '{metadata.get('description')}', "
            "please PERFORM A WEB SEARCH for this video title to find summaries or reviews, "
            "and then synthesize a report."
        )

    print(json.dumps(final_output, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py <url>")
    else:
        main(sys.argv[1])
