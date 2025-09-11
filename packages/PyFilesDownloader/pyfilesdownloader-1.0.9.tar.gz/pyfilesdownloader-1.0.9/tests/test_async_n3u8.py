# coding: utf-8
import shutil

from PyFilesDownloader.aio.m3u8 import AsyncM3U8Downloader

url = 'https://svip.high21-playback.com/20250130/41326_717cc871/index.m3u8'
save_path = './download'
file_name = '哪吒之魔童降世.mp4'
loader = AsyncM3U8Downloader(url, save_path, file_name, merge_mode='ffmpeg')
loader.run()
