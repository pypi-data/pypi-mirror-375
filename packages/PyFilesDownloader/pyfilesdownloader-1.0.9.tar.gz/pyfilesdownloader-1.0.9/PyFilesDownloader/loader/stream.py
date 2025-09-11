# coding: utf-8
from pathlib import Path
from typing import Union, Unpack

from .base import DownloaderBase, DownloadDict


class StreamDownloader(DownloaderBase):
    """
    流下载器
    """

    def __init__(
            self,
            url: str,
            save_path: Union[str, Path],
            save_name: str = None,
            chunk_size: int = 1024,
            **kwargs: Unpack[DownloadDict]
    ):
        """
        初始化下载器
        """
        super().__init__(url, save_path, save_name, create_temp_dir=False, **kwargs)
        self.chunk_size = chunk_size

    def _download(self):
        """
        下载文件
        :return:
        """
        if self.is_overwrite:
            self.deleteSaveFile()

        self.setLog('开始解析下载文件')
        local_file_size = self.getFileSize(self.save_file_path)
        length = self.getURLLength(self.url)
        self.getInitialProgress(length / self.chunk_size)
        if local_file_size == length and self.is_overwrite is False:
            print(f"文件{self.save_file_path}已存在，无需下载")
            return
        self.headers.update({"Range": f"bytes={local_file_size}-{length}"})
        response = self.send_request(self.url, headers=self.headers, stream=True)
        for index, chunk in enumerate(response.iter_content(chunk_size=self.chunk_size), 1):
            self.setRunning(True)
            if self.isStop():
                break
            self.addSaveData(chunk)
            progress = (index * self.chunk_size + local_file_size) / length * 100
            print(f"\r正在下载{self.file_name}, 进度 {progress:.2f} %", end='', flush=True)
            self.setLog(f"正在下载{self.file_name}, 进度{progress:.2f} %")
            self.setProgress(progress)
        self.setRunning(False)
        self.setStop(True)
        print(f"文件{self.save_file_path}下载完成")

    def getInitialProgress(self, sum_size: Union[int, float]):
        """
        获取初始进度
        :return:
        """
        if sum_size == 0:
            return 0
        file_size = self.getFileSize(self.save_file_path)
        progress = file_size / sum_size * 100
        self.setProgress(progress)
        return progress

    def run(self):
        """
        运行下载器
        :return:
        """
        self._download()
