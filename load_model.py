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

class MainApp(QMainWindow):
    def __init__(self, gesture_recognizer):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化 Mediapipe 和 OpenCV
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 加载手势识别任务模型
        # 接收加载好的手势识别模型
        self.gesture_recognizer = gesture_recognizer

        # 定时器，用于更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 连接按钮的点击事件
        self.ui.open_camera_btn.clicked.connect(self.open_camera)
        self.ui.close_camera_btn.clicked.connect(self.close_camera)

    def load_gesture_recognizer(self, model_path):
        """
        加载手势识别任务模型
        """
        print(model_path)
        base_options = python.BaseOptions(model_asset_path=model_path)
        print('############')
        options = vision.GestureRecognizerOptions(base_options=base_options)
        print('############')
        print(f"当前工作目录: {os.getcwd()}")
        return GestureRecognizer.create_from_options(options)

    def open_camera(self):
        """打开摄像头"""
        self.cap = cv2.VideoCapture(0)  # 打开默认摄像头
        if not self.cap.isOpened():
            print("Error: 无法访问摄像头。")
            return
        self.timer.start(30)  # 每 30 毫秒更新一次

    def close_camera(self):
        """关闭摄像头"""
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.ui.original_video_label.setText("等待摄像头开启")
        self.ui.processed_video_label.setText("等待手势识别")

    def update_frame(self):
        """更新视频帧"""
        if not self.cap or not self.cap.isOpened():
            print("Error: 摄像头未打开。")
            return

        ret, frame = self.cap.read()
        if not ret:
            print("Error: 无法读取摄像头帧。")
            return

        # 将帧转换为 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture = "未检测到手势"  # 默认手势文本

        # 如果检测到手部关键点
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # 绘制手部关键点
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)
                #print('############已绘制手部关键点')
                # 调用手势识别逻辑
                if self.gesture_recognizer:
                    gesture = self.recognize_gesture(rgb_frame)
                    print(f"识别到的手势: ")

        # 将帧转换为 QImage 格式以显示
        original_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        processed_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)

        # 更新 QLabel 显示
        self.ui.original_video_label.setPixmap(QPixmap.fromImage(original_image).scaled(
            self.ui.original_video_label.width(), self.ui.original_video_label.height()))
        self.ui.processed_video_label.setPixmap(QPixmap.fromImage(processed_image).scaled(
            self.ui.processed_video_label.width(), self.ui.processed_video_label.height()))

        # 在状态栏显示识别到的手势
        self.ui.statusbar.showMessage(f"识别到的手势: {gesture}")

    def recognize_gesture(self, frame):
        """
        使用手势识别任务模型识别手势
        """
        try:
            # 将 OpenCV 图像转换为 Mediapipe Image
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)

            # 使用手势识别模型进行预测
            recognition_result = self.gesture_recognizer.recognize(mp_image)

            # 获取识别结果
            if recognition_result.gestures:
                print('############')
                top_gesture = recognition_result.gestures[0][0]  # 获取置信度最高的手势
                return top_gesture.category_name  # 返回手势类别名称
            else:
                return "未知手势"
        except Exception as e:
            print(f"Error: 手势识别失败 - {e}")
            return "识别错误"

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.close_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    # 加载手势识别模型
    gesture_recognizer = load_gesture_recognizer()

    app = QApplication(sys.argv)
    main_window = MainApp(gesture_recognizer)
    main_window.show()
    sys.exit(app.exec_())