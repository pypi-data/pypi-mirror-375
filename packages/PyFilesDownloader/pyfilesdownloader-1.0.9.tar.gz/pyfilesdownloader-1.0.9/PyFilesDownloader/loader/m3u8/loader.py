# coding: utf-8
import os
import shutil
import time
import traceback
from pathlib import Path
from typing import Unpack, Union, Literal

from .cryptoModel import DecodeByte
from .method import redirected_resolution_url, m3u8_to_absolute_uris
from ..base import DownloaderBase, DownloadDict


class M3U8Downloader(DownloaderBase):
    def __init__(
            self,
            url: str,
            save_path: Union[Path, str],
            file_name: str = None,
            retry_count: int = 7,
            merge_mode: Literal['ffmpeg', 'merge'] = 'merge',
            ffmpeg_path: str = 'ffmpeg',
            isQt: bool = False,
            **kwargs: Unpack[DownloadDict]
    ):
        super().__init__(url, save_path, file_name, True, **kwargs)
        self.retry_count = retry_count
        self.merge_mode = merge_mode
        self.ffmpeg_path = ffmpeg_path
        self.is_qt = isQt
        self.index = 1
        self.sum_size = 1
        # 判断是否安装 ffmpeg
        if self.merge_mode == 'ffmpeg' and not shutil.which(self.ffmpeg_path):
            raise FileNotFoundError(f'未找到 ffmpeg，请安装 ffmpeg 并配置 ffmpeg_path 参数')

    def _download_ts(self,
                     ts_url: str,
                     ts_name: str,
                     key: dict, *,
                     retry_count: int = 1):
        self.setRunning(True)
        try:
            iv = key["iv"] if key.get("iv") else ts_name.split('.')[0].zfill(16)
            content = self.send_request(ts_url, self.headers).content
            if key.get("uri") and key.get("method") and key.get("key"):
                decoded_content = DecodeByte.do_decode(key["key"], iv, content, method=key.get("method", "AES-128"))
            else:
                decoded_content = content
            self.setTempData(ts_name, decoded_content)
            progress = (self.index / self.sum_size) * 100
            self.setProgress(progress)
            self.setLog(f'正在下载{self.file_name}, 进度 {progress:.2f} %', False)
            print(f"\r正在下载{self.file_name}, 进度 {progress:.2f} %", end='', flush=True)
            self.index += 1
        except Exception as e:
            err_msg = traceback.format_exc()
            print(f"下载 {ts_name} 失败，重试次数 {retry_count} 次，原因：{err_msg}")
            time.sleep(1)
            if retry_count < self.retry_count:
                retry_count += 1
                self._download_ts(ts_url, ts_name, key, retry_count=retry_count)
            else:
                self.addFailedData(ts_url, ts_name)
                print(f"下载 {ts_name} 失败，重试次数 {retry_count} 次，原因：{e}")

    def _download(self):
        if self.is_overwrite:
            self.deleteSaveFile()
        if self.save_file_path.exists() and not self.is_overwrite:
            self.setLog(f'{self.file_name} 已存在，跳过下载')
            return

        self.setLog(f'开始解析 {self.url}')
        resolved_url = redirected_resolution_url(self.url, headers=self.headers, verify_ssl=self.verify_ssl,
                                                 timeout=self.timeout)
        self.setLog(f'解析 {self.url} 完成，重定向 URL 为 {resolved_url}')
        self.setLog('判断是否需要解密 m3u8 文件')
        if resolved_url:
            playlists, key = m3u8_to_absolute_uris(resolved_url, headers=self.headers, verify_ssl=self.verify_ssl,
                                                   timeout=self.timeout)
        else:
            playlists, key = m3u8_to_absolute_uris(self.url, headers=self.headers, verify_ssl=self.verify_ssl,
                                                   timeout=self.timeout)
        msg = '判断是否需要解密 m3u8 文件完成, 开始下载 ts 文件列表'
        self.setLog(msg)
        self.sum_size = len(playlists)
        for index, ts_url in enumerate(playlists, 1):
            if self.isStop():
                break
            ts_name = f"{str(index).zfill(6)}.ts"
            if ts_name in self.getSuccessfulData():
                continue
            self._download_ts(ts_url, ts_name, key)
        self.setLog('下载完成')
        if self.isStop():
            return
        self.setLog('开始合并 ts 文件')
        self.merge_ts()
        self.deleteTempDir()
        self.setLog('合并完成')
        self.setRunning(False)
        self.setStop(True)

    def merge_ts(self):
        """
        合并ts文件
        """
        if self.merge_mode == 'ffmpeg':
            self._ffmpeg_merge()
        elif self.merge_mode == 'merge':
            self._merge_ts()

    def _ffmpeg_merge(self):
        """
        使用ffmpeg合并ts文件
        """
        self.sortFfmpegLog()
        cmd = f'{self.ffmpeg_path} -f concat -safe 0 -i  {self.ffmpeg_file_path}  -c  copy {self.save_file_path}'
        self.setLog(f'开始合并 {self.file_name}，命令：{cmd}')
        try:
            if self.is_qt:
                from ...Qt.qt import runProcess
                runProcess(cmd)
            else:
                os.system(cmd)
            self.setLog(f'合并 {self.file_name} 完成')
        except Exception as e:
            err_msg = traceback.format_exc()
            self.setLog(f'合并 {self.file_name} 失败')
            print(f'合并 {self.file_name} 失败，原因：{err_msg}')

    def _merge_ts(self):
        """
        合并ts文件
        """
        ts_files = self.getTempDirFiles('ts', isList=True)
        if not ts_files:
            print('没有找到ts文件')
            return
        ts_files.sort(key=lambda s: s.name.split('.')[0])
        length = len(ts_files)
        for i, ts_file in enumerate(ts_files, 1):
            ts_file: Path
            self.addSaveData(ts_file.read_bytes())
            self.setLog(f'正在合并{self.file_name}, 进度 {i / length * 100:.2f} %', False)
            print('\r合并中: {:3.2f}%'.format(i / length * 100), end='', flush=True)
        self.setLog(f'合并 {self.file_name} 完成')

    def run(self):
        self._download()

    def stop(self):
        self.setStop(True)
        self.setRunning(False)
        self.setLog('下载已停止')
