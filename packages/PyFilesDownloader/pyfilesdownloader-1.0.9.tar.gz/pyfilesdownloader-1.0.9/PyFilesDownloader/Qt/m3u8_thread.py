# coding: utf-8
from pathlib import Path
from typing import Union

from .qt import QThread, Signal
from ..aio import AsyncM3U8Downloader


class M3u8DownloaderThread(QThread):
    progressSignal = Signal(float)
    logSignal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.url = None
        self.save_path = None
        self.file_name = None
        self.kwargs = {}

        self.loader: AsyncM3U8Downloader = None

    def run(self):
        self.loader = AsyncM3U8Downloader(
            url=self.url,
            save_path=self.save_path,
            file_name=self.file_name,
            progress_func=self.progressSignal.emit,
            log_func=self.logSignal.emit,
            isQt=True,
            **self.kwargs
        )
        self.loader.run()

    def stop(self):
        if self.loader:
            self.loader.stop()

    def setParams(self, url: str,
                  save_path: Union[Path, str],
                  file_name: str = None, **kwargs):
        self.url = url
        self.save_path = save_path
        self.file_name = file_name
        self.kwargs = kwargs
