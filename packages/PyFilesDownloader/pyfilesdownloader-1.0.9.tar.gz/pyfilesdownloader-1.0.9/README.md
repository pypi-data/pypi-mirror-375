# [PyFilesDownloader](PyFilesDownloader)

#### 介绍

PyFilesDownloader是一个基于Python的下载器，可以下载各种网站的资源。

#### 安装依赖

```python
pip install requests
pip install loguru
pip install pycryptodome
pip install m3u8
```

#### 安装教程

```python
pip install PyFilesDownloader
```

#### 使用说明

#### 示例代码

##### 下载单个文件

```python
from PyFilesDownloader import StreamDownloader

url = 'https://v16m-default.akamaized.net/e1d9304942ebc65508c9e50294e44e29/677bd662/video/tos/alisg/tos-alisg-ve-0051c001-sg/oUfbIGcZlzP1pj65fsCSE4BhARF9DOAYeqDgbE/?a=2011&bti=MzhALjBg&ch=0&cr=0&dr=0&net=5&cd=0%7C0%7C0%7C0&br=1128&bt=564&cs=0&ds=3&ft=XE5bCqq3mbuPD12imGcJ3wU1NmxdEeF~O5&mime_type=video_mp4&qs=0&rc=aTQ0PDRmPDdnODo7Ozc0OkBpank2aXM5cjZydzMzODYzNEBgLi4xMi0zXzAxLi1eLS1eYSNmXjVqMmRzYnBgLS1kMC1zcw%3D%3D&vvpl=1&l=20250106064655ECC206E262E86FE01FD4&btag=e000a8000'
save_path = 'download/不知为何我和尼特且宅的女忍者开始了同居生活'
save_name = '第一集.mp4'
downloader = StreamDownloader(url, save_path, save_name, is_overwrite=True)
downloader.run()
```

##### 下载M3U8格式的视频

> 注意：M3U8格式的视频需要使用M3U8Downloader类进行下载，该类会自动解析M3U8文件并下载视频。
>
> 注意：M3U8格式的视频下载速度较慢，请耐心等待。
>

##### 同步下载

```python
from PyFilesDownloader import M3U8Downloader

url = 'https://v.cdnlz22.com/20250101/10507_73949974/index.m3u8'
save_path = './download/上班族转生异世界当上了四天王不是很正常吗'
file_name = '第一集.mp4'
loader = M3U8Downloader(url, save_path, file_name)
loader.run()
```

##### 异步下载

```python
from PyFilesDownloader.async_loader.async_m3u8 import AsyncM3U8Downloader

url = 'https://v.cdnlz22.com/20250101/10507_73949974/index.m3u8'
save_path = './download/上班族转生异世界当上了四天王不是很正常吗'
file_name = '第一集.mp4'
loader = AsyncM3U8Downloader(url, save_path, file_name)
loader.run()

```

#### Qt下载器

> 注意：Qt下载器需要安装`PyQt5\PyQt6\PySide2\PySide6`库。

##### 下载单个文件

```python
# coding: utf-8
from PyFilesDownloader.Qt import StreamDownloaderThread
from PySide6.QtCore import QCoreApplication
import sys

app = QCoreApplication(sys.argv)
url = 'https://v16m-default.akamaized.net/e1d9304942ebc65508c9e50294e44e29/677bd662/video/tos/alisg/tos-alisg-ve-0051c001-sg/oUfbIGcZlzP1pj65fsCSE4BhARF9DOAYeqDgbE/?a=2011&bti=MzhALjBg&ch=0&cr=0&dr=0&net=5&cd=0%7C0%7C0%7C0&br=1128&bt=564&cs=0&ds=3&ft=XE5bCqq3mbuPD12imGcJ3wU1NmxdEeF~O5&mime_type=video_mp4&qs=0&rc=aTQ0PDRmPDdnODo7Ozc0OkBpank2aXM5cjZydzMzODYzNEBgLi4xMi0zXzAxLi1eLS1eYSNmXjVqMmRzYnBgLS1kMC1zcw%3D%3D&vvpl=1&l=20250106064655ECC206E262E86FE01FD4&btag=e000a8000'
save_path = 'download/不知为何我和尼特且宅的女忍者开始了同居生活'
save_name = '第一集.mp4'
downloader = StreamDownloaderThread(app)
downloader.setParams(url, save_path, save_name, is_overwrite=True)
downloader.start()
sys.exit(app.exec())

```

循环下载

```python
# coding: utf-8
from PyFilesDownloader.Qt import QueueStreamDownloaderThread
from PySide6.QtCore import QCoreApplication
import sys

app = QCoreApplication(sys.argv)
url = 'https://v16m-default.akamaized.net/e1d9304942ebc65508c9e50294e44e29/677bd662/video/tos/alisg/tos-alisg-ve-0051c001-sg/oUfbIGcZlzP1pj65fsCSE4BhARF9DOAYeqDgbE/?a=2011&bti=MzhALjBg&ch=0&cr=0&dr=0&net=5&cd=0%7C0%7C0%7C0&br=1128&bt=564&cs=0&ds=3&ft=XE5bCqq3mbuPD12imGcJ3wU1NmxdEeF~O5&mime_type=video_mp4&qs=0&rc=aTQ0PDRmPDdnODo7Ozc0OkBpank2aXM5cjZydzMzODYzNEBgLi4xMi0zXzAxLi1eLS1eYSNmXjVqMmRzYnBgLS1kMC1zcw%3D%3D&vvpl=1&l=20250106064655ECC206E262E86FE01FD4&btag=e000a8000'
save_path = 'download/不知为何我和尼特且宅的女忍者开始了同居生活'
save_name = '第一集.mp4'
downloader = QueueStreamDownloaderThread(app)
downloader.setParams(url, save_path, save_name, is_overwrite=True)
downloader.setParams(url, save_path, save_name, is_overwrite=True)
downloader.setParams(url, save_path, save_name, is_overwrite=True)
downloader.start()
sys.exit(app.exec())

```

##### 下载M3U8格式的视频

```python
# coding: utf-8
from PyFilesDownloader.Qt import M3u8DownloaderThread

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PyFilesDownloader")
        self.verticalLayout = QVBoxLayout(self)
        self.startButton = QPushButton(self)
        self.stopButton = QPushButton(self)

        self.downloadThread = M3u8DownloaderThread(self)

        self.startButton.setText("开始下载")
        self.stopButton.setText("停止下载")
        self.verticalLayout.addWidget(self.startButton)
        self.verticalLayout.addWidget(self.stopButton)

        self.startButton.clicked.connect(self.startDownload)
        self.stopButton.clicked.connect(self.stopDownload)

    def startDownload(self):
        self.downloadThread.setParams(
            url='https://v.cdnlz22.com/20250101/10507_73949974/index.m3u8',
            save_path='./download/上班族转生异世界当上了四天王不是很正常吗',
            file_name='第一集.mp4',
            semaphore=10
        )
        self.downloadThread.start()

    def stopDownload(self):
        self.downloadThread.stop()


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.resize(400, 300)
    window.show()

    # 运行程序
    sys.exit(app.exec())


```

#### 参与贡献

> 1. 赤鸢仙人创建本仓库
> 2. 新建 master 分支
> 3. 提交代码
> 4. 新建 Pull Request
