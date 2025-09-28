#!/usr/bin/env python3
import sys
import re
import glob
from pathlib import Path

# Responsive iframe template
RESPONSIVE_IFRAME = '''
<div style="width:100%">
  <iframe
    src="{youtube_url}"
    title="YouTube video player"
    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share"
    referrerpolicy="strict-origin-when-cross-origin"
    allowfullscreen
    style="width:100%; aspect-ratio:16/9; border:0;"
  ></iframe>
</div>
'''

# Regex to match YouTube iframe src
IFRAME_PATTERN = re.compile(
    r'<iframe[^>]*src="https://www\.youtube\.com/embed/([^"?&]+)[^"]*"[^>]*></iframe>',
    re.IGNORECASE
)

# Regex to detect if the iframe is already inside a responsive div
RESPONSIVE_DIV_PATTERN = re.compile(
    r'<div[^>]*style="[^"]*width\s*:\s*100%[^"]*"[^>]*>.*?</div>',
    re.IGNORECASE | re.DOTALL
)

def replace_iframes_in_file(file_path):
    content = Path(file_path).read_text(encoding="utf-8")
    new_content = content

    # Skip if already inside <div style="width:100%">
    def repl(match):
        start, end = match.span()
        # Check if the iframe is inside a responsive div
        surrounding = content[max(0, start-50):min(len(content), end+50)]
        if 'width:100%' in surrounding:
            return match.group(0)  # already fixed
        video_id = match.group(1)
        youtube_url = f"https://www.youtube.com/embed/{video_id}"
        return RESPONSIVE_IFRAME.format(youtube_url=youtube_url)

    new_content, count = IFRAME_PATTERN.subn(repl, content)

    if count > 0:
        Path(file_path).write_text(new_content, encoding="utf-8")
        print(f"[+] Updated {file_path} ({count} iframe(s) replaced)")

def main():
    if len(sys.argv) < 2:
        print("Usage: python replace_iframes.py <path_or_glob>")
        sys.exit(1)

    paths = sys.argv[1:]
    files_to_process = []

    for path in paths:
        files_to_process.extend(glob.glob(path, recursive=True))

    for file_path in files_to_process:
        if file_path.endswith(".md"):
            replace_iframes_in_file(file_path)

if __name__ == "__main__":
    main()
