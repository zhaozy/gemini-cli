import sys
import json
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import TextFormatter

def get_transcript(video_url):
    try:
        video_id = video_url.split('v=')[-1].split('&')[0]
        
        # 实例化 API
        ytt_api = YouTubeTranscriptApi()
        
        # 使用实例方法 list
        transcript_list = ytt_api.list(video_id)
        
        # 尝试寻找手动创建的中文或英文字幕
        try:
            transcript = transcript_list.find_manually_created_transcript(['zh-Hans', 'zh-TW', 'en'])
        except:
            # 如果没有手动，尝试自动生成的
            try:
                transcript = transcript_list.find_generated_transcript(['zh-Hans', 'zh-TW', 'en'])
            except:
                 # 如果都没找到指定语言，直接拿第一个可用的并翻译（如果需要，这里暂取第一个）
                 transcript = next(iter(transcript_list))

        # 获取实际内容
        transcript_data = transcript.fetch()
        
        formatter = TextFormatter()
        text_formatted = formatter.format_transcript(transcript_data)
        
        return {
            "status": "success",
            "transcript": text_formatted[:20000]
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"status": "error", "message": "No URL provided"}))
    else:
        print(json.dumps(get_transcript(sys.argv[1]), ensure_ascii=False, indent=2))
