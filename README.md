# lmDemo-python-pyqt6
公司叫开发的一个小工具，用pyqt6做简单得界面（输入框、文件选择、进度条等），执行后对目录内所有指定后缀名的图片进行识别然后分类放到对应文件夹，并生成excel表记录结果。todo（由于没有要求所以没有对图片进行打框,其实也很简单opencv，或者pil绘制一下即可）

直接执行main.py文件即可
文件架构如下->

Common.py -> 公共常量类，以及读取json配置的代码
config.json -> 程序运行后会生成的配置表，用于修改常量
Excel.py -> 操作excel表的具体代码
Exif.py -> 读取图片exif信息
main.py -> 主要程序启动
MyThread.py -> 自定义线程类
script.py -> 主要代码，包括识别接口调用，文件保存等
ui.py -> pyqt6的ui代码
