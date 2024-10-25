import base64
import shutil
from pathlib import Path

import urllib3

from tool.Common import Config
from tool.Exif import Exif
from loguru import logger


class Script:

    def __init__(self, files, target):
        self.files = files
        self.target = target
        self.t = Path(self.target)
        if not self.t.exists():
            self.t.mkdir(parents=True, exist_ok=True)
        self.config = Config()
        self.bar = None
        self.total = 0

        self.wb = None

    def run(self, error):
        files = self.files
        for file in files:
            try:
                fields = Exif.read(file)
                res = self.predict(self.path2base64(file))
                if res:
                    counts = {}
                    for item in res:
                        score = item.get("score")
                        tName = item.get("name")
                        if score>=self.config.score and tName not in self.config.exclude:
                            counts[item.get("name")] = counts.get(item.get("name"), 0) + 1
                    for name in counts.keys():
                        temp = self.t / name
                        if not temp.exists():
                            temp.mkdir(parents=True, exist_ok=True)
                        targetFile = temp / file.name
                        shutil.copy(file, targetFile)

                        add = [file.name,
                               fields.get("Image DateTime"),
                               fields.get("Image Make") + fields.get("Image Model"),
                               name,
                               counts.get(name),
                               str(targetFile)]
                        self.wb.write_line(add)
                if self.bar:
                    self.bar.setValue(min(100, self.bar.value() + int(100 * 1.0 / self.total)))
            except Exception as e:
                logger.error(f"处理文件{file}时发生异常：")
                logger.error(e.args)
                error.emit()
        """
        [{'bbox': [27, 165, 109, 173], 'group_name': '人', 'group_score': 0.9478, 'name': '野猪', 'score': 0.8711}]
        """

    def set_bar(self, bar):
        self.bar = bar

    def set_wb(self, wb):
        self.wb = wb

    def set_total(self, total):
        self.total = total

    @staticmethod
    def path2base64(path):
        """
        图片转base64
        :param path: 图片路径
        :return: base64
        """
        with open(path, 'rb') as image_file:
            encoded_string = base64.b64encode(image_file.read())
            return encoded_string.decode('utf-8')

    def predict(self, img) -> list[dict]:
        http = urllib3.PoolManager()
        data = {
            'image': img
        }
        url = self.config.api
        response = http.request('POST', url, json=data)
        data = response.json()
        if data.get('status', -1) == 0:
            return data.get('results')

# if __name__ == '__main__':
#     s = Script(r"D:\dddd\hwxj 测试数据", "D:\dddd\结果")
#     res = s.predict(s.path2base64(r"D:\1.jpg"))
#     print(res)
    # s.run()
