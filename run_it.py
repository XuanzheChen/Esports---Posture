import subprocess

from PyQt5.QtWidgets import QWidget, QLabel, QPushButton, QApplication
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import cv2
import os
import sys
from PyQt5.QtCore import Qt


class VideoPlayerApp(QWidget):
    def __init__(self, video_source1='video_input/video1.mp4', target_file='output.mp4'):
        super().__init__()
        self.update_target_file_status_flag = False
        self.video_source1 = video_source1
        self.target_file = target_file

        self.initUI()

        # 创建定时器并连接到自动检查目标文件状态的方法
        self.timer_auto_check = QTimer(self)
        self.timer_auto_check.timeout.connect(self.auto_check_target_file_status)
        # 设置定时器的间隔时间为每隔1000毫秒（1秒）执行一次自动检查
        self.timer_auto_check.start(1000)

    def initUI(self):
        self.setWindowTitle('运行界面')
        self.setGeometry(100, 100, 500, 500)

        self.label = QLabel(self)
        self.label.setGeometry(10, 10, 440, 320)

        self.status_label = QLabel(self)  # 添加用于显示文件状态的标签
        self.status_label.setGeometry(10, 550, 400, 20)

        # 添加黑色遮罩层
        self.cover_label = QLabel(self)
        self.cover_label.setGeometry(0, 0, self.width(), self.height())
        self.cover_label.setStyleSheet("background-color: rgba(0, 0, 0, 0.8);")
        self.cover_label.hide()  # 初始时隐藏

        self.running_label = QLabel("正在运行，不要触碰", self)
        self.running_label.setGeometry(0, 0, self.width(), self.height())
        self.running_label.setStyleSheet("color: white; font-size: 50px;")
        self.running_label.setAlignment(Qt.AlignCenter)
        self.running_label.hide()  # 初始时隐藏

        self.btn_play = QPushButton('显示原视频', self)
        self.btn_play.setGeometry(10, 400, 120, 40)
        self.btn_play.clicked.connect(self.play_video)

        self.btn_pause = QPushButton('暂停', self)
        self.btn_pause.setGeometry(180, 400, 120, 40)
        self.btn_pause.clicked.connect(self.pause_video)

        self.btn_run = QPushButton('开始运行', self)
        self.btn_run.setGeometry(350, 400, 120, 40)
        # 如果需要运行其他功能，可以连接运行按钮的点击事件到相应方法，比如 self.btn_run.clicked.connect(self.run_function)
        self.btn_run.clicked.connect(self.run_function)
        self.update_target_file_status()

    def play_video(self):
        self.cap = cv2.VideoCapture(self.video_source1)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

    def pause_video(self):
        self.timer.stop()

    def stop_video(self):
        self.timer.stop()
        self.cap.release()

    def update_frame(self):
        ret, frame = self.cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0], QImage.Format_RGB888)
            pixmap = QPixmap.fromImage(image)
            self.label.setPixmap(pixmap)
            self.label.setScaledContents(True)

    def update_target_file_status(self):
        if os.path.exists(self.target_file) and not self.update_target_file_status_flag:
            #self.status_label.setText(f" 已完成")
            self.update_target_file_status_flag = True
            self.run_function1()  # 如果目标文件存在，就运行另一个 Python 文件

       # else:
            #self.status_label.setText(f"未完成")

    def auto_check_target_file_status(self):
        self.update_target_file_status()

    def run_function(self):
        # 运行另一个 Python 文件
        # args = ["python", "show_it.py"]
        # # 在运行其他文件前显示黑色覆盖层
        # self.cover_label.show()
        # self.running_label.show()

        self.update_target_file_status_flag = False

        args = ["python", "all_process.py"]
        args1 = ["python", "2.py"]
        args2 = ["python", "4.py"]
        # subprocess.run(args)
        proc1 = subprocess.Popen(args)
        proc1.wait()
        # subprocess.run(args1)
        proc2 = subprocess.Popen(args1)
        proc2.wait()
        print("OK")
        proc3 = subprocess.Popen(args2)
        proc3.wait()
        # subprocess.run(args2)

    def run_function1(self):
        # 运行另一个 Python 文件
        args = ["python", "show_it.py"]
        # args = ["python", "path_to_your_script.py", "arg1", "arg2", "arg3"]
        subprocess.run(args)


if __name__ == "__main__":

    file_path = "output.mp4"
    if os.path.exists(file_path):
        try:
            # 删除文件
            os.remove(file_path)
            print(f"{file_path} 文件删除成功")
        except OSError as e:
            print(f"Error: {file_path} 文件删除失败 - {e.strerror}")

    app = QApplication(sys.argv)
    window = VideoPlayerApp()
    window.show()
    sys.exit(app.exec_())
