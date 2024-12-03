import base64
import shutil
from pathlib import Path

import cv2
import urllib3

from tool.Common import Config
from tool.Exif import Exif
from loguru import logger


class Script:

    def __init__(self, files, target):
        self.files = files
        self.target = target
        self.t = Path(self.target)
        self.o_path = self.t / "可疑物种"
        if not self.t.exists():
            self.t.mkdir(parents=True, exist_ok=True)
        self.config = Config()
        self.bar = None
        self.total = 0

        self.wb = None

        self.previous = []

    def run(self, error, process):
        files = self.files
        for file in files:
            try:
                fields = Exif.read(file)
                suffix = file[file.rfind(".")+1:]
                # suffix:str = suffix[1:]
                suffix = suffix.lower()
                file_name = file[file.rfind("\\")+1:]
                if suffix in self.config.IMG:
                    counts, others = self.predict_image(file)
                    self.previous = [counts, others]
                else:
                    if self.previous:
                        counts, others = self.previous[:]
                    else:
                        counts, others = self.predict_video(file)
                if counts:
                    """确种"""
                    for name in counts.keys():
                        temp = self.t / name
                        if not temp.exists():
                            temp.mkdir(parents=True, exist_ok=True)
                        targetFile = temp / file_name
                        shutil.copy(file, targetFile)

                        add = [file_name,
                               fields.get("Image DateTime"),
                               fields.get("Image Make") + fields.get("Image Model"),
                               name,
                               counts.get(name),
                               str(targetFile)]
                        self.wb.sheet.append(add)
                elif others:
                    """可疑物种"""
                    for name in others.keys():
                        temp = self.o_path / name
                        if not temp.exists():
                            temp.mkdir(parents=True, exist_ok=True)
                        targetFile = temp / file_name
                        shutil.copy(file, targetFile)
                        add = [file_name,
                               fields.get("Image DateTime"),
                               fields.get("Image Make") + fields.get("Image Model"),
                               name,
                               others.get(name),
                               str(targetFile)]
                        self.wb.sheet2.append(add)

                process.emit()

            except Exception as e:
                logger.error(f"处理文件{file}时发生异常：")
                logger.error(e)
                error.emit()
        """
        [{'bbox': [27, 165, 109, 173], 'group_name': '人', 'group_score': 0.9478, 'name': '野猪', 'score': 0.8711}]
        """

    def predict(self,file):
        suffix = file.suffix
        suffix: str = suffix[1:]
        suffix = suffix.lower()
        if suffix in self.config.IMG:
            counts, others = self.predict_image(file)
        else:
            counts, others = self.predict_video(file)

    def predict_video(self, location):
        cap = cv2.VideoCapture(location)
        if not cap.isOpened():
            return {}
        c = 0
        counts = {}
        others = {}

        if not cap.isOpened():
            logger.error(f"视频文件异常->{location}")
            return counts, others

        while True:
            ret, frame = cap.read()
            if not ret:
                cap.release()
                break
            if c % self.config.drop_frames == 0:
                _, buffer = cv2.imencode('.jpg', frame)
                b = base64.b64encode(buffer.tobytes()).decode("utf-8")
                res = self.predict(b)
                counts, others = self.count_res(res, counts, others)
            c += 1

        if counts:
            """统计出现最多次数得物种，如果次数较少，归类为可疑物种"""
            max_item = max(counts, key=counts.get)
            counts = {max_item:counts[max_item]}

        if others:
            """只取出现最多的物种"""
            max_item = max(others, key=others.get)
            others = {max_item:others[max_item]}
        return counts,others

    def predict_image(self, location):
        res = self.predict(self.path2base64(location))
        if res:
            return self.count_res(res, {}, {})
        else:
            return [{},{}]

    def count_res(self, data: list[dict], counts: dict[str, int], others:dict[str, int]) -> list[dict[str, int]]:
        for item in data:
            score = item.get("score")
            tName = item.get("name")
            if tName in self.config.name_sheet.keys():
                tName = self.config.name_sheet.get(tName)
            if score >= self.config.score and tName not in self.config.exclude:
                counts[tName] = counts.get(tName, 0) + 1
            else:
                group_score = item.get("group_score")
                if group_score > self.config.group_score:
                    others[tName] = others.get(tName, 0) + 1
        return [counts,others]


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


if __name__ == '__main__':
    s = Script(r"D:\dddd\hwxj 测试数据", "D:\dddd\结果")
    # res = s.predict(s.path2base64(r"D:\1.jpg"))
    s.run("aa")
    # s.predict_video(r"D:\dddd\hwxj 测试数据\2021南雄2\1001\IMAG0088.AVI")

