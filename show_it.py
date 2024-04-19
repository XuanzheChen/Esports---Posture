import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import QTimer
import cv2
import matplotlib.pyplot as plt
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QGraphicsView, QGraphicsScene
from PyQt5.QtCore import QTimer
import cv2
import subprocess
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas


class VideoPlayerApp(QWidget):
    def __init__(self, video_source1='video_input/video1.mp4', video_source2='output.mp4', text_file='angle2.txt'):
        super().__init__()
        self.video_source1 = video_source1
        self.video_source2 = video_source2
        self.text_file = text_file
        self.numbers = self.load_numbers()
        self.angles = self.load_numbers1()
        self.initUI()
        self.playing = False

    def initUI(self):
        self.setWindowTitle('身体姿态分析界面')
        self.setGeometry(100, 100, 700, 800)  # 设置窗口位置和大小

        self.label1 = QLabel(self)
        self.label1.setGeometry(20, 20, 320, 240)  # 设置第一个视频播放区域的位置和大小

        self.label2 = QLabel(self)
        self.label2.setGeometry(360, 20, 320, 240)  # 设置第二个视频播放区域的位置和大小

        self.btn_play = QPushButton('展示3D模型', self)
        self.btn_play.setGeometry(120, 280, 120, 40)  # 设置播放按钮的位置和大小
        self.btn_play.clicked.connect(self.play_video)  # 连接播放按钮的点击事件到播放方法

        self.btn_pause = QPushButton('暂停', self)
        self.btn_pause.setGeometry(360, 280, 120, 40)  # 设置暂停按钮的位置和大小
        self.btn_pause.clicked.connect(self.pause_video)  # 连接暂停按钮的点击事件到暂停方法

        self.running_label = QLabel("腰椎角度：", self)
        self.running_label.setStyleSheet("color: black; font-size: 20px;")
        self.running_label.move(10, 360)  # 设置位置为 (100, 100)
        self.running_label.hide()  # 初始时隐藏

        self.running_label1 = QLabel("腰椎角度变化图", self)
        self.running_label1.setStyleSheet("color: black; font-size: 30px;")
        self.running_label1.move(240, 390)  # 设置位置为 (100, 100)
        self.running_label1.hide()  # 初始时隐藏

        self.label_time1 = QLabel(self)
        self.label_time1.setGeometry(20, 330, 300, 20)  # 设置第一个视频播放时间显示的位置和大小

        self.label_time2 = QLabel(self)
        self.label_time2.setGeometry(360, 330, 300, 20)  # 设置第二个视频播放时间显示的位置和大小

        self.label_text = QLabel(self)
        self.label_text.setGeometry(110, 360, 760, 20)  # 设置文本显示区域的位置和大小
        # 添加一个定时器，每隔0.2秒更新一次文本
        self.text_timer = QTimer(self)
        self.text_timer.timeout.connect(self.update_text)
        self.text_index = 0  # 用于记录当前显示到的文本索引

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene, self)
        self.view.setGeometry(20, 430, 760, 300)

        self.vid1 = cv2.VideoCapture(self.video_source1)
        self.vid2 = cv2.VideoCapture(self.video_source2)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update)

        self.playing = True

    def play_video(self):
        if not self.playing:
            # 重置视频的读取位置
            self.running_label.show()
            self.running_label1.show()
            self.timer.start(30)
            self.vid1.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.vid2.set(cv2.CAP_PROP_POS_FRAMES, 0)
            self.timer.start(30)
            self.playing = True

            self.restart_text_display()
            self.draw_graph()

    def pause_video(self):
        if self.playing:
            self.timer.stop()
            self.playing = False
            self.text_timer.stop()  # 停止文本显示定时器

    def stop_video(self):
        self.timer.stop()
        self.vid1.release()
        self.vid2.release()
        self.label1.clear()
        self.label2.clear()

    def draw_graph(self):
        self.scene.clear()

        figure = plt.figure()
        ax = figure.add_subplot(111)
        ax.plot(self.angles)
        ax.set_xlabel('Frame')
        ax.set_ylabel('Angle')
        ax.set_title('Angle over Frames')
        ax.grid(True)

        canvas = FigureCanvas(figure)
        canvas.draw()
        canvas.setFixedSize(600, 300)  # 设置 FigureCanvas 的固定大小为 600x300 像素
        self.scene.addWidget(canvas)

    def update(self):
        ret1, frame1 = self.vid1.read()
        ret2, frame2 = self.vid2.read()
        if ret1 and ret2:
            # Convert frames from BGR to RGB
            frame1_rgb = cv2.cvtColor(frame1, cv2.COLOR_BGR2RGB)
            frame2_rgb = cv2.cvtColor(frame2, cv2.COLOR_BGR2RGB)

            # Convert frames to QPixmap
            pixmap1 = QPixmap.fromImage(
                QImage(frame1_rgb, frame1_rgb.shape[1], frame1_rgb.shape[0], QImage.Format_RGB888))
            pixmap2 = QPixmap.fromImage(
                QImage(frame2_rgb, frame2_rgb.shape[1], frame2_rgb.shape[0], QImage.Format_RGB888))

            # Set QPixmap to QLabel
            self.label1.setPixmap(pixmap1.scaled(320, 240))
            self.label2.setPixmap(pixmap2.scaled(320, 240))

            # 获取当前视频的帧数和帧率
            frame_count1 = int(self.vid1.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_rate1 = int(self.vid1.get(cv2.CAP_PROP_FPS))
            frame_count2 = int(self.vid2.get(cv2.CAP_PROP_FRAME_COUNT))
            frame_rate2 = int(self.vid2.get(cv2.CAP_PROP_FPS))

            # 计算当前播放时间
            current_frame1 = int(self.vid1.get(cv2.CAP_PROP_POS_FRAMES))
            current_time1 = current_frame1 / frame_rate1
            current_frame2 = int(self.vid2.get(cv2.CAP_PROP_POS_FRAMES))
            current_time2 = current_frame2 / frame_rate2

            # 显示当前播放时间和视频总时长
            self.label_time1.setText(f"视频1: {current_time1:.2f} / {frame_count1 / frame_rate1:.2f} s")
            self.label_time2.setText(f"视频2: {current_time2:.2f} / {frame_count2 / frame_rate2:.2f} s")

    def load_numbers(self):
        # 从文本文件中加载数值列表
        with open(self.text_file, 'r') as file:
            numbers = [line.strip() for line in file if line.strip()]
        return numbers

    def load_numbers1(self):
        # 读取.txt文件
        file_path = self.text_file
        with open(file_path, 'r') as file:
            data = file.readlines()

        # 处理数据
        angles = []
        for line in data:
            angle = float(line.strip())
            angles.append(angle)

        return angles

    def update_text(self):
        # 更新文本显示
        if self.text_index < len(self.numbers):
            self.label_text.setText(self.numbers[self.text_index])
            self.text_index += 1
        else:
            # 如果已经显示完所有文本，则停止定时器
            self.text_timer.stop()

    def restart_text_display(self):
        # 重新开始文本显示
        self.text_timer.stop()  # 先停止文本显示定时器
        self.text_index = 0
        self.text_timer.start(2.83 / 83 * 1000)  # 重新开始文本显示定时器，每隔0.2秒更新一次文本

    def run_function(self):
        # 运行另一个 Python 文件
        args = ["python", "path_to_your_script.py", "arg1", "arg2", "arg3"]
        subprocess.run(args)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    player = VideoPlayerApp()
    player.show()
    sys.exit(app.exec_())
