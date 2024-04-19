'''
import sys
import numpy as np
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QOpenGLWidget
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QSize
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *

# 设置窗口大小
window_width = 800
window_height = 600

# 定义骨骼姿态数据
specific_3d_skeleton = np.load('3d_pose.npy')
frame_index = 0

human36m_connectivity_dict = [[0, 1], [1, 2], [2, 6], [5, 4], [4, 3], [3, 6], [6, 7],
                              [7, 8], [8, 16], [9, 16],
                              [8, 12], [11, 12], [10, 11], [8, 13], [13, 14], [14, 15]]

class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        start_time = time.time()  # 记录绘制开始时间

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()

        # 设置视口和投影矩阵等
        glViewport(0, 0, self.width(), self.height())
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(-1400, 1400, -1400, 1400, -2000, 2000)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # 设置相机位置和方向
        gluLookAt(0,0 , 150, 1500, -1500, 1500, 0, 0, 1)

        # 绘制骨骼姿态
        draw3Dpose(specific_3d_skeleton[frame_index])

        self.update()

        end_time = time.time()  # 记录绘制结束时间
        elapsed_time = end_time - start_time  # 计算绘制时间
        print("Frame Time:", elapsed_time)  # 打印每帧绘制时间

    def sizeHint(self):
        return QSize(window_width, window_height)

def updateAnimation():
    global frame_index
    frame_index = (frame_index + 1) % specific_3d_skeleton.shape[0]

def draw3Dpose(pose_3d):
    glColor3f(0.0, 0.0, 1.0)  # 设置颜色为蓝色

    # 绘制连接线
    glBegin(GL_LINES)
    for i in human36m_connectivity_dict:
        x1, y1, z1 = pose_3d[i[0]]
        x2, y2, z2 = pose_3d[i[1]]
        glVertex3f(x1, y1, z1)
        glVertex3f(x2, y2, z2)
    glEnd()

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.opengl_widget = OpenGLWidget()

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.opengl_widget)
        self.setCentralWidget(central_widget)

        self.timer = QTimer(self)
        self.timer.setInterval(13)  # 设置定时器间隔，约30帧每秒
        self.timer.timeout.connect(updateAnimation)
        self.timer.timeout.connect(self.opengl_widget.update)

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
    '''
import sys

import time
import json
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QOpenGLWidget, QPushButton
from PyQt5.QtGui import QPainter
from PyQt5.QtCore import QTimer, QSize
import cv2
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import joblib
import numpy as np
import numpy as np
from PIL import Image

# 设置窗口大小
window_width = 800
window_height = 600

offset = np.load('body_creat_bias.npy')
print(len(offset))
specific_3d_skeleton = np.load('bodyfinal.npy')
print(specific_3d_skeleton)
print(len(specific_3d_skeleton))
specific_3d_skeleton *= 2000

# 从json文件中读取数据


frame_index = 0

human36m_connectivity_dict = [[12, 9],
                              [14, 9], [13, 9], [9, 6], [6, 3], [3, 0], [13, 16],
                              [16, 18], [2, 5], [1, 4], [5, 8], [4, 7], [19, 21], [18, 20],
                              [7, 10], [14, 17], [17, 19], [19, 21], [0, 1], [0, 2]
                              ]


# [19,21],[16.18],[13,16],[18.20]
class OpenGLWidget(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animating = False

    def save_frame(self, filename):
        image = self.grabFramebuffer()
        image.save(filename)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

    def paintGL(self):
        if self.animating:
            start_time = time.time()  # 记录绘制开始时间

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glClearColor(1.0, 1.0, 1.0, 1.0)
            glLoadIdentity()

            # 设置视口和投影矩阵等
            glViewport(0, 0, self.width(), self.height())
            glMatrixMode(GL_PROJECTION)
            glLoadIdentity()
            gluPerspective(45, 800 / 600, 50, 30000.0)
            glMatrixMode(GL_MODELVIEW)
            glLoadIdentity()

            # 设置相机位置和方向
            gluLookAt(8000, 3000, 3000, -15000, -2000, -2000, 0, 0, 1)  # 调整相机位置和方向 # 调整相机位置和方向
            # gluLookAt(2000, -6000, 2000, 0, 30000, -5000, 0, 0, 1)

            # 绘制骨骼姿态
            glColor3f(0.0, 1.0, 0.2)

            draw3Dpose(specific_3d_skeleton[frame_index], offset[frame_index], offset[frame_index - 1],
                       offset[frame_index - 2], offset[frame_index - 3], offset[frame_index - 4])

            self.update()

            end_time = time.time()  # 记录绘制结束时间
            elapsed_time = end_time - start_time  # 计算绘制时间
            # print("Time:", elapsed_time)  # 打印每帧绘制时间

    def sizeHint(self):
        return QSize(window_width, window_height)


def updateAnimation(widget):
    global frame_index
    frame_index = (frame_index + 1) % specific_3d_skeleton.shape[0]
    widget.update()


def draw3Dpose(pose_3d, position0, position1, postion2, postion3, postion4):
    glColor3f(0.0, 0.0, 1.0)
    glLineWidth(3)
    # 绘制连接线
    glBegin(GL_LINES)

    for i in human36m_connectivity_dict:
        x1, y1, z1 = pose_3d[i[0]]
        x2, y2, z2 = pose_3d[i[1]]
        x1 = x1 - 500
        x2 = x2 - 500
        y1 = y1 - 800
        y2 = y2 - 800
        z1 = z1 + 3000
        z2 = z2 + 3000
        glVertex3f(x1, z1, -y1)
        glVertex3f(x2, z2, -y2)
    glEnd()

    glFlush()


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.opengl_widget = OpenGLWidget()
        self.start_button = QPushButton("3D POSE")

        central_widget = QWidget()
        layout = QVBoxLayout(central_widget)
        layout.addWidget(self.opengl_widget)
        layout.addWidget(self.start_button)
        self.setCentralWidget(central_widget)
        self.start_button.clicked.connect(self.toggleAnimation)
        self.timer = QTimer(self)
        self.timer.setInterval(60)
        self.timer.timeout.connect(lambda: updateAnimation(self.opengl_widget))

    def showEvent(self, event):
        super().showEvent(event)
        self.timer.start()

    def hideEvent(self, event):
        super().hideEvent(event)
        self.timer.stop()

    def toggleAnimation(self):
        self.opengl_widget.animating = not self.opengl_widget.animating

    def save_video(self, filename, duration=10, fps=30):
        video_writer = cv2.VideoWriter(filename, cv2.VideoWriter_fourcc(*'mp4v'), fps, (window_width, window_height))

        total_frames = int(duration * fps)
        for i in range(total_frames):
            updateAnimation(self.opengl_widget)  # 更新动画
            frame = self.opengl_widget.grabFramebuffer()  # 获取当前帧
            pil_image = Image.fromqpixmap(frame)  # 将QImage转换为PIL图像
            numpy_image = np.array(pil_image)  # 将PIL图像转换为NumPy数组
            frame = cv2.cvtColor(numpy_image, cv2.COLOR_RGBA2BGR)  # 转换为OpenCV格式
            video_writer.write(frame)

        video_writer.release()

        print("Video saved successfully!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.opengl_widget.animating = True
    window.save_video("output.mp4", duration=10, fps=30)
    sys.exit(app.exec_())
