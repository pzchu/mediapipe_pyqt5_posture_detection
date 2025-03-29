# -*- coding: utf-8 -*-

import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from camera import Ui_MainWindow
from mediapipe.tasks.python import vision
from mediapipe.tasks.python.vision import GestureRecognizer

from mediapipe.tasks import python
import os
#os.chdir(r"C:\Users\deep\gitcode\mediapipe_pyqt5_posture_detection")



class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化 Mediapipe 和 OpenCV
        os.chdir('C:/Users/deep/gitcode/mediapipe_pyqt5_posture_detection')
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 加载手势识别任务模型
        try:
            #model_path = os.path.abspath('C:/Users/deep/gitcode/mediapipe_pyqt5_posture_detection/gesture_recognizer (2).task')
            #self.gesture_recognizer = self.load_gesture_recognizer(model_path)
            # 使用相对路径加载模型
            print(f"当前工作目录: {os.getcwd()}")
            print(f"当前工作目录: {os.getcwd()}")
            model_path = "./gesture_recognizer.task"
            base_options = python.BaseOptions(model_asset_path=model_path)
            print(base_options)
            options = vision.GestureRecognizerOptions(base_options=base_options)
            print(f'############')
         
            self.gesture_recognizer = vision.GestureRecognizer.create_from_options(options)
            print('------------')
        except Exception as e:
            print(f"Error: 无法加载手势识别模型 - {e}")
            self.gesture_recognizer = None

        # 定时器，用于更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 连接按钮的点击事件
        self.ui.open_camera_btn.clicked.connect(self.open_camera)
        self.ui.close_camera_btn.clicked.connect(self.close_camera)

def load_gesture_recognizer():
    """
    加载 Mediapipe 手势识别模型
    """
    try:
        # 使用绝对路径加载模型
        model_path = os.path.abspath('./gesture_recognizer.task')
        print(f"加载模型文件路径: {model_path}")

        # 检查文件是否存在
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"模型文件不存在: {model_path}")

        # 加载模型
        base_options = python.BaseOptions(model_asset_path=model_path)
        options = vision.GestureRecognizerOptions(base_options=base_options)
        gesture_recognizer = vision.GestureRecognizer.create_from_options(options)
        print("模型加载成功")
        return gesture_recognizer
    except Exception as e:
        print(f"Error: 无法加载手势识别模型 - {e}")
        return None



if __name__ == "__main__":
     # 加载手势识别模型
    gesture_recognizer = load_gesture_recognizer()

    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())
