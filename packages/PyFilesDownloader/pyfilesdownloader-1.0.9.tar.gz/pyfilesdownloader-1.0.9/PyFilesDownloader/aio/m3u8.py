# coding: utf-8
import asyncio
from time import sleep
from typing import List

from ..loader import M3U8Downloader, m3u8_to_absolute_uris, redirected_resolution_url


class AsyncM3U8Downloader(M3U8Downloader):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.semaphore = kwargs.get('semaphore', 4)
        self.index = 1
        self.sum_size = 0
        self.loop: asyncio.AbstractEventLoop = None

    async def _async_download_ts(self, urls: List[str], key: dict):
        print('=' * 100)
        tasks = []
        for index, ts_url in enumerate(urls, 1):
            ts_name = f"{str(index).zfill(6)}.ts"
            if ts_name in self.getSuccessfulData():
                self.index += 1
                continue
            async with asyncio.Semaphore(self.semaphore):
                task = self.loop.create_task(
                    asyncio.to_thread(self._download_ts, ts_url, ts_name, key))
                tasks.append(task)

        await asyncio.gather(*tasks)


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
        # 下载 ts 文件列表
        self.setLog('判断是否需要解密 m3u8 文件完成, 开始下载 ts 文件列表')
        self.sum_size = len(playlists)
        # 异步下载 ts 文件
        # 主逻辑, 使用事件循环启动异步任务
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)

        try:
            self.loop.run_until_complete(self._async_download_ts(playlists, key))
        except asyncio.CancelledError as e:
            print(e)
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()
        del self.loop
        self.loop = None

        # 合并 ts 文件
        if self.isStop():
            return
        self.setLog('开始合并 ts 文件')
        self.merge_ts()
        self.deleteTempDir()

    def stop(self):
        self.setStop(True)
        if not self.loop:
            return
        tasks = asyncio.all_tasks(self.loop)
        # 取消所有任务
        for task in tasks:
            task: asyncio.Task
            task.cancel()
        # 等待所有任务完成
        while not all(task.done() for task in tasks):  # 等待所有任务完成
            for task in tasks:
                try:
                    task.cancel()
                except asyncio.CancelledError:
                    pass
                except Exception as e:
                    raise e
            sleep(0.01)

    def isRunning(self):
        if self.loop:
            return self.loop.is_running()
        else:
            return super().isRunning()

    def isStop(self):
        if self.loop:
            return self.loop.is_closed()
        else:
            return super().isStop()
