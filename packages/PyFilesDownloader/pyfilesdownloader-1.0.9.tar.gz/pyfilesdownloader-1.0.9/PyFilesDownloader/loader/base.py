# coding: utf-8
import re
import shutil
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Union, Callable, TypedDict, Unpack, List, Tuple

import requests

requests.packages.urllib3.disable_warnings()


class DownloadDict(TypedDict):
    """
    下载器的关键字参数
    :param headers: 请求头
    :param proxies: 代理
    :param timeout: 超时时间
    :param verify_ssl: 验证 SSL 证书
    :param log_func: 日志函数
    :param progress_func: 进度函数
    """
    headers: Union[dict, None]
    proxies: Union[dict, None]
    timeout: int
    verify_ssl: bool
    encoding: str
    is_overwrite: bool
    log_func: Callable
    progress_func: Callable


class DownloaderBase(ABC):
    session = requests.Session()

    def __init__(
            self,
            url: str,
            save_path: Union[Path, str],
            file_name: str = None,
            create_temp_dir: bool = True,
            **kwargs: Unpack[DownloadDict]
    ):
        """
        初始化下载器
        :param url: 下载的 url
        :param save_path: 保存路径
        :param file_name: 文件名 (默认使用 url 中的文件名，带后缀)
        :param kwargs: 下载器的关键字参数
        """
        self.url = url
        # 保存路径
        if isinstance(save_path, str):
            self.save_path = Path(save_path)
        else:
            self.save_path = save_path
        self.file_name = file_name
        self.save_file_path = self.save_path / (self.file_name or Path(url).name)
        self.save_path.mkdir(exist_ok=True, parents=True)
        # 临时目录
        self.temp_dir = self.save_path / Path(file_name).stem / 'temp'
        if create_temp_dir:
            self._create_temp_dir()

        self.headers = kwargs.get('headers', {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0'
        })
        self.proxies = kwargs.get('proxies')
        self.timeout = kwargs.get('timeout')
        self.verify_ssl = kwargs.get('verify_ssl')
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.is_overwrite = kwargs.get('is_overwrite', False)
        self.log_func = kwargs.get('log_func')
        self.progress_func = kwargs.get('progress_func')
        self.kwargs = kwargs

        # 标记
        self.__is_running = False
        self.__is_stop = False
        self.progress = 0

    def _create_temp_dir(self):
        """
        创建临时目录
        :return:
        """
        self.successful_file_path = self.temp_dir / 'successful.txt'
        self.failed_file_path = self.temp_dir / 'failed.txt'
        self.ffmpeg_file_path = self.temp_dir / 'ffmpeg.txt'
        # 创建临时目录
        self.temp_dir.mkdir(exist_ok=True, parents=True)
        self.successful_file_path.touch(exist_ok=True)
        self.failed_file_path.touch(exist_ok=True)
        self.ffmpeg_file_path.touch(exist_ok=True)

    def send_request(self, url: str, headers: dict = None, *, method: str = 'GET', **kwargs):
        """
        发送请求
        :param url: 请求的url
        :param headers: 请求头
        :param method: 请求方法
        :return:
        """
        response = self.session.request(
            method,
            url,
            headers=headers,
            proxies=self.proxies,
            timeout=self.timeout,
            verify=self.verify_ssl,
            **kwargs
        )
        response.raise_for_status()
        return response

    def getURLLength(self, url: str, **kwargs) -> int:
        """
        获取 url 长度
        :param url: 请求的url
        :return:
        """
        response = self.send_request(url, headers=self.headers, method='HEAD', **kwargs)
        length = response.headers.get('Content-Length')
        if length is None:
            length = 0
        return int(length)

    @abstractmethod
    def run(self):
        """
        开始下载
        这个方法应该通过子类来实现。
        :return:
        """
        raise NotImplementedError

    def getSaveSize(self) -> int:
        """
        获取文件大小
        :return:
        """
        raise NotImplementedError

    def getSavePath(self) -> Path:
        """
        获取保存路径
        :return:
        """
        return self.save_file_path

    def setSaveData(self, data: bytes):
        """
        设置保存数据
        :param data:
        :return:
        """
        with open(self.save_file_path, 'wb') as f:
            f.write(data)

    def addSaveData(self, data: bytes):
        """
        添加保存数据
        :param data:
        :return:
        """
        if not data:
            return
        with open(self.save_file_path, 'ab') as f:
            f.write(data)

    def addSuccessfulData(self, *args: Union[str, List[str], Tuple[str]]):
        """
        设置成功下载的 args
        :param args:
        :return:
        """
        with open(self.successful_file_path, 'a', encoding=self.encoding) as f:
            f.write(' | '.join(args) + '\n')

    def getSuccessfulData(self) -> List[str]:
        """
        获取成功下载的 args
        :return:
        """
        with open(self.successful_file_path, 'r', encoding=self.encoding) as f:
            return [line.strip() for line in f.readlines()]

    def addFailedData(self, *args: Union[str, List[str], Tuple[str]]):
        """
        设置失败下载的 args
        :param args:
        :return:
        """
        with open(self.failed_file_path, 'a', encoding=self.encoding) as f:
            f.write(' | '.join(args) + '\n')

    def getFailedData(self) -> List[str]:
        """
        获取失败下载的 args
        :return:
        """
        with open(self.failed_file_path, 'r', encoding=self.encoding) as f:
            return [line.strip() for line in f.readlines()]

    def setTempData(self, name: str, data: bytes):
        """
        设置临时数据
        :param name: 文件名
        :param data: 数据
        :return:
        """
        with open(self.temp_dir / name, 'wb') as f:
            f.write(data)
            self.addSuccessfulData(name)
            self.addFfmpegLog(name)

    def getTempDirFiles(self, suffix: str, isList: bool = False):
        """
        获取临时目录文件
        :param suffix: 文件后缀
        :param isList: 是否返回列表
        :return:
        """
        files = self.temp_dir.glob(f'**/*.{suffix}')
        if isList:
            return [file for file in files]
        else:
            return files

    def deleteTempDir(self):
        """
        删除临时目录
        :return:
        """
        try:
            shutil.rmtree(self.temp_dir.parent)
        except Exception as e:
            print(f'删除临时目录失败: {e}')

    def deleteSaveFile(self):
        """
        删除保存文件
        :return:
        """
        if self.save_file_path.exists():
            self.save_file_path.unlink()

    def getFileSize(self, file: Union[str, Path] = None) -> int:
        """
        获取文件大小
        :param file: 文件路径
        :return:
        """
        if isinstance(file, str):
            file = Path(file)
        if not file.exists():
            return 0
        file_size = file.stat().st_size
        return file_size

    def stop(self):
        self.__is_stop = True
        self.__is_running = False

    def isStop(self) -> bool:
        """
        是否停止
        :return:
        """
        return self.__is_stop

    def isRunning(self) -> bool:
        """
        是否正在运行
        :return:
        """
        return self.__is_running

    def setRunning(self, is_running: bool):
        """
        设置是否正在运行
        :param is_running:
        :return:
        """
        self.__is_running = is_running

    def setStop(self, is_stop: bool):
        """
        设置是否停止
        :param is_stop:
        :return:
        """
        self.__is_stop = is_stop

    def getProgress(self) -> float:
        """
        获取下载进度
        :return:
        """
        return self.progress

    def setProgress(self, progress: float):
        """
        设置下载进度
        :param progress:
        :return:
        """
        self.progress = progress
        if self.progress_func:
            self.progress_func(progress)

    def setLog(self, log: str, show_log: bool = True):
        """
        设置日志信息
        :param log:
        :param show_log: 是否显示日志
        :return:
        """
        if self.log_func:
            self.log_func(log)
        if show_log:
            print(log)

    def getDownloadedSize(self) -> int:
        """
        获取已下载大小
        :return:
        """
        return self.getFileSize(self.save_file_path)

    def getSpeed(self) -> float:
        """
        获取下载速度(网络速度)
        :return:
        """
        raise NotImplementedError

    def getInitialProgress(self, sum_size: int) -> int:
        """
        获取初始下载进度信息
        :return:
        """
        return 0

    def addFfmpegLog(self, name: str):
        """
        设置 ffmpeg 日志信息
        :param name:
        :return:
        """
        with open(self.ffmpeg_file_path, 'a', encoding=self.encoding) as f:
            f.write(f"file '{name}'\n")

    def sortFfmpegLog(self):
        """
        排序 ffmpeg 日志信息
        :return:
        """
        files = self.ffmpeg_file_path.read_text(encoding=self.encoding).split('\n')
        # 去除空行
        files = list(filter(None, files))
        # 按文件名排序
        def file_sort(x):
            return re.findall(r'\d+', x)[0]
        files.sort(key=file_sort)
        self.ffmpeg_file_path.write_text('\n'.join(files), encoding=self.encoding)