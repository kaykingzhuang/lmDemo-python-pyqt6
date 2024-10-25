import sys
from pathlib import Path

from PyQt6 import QtWidgets
from PyQt6.QtCore import QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import QFileDialog, QMessageBox
from loguru import logger

from tool.Common import Config
from tool.Excel import Excel
from tool.MyThread import MyThread
from tool.script import Script
from tool.ui import Ui_Dialog

class Status(enumerate):
    wait = "待处理"
    handle = "处理中"
    finish = "处理完成"
    noSelect = "目录不可为空"
    error = "未知异常"

class MyApp(QtWidgets.QMainWindow, Ui_Dialog):


    def __init__(self):
        super(MyApp, self).__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(lambda: self.selectFolder(self.lineEdit))
        self.pushButton_2.clicked.connect(lambda: self.selectFolder(self.lineEdit_2))
        self.startBtn.clicked.connect(self.start)
        self.openBtn.clicked.connect(lambda: self.open_directory(self.lineEdit_2.text()))
        self.config = Config()
        logger.info(f"当前使用接口{self.config.api}")


        # 配置日志回滚
        logger.add(self.config.log_file_path, format="{time} {level} {message}",
                   rotation="00:00", retention="1 day")

        logger.info(
            f"程序初始化成功，当前配置为：处理图片类型->{self.config.suffix},"
            f"识别接口->{self.config.api},处理线程数->{self.config.thread},"
            f"过滤置信度->{self.config.score},排除物种名->{self.config.exclude}")

    def selectFolder(self, rev):
        directory = QFileDialog.getExistingDirectory(self, "选择文件夹", self.config.last_folder)
        if directory:
            self.config.last_folder = directory
            self.config.write_json()
            rev.setText(directory)

    def start(self):
        self.startBtn.setVisible(False)
        self.status.setText(Status.handle)

        wb = Excel()
        wb = wb.work_book().set_title_border(self.config.title)

        root = self.lineEdit.text()
        target = self.lineEdit_2.text()
        try:
            if not root or not target:
                raise Exception(Status.noSelect)
            self.bar.setValue(0)
            files = self.get_file_list(root)
            items = self.split_file_list(files, int(len(files) / self.config.thread) + 1)
            threads = []

            for item in items:
                s = Script(item,target)
                s.set_total(len(files))
                s.set_bar(self.bar)
                s.set_wb(wb)
                th = MyThread(s)
                threads.append(th)

            for i in range(len(threads)):
                threads[i].error.connect(self.error)
                threads[i].start()

            for th in threads:
                th.wait()

            # for th in threads:
            #     th.join()
        except Exception as e:
            print(e.args)
            out = Status.error
            QMessageBox.critical(None,"错误信息", str(e.args), QMessageBox.StandardButton.Ok)
        finally:
            save =  Path(Path(target) / "result.xlsx")
            if save.exists():
                save.unlink()
            wb.save(save.as_posix())
            self.done()

    # def begin(self):
    #     self.startBtn.setVisible(False)
    #     self.status.setText(Status.handle)


    def done(self):
        self.bar.setValue(100)
        self.status.setText(Status.finish)
        self.startBtn.setVisible(True)

    def error(self):
        self.status.setText(Status.error + ",详细内容查看log下日志文件")

    @staticmethod
    def open_directory(path):
        try:
            if not path:
                raise Exception("未选中保存目录！")
            url = QUrl.fromLocalFile(path)
            if not QDesktopServices.openUrl(url):
                raise Exception("打开目录失败！")
        except Exception as e:
            QMessageBox.critical(None,"错误信息", str(e.args), QMessageBox.StandardButton.Ok)


    def get_file_list(self, root) -> list[str]:
        directory = Path(root)
        s = []
        for item in self.config.suffix:
            s += list(directory.rglob(f"*.{item}"))
        return s

    @staticmethod
    def split_file_list(alist, size):
        return [alist[i:i + size] for i in range(0, len(alist), size)]


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.setFixedSize(window.width(), window.height())
    window.show()
    app.exec()
