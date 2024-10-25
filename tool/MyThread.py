import threading

from PyQt6.QtCore import QThread, pyqtSignal

from tool.script import Script


class MyThread(QThread):
    error = pyqtSignal()
    def __init__(self, s:Script):
        """
        初始化线程
        """
        super().__init__()
        self.s = s

    def run(self):

        self.s.run(self.error)

