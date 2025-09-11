# coding: utf-8
from pathlib import Path
from queue import Queue
from typing import Union, Unpack

from .qt import QThread, Signal
from ..loader import StreamDownloader, DownloadDict


class StreamDownloaderThread(QThread):
    """
    单线程下载器
    """
    progressSignal = Signal(float)
    logSignal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loader: StreamDownloader = None
        self.url = None
        self.save_path = None
        self.save_name = None
        self.chunk_size = None
        self.kwargs = None

    def run(self):
        loader = StreamDownloader(
            url=self.url,
            save_path=self.save_path,
            save_name=self.save_name,
            chunk_size=self.chunk_size,
            log_func=self.logSignal.emit,
            progress_func=self.progressSignal.emit,
            **self.kwargs
        )
        loader.run()

    def stop(self):
        self.loader.stop()

    def setParams(
            self,
            url: str,
            save_path: Union[str, Path],
            save_name: str = None,
            chunk_size: int = 1024,
            **kwargs: Unpack[DownloadDict]
    ):
        self.url = url
        self.save_path = save_path
        self.save_name = save_name
        self.chunk_size = chunk_size
        self.kwargs = kwargs


class QueueStreamDownloaderThread(QThread):
    """
    多线程下载器，使用队列管理下载任务
    """
    progressSignal = Signal(float)
    logSignal = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.loader: StreamDownloader = None
        self.queue = Queue()
        self._isStop = False

    def run(self):
        while not self.queue.empty():
            if self._isStop:
                break
            url, save_path, save_name, chunk_size, kwargs = self.queue.get()
            msg = f"开始下载{url}, 保存路径{save_path}, 文件名{save_name}"
            self.logSignal.emit(msg)
            print(msg)
            self.loader = StreamDownloader(
                url=url,
                save_path=save_path,
                save_name=save_name,
                chunk_size=chunk_size,
                log_func=self.logSignal.emit,
                progress_func=self.progressSignal.emit,
                **kwargs
            )
            self.loader.run()

    def stop(self):
        self._isStop = True
        self.loader.stop()

    def addParams(
            self,
            url: str,
            save_path: Union[str, Path],
            save_name: str = None,
            chunk_size: int = 1024,
            **kwargs: Unpack[DownloadDict]
    ):
        self.queue.put((url, save_path, save_name, chunk_size, kwargs))
