import sys

if sys.platform.startswith('win'):
    ffmpeg_path = r'.\\ffmpeg\\bin\\ffmpeg.exe'  # Windows path
else:
    ffmpeg_path = './ffmpeg/bin/ffmpeg'  # Linux/macOS path (không có .exe)