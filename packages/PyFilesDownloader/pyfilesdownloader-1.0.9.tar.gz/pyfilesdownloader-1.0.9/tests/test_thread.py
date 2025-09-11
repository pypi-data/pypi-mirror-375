# coding: utf-8
from PyFilesDownloader.Qt import M3u8DownloaderThread

import sys
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton


class MainWindow(QWidget):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setWindowTitle("PyDownloader")
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
