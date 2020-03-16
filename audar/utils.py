import requests
import youtube_dl
from tqdm import tqdm


def download_file(url, output_dir="./"):
    output_file = output_dir + url.split("/")[-1]

    r = requests.get(url, stream=True)
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024 #1 Kibibyte
    t = tqdm(total=total_size, unit='iB', unit_scale=True)
    with open(output_file, 'wb') as f:
        for data in r.iter_content(block_size):
            t.update(len(data))
            f.write(data)

def download_ytaudio(ytid, start_seconds=None, end_seconds=None, output_dir="."):
    class MyLogger(object):
        def debug(self, msg):
            pass
        def warning(self, msg):
            pass
        def error(self, msg):
            print(msg)

    def my_hook(d):
        if d['status'] == 'finished':
            print('Done downloading, now converting ...')
        
    ydl_opts = {
        'outtmpl': f'{output_dir}/%(id)s.%(ext)s',
        'format': 'bestaudio/best',
        'noplaylist' : True,
        'keepvideo': False,
        'geo_bypass': True,
        'writeinfojson': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'flac'
        }],
        "start_time": 3, 
        "end_time": 5,
        'logger': MyLogger(),
        # 'progress_hooks': [my_hook],
    }
    try:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={ytid}"])
    except Exception as e:
        print(e)
