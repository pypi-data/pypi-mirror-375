# coding: utf-8
from pathlib import Path
from typing import Union
import sys

QtExist = False
QtVersion = None
QtList = [
    'PyQt5',
    'PySide2',
    'PySide6',
    'PyQt6',
]
for qt in QtList:
    try:
        __import__(qt)
        QtExist = True
        QtVersion = qt
        break
    except ImportError:
        pass
if not QtExist:
    raise ImportError('No Qt library found. Please install one of the following libraries: {}'.format(QtList))

if QtVersion == 'PyQt5':
    from PyQt5.QtCore import QThreadPool, QThread, pyqtSignal as Signal, pyqtProperty as Property, QObject, QProcess
elif QtVersion == 'PyQt6':
    from PyQt6.QtCore import QThreadPool, QThread, pyqtSignal as Signal, pyqtProperty as Property, QObject, QProcess
elif QtVersion == 'PySide2':
    from PySide2.QtCore import QThreadPool, QThread, Signal, Property, QObject, QProcess
elif QtVersion == 'PySide6':
    from PySide6.QtCore import QThreadPool, QThread, Signal, Property, QObject, QProcess
else:
    raise ImportError('No Qt library found. Please install one of the following libraries: {}'.format(QtList))

def isWindows():
    return sys.platform.startswith('win')


def runProcess(executable: Union[str, Path], args=None, timeout=5000, cwd=None, encoding='gbk') -> str:
    process = QProcess()

    if cwd:
        process.setWorkingDirectory(str(cwd))

    process.start(str(executable).replace("\\", "/"), args or [])
    process.waitForFinished(timeout)
    return process.readAllStandardOutput().data().decode(encoding)
