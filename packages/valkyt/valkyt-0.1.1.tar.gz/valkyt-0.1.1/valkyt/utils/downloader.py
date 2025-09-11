import os
import requests
import tempfile
import shutil
import yt_dlp

from uuid import uuid4
from dekimashita import Dekimashita
from requests import Response
from loguru import logger

from .directory import Dir
from .fileIO import File

class Down:

    @staticmethod
    def curl(url: str, path: str, headers: dict = None, cookies: dict = None, extension: str = None) -> Response:
        Dir.create_dir(paths='/'.join(path.split('/')[:-1]))
        response = requests.get(url=url, headers=headers, cookies=cookies, verify=False, timeout=900)
        with open(path, 'wb') as f:
            f.write(response.content)

        return response
    
    @staticmethod
    def curlv2(path: str, response: Response, extension: str = None) -> Response:
        Dir.create_dir(paths='/'.join(path.split('/')[:-1]))
        with open(path, 'wb') as f:
            f.write(response.content)
            
    
    @staticmethod
    def youtube_download(url):
        logger.info(f'VIDEO DOWNLOAD :: URL [ {url} ]')
        ydl_opts = {
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
            'http_headers': {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'},
            'nocheckcertificate': True
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print("start...")
                
                info = ydl.extract_info(url, download=False)
                
                if 'entries' in info:
                    video_info = info['entries'][0]
                else:
                    video_info = info
                
                formats = video_info.get('formats', [])
                
                def safe_get_filesize(f):
                    return f.get('filesize') or f.get('filesize_approx') or 0
                
                best_format = max(formats, key=safe_get_filesize)
                video_url = best_format['url']
                
                with ydl.urlopen(video_url) as response:
                    video_bytes = response.read()
                
            print("Unduhan selesai!")
            return video_bytes
        except Exception as e:
            print(f"Terjadi kesalahan: {str(e)}")
            return None
        
    
