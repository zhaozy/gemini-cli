import sys
import urllib.request
import re
import json

def get_metadata(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    try:
        req = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8', errors='ignore')
            
            # Extract Title
            title_match = re.search(r'<title>(.*?)</title>', html)
            title = title_match.group(1).replace("- YouTube", "").strip() if title_match else "Unknown Title"
            
            # Extract Description (og:description)
            desc_match = re.search(r'<meta property="og:description" content="(.*?)"', html)
            description = desc_match.group(1) if desc_match else ""
            
            return {
                "title": title,
                "description": description,
                "url": url
            }
    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No URL provided"}))
    else:
        print(json.dumps(get_metadata(sys.argv[1]), indent=2, ensure_ascii=False))
