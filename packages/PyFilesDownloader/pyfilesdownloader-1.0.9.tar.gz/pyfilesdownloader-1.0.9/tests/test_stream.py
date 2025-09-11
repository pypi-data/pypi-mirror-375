# coding: utf-8
from PyFilesDownloader import StreamDownloader

url = 'https://v16m-default.akamaized.net/e1d9304942ebc65508c9e50294e44e29/677bd662/video/tos/alisg/tos-alisg-ve-0051c001-sg/oUfbIGcZlzP1pj65fsCSE4BhARF9DOAYeqDgbE/?a=2011&bti=MzhALjBg&ch=0&cr=0&dr=0&net=5&cd=0%7C0%7C0%7C0&br=1128&bt=564&cs=0&ds=3&ft=XE5bCqq3mbuPD12imGcJ3wU1NmxdEeF~O5&mime_type=video_mp4&qs=0&rc=aTQ0PDRmPDdnODo7Ozc0OkBpank2aXM5cjZydzMzODYzNEBgLi4xMi0zXzAxLi1eLS1eYSNmXjVqMmRzYnBgLS1kMC1zcw%3D%3D&vvpl=1&l=20250106064655ECC206E262E86FE01FD4&btag=e000a8000'
save_path = 'download/不知为何我和尼特且宅的女忍者开始了同居生活'
save_name = '第一集.mp4'
downloader = StreamDownloader(url, save_path, save_name, is_overwrite=True)
downloader.run()
