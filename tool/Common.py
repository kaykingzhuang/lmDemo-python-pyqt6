import json
import pathlib
from pathlib import Path


class Config:
    """
        常量类（当根目录存在json时使用json内配置）
    """
    # 输出表格标题
    title = ["照片名", "拍摄时间", "设备名称", "物种名", "数量", "文件路径"]

    # 设置日志文件的路径
    log_file_path = "log/log_{time}.log"

    # 处理的文件后缀
    suffix = ["jpg", "png", "jpeg"]

    # 处理线程数
    thread = 3

    json_name = "config.json"

    last_folder = "/"

    score = 0.85

    api = "http://192.168.1.110:5000/predict"

    exclude = ["鸟","兽"]

    def __init__(self):
        js = self.init_json()
        self.title = js["title"]
        self.suffix = js["suffix"]
        self.thread = js["thread"]
        self.last_folder = js["last_folder"]
        self.api = js["api"]
        self.score = js["score"]
        self.exclude = js["exclude"]


    def init_json(self):
        file = Path(pathlib.Path.cwd()) / self.json_name

        if file.exists():
            with open(file.as_posix(), "r", encoding="utf-8") as f:
                js = json.load(f)
                return js
        else:
            self.write_json()
            return self.init_json()

    def write_json(self):
        file = Path(pathlib.Path.cwd()) / self.json_name
        data = {
            "title": self.title,
            "suffix": self.suffix,
            "thread": self.thread,
            "last_folder": self.last_folder,
            "api": self.api,
            "score": self.score,
            "exclude": self.exclude,
        }
        with open(file.as_posix(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        self.__init__()

# if __name__ == '__main__':
#     c = Config()
#     print(c.suffix)
#     print(c.thread)
#     print(c.title)
