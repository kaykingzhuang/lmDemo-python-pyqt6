import exifread


class Exif:

    @staticmethod
    def read(img) -> dict:
        # 打开图片文件
        fields = {
            "Image Make": "",
            "Image Model": "",
            "Image DateTime": ""
        }
        with open(img, 'rb') as file:
            # 读取图片的EXIF信息
            tags = exifread.process_file(file)

            for key in fields.keys():
                try:
                    value = tags.get(key).values
                except Exception as e:
                    value = ""
                fields[key] = value
        return fields

