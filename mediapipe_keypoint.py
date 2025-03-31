# -*- coding: utf-8 -*-

import sys
import cv2
import mediapipe as mp
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from new_ui import Ui_MainWindow

class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化Mediapipe手部模型
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        
        # 视频捕获相关
        self.cap = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 初始化按钮状态
        self.ui.close_camera_btn.setEnabled(False)
        self.ui.open_camera_btn.clicked.connect(self.open_camera)
        self.ui.close_camera_btn.clicked.connect(self.close_camera)

    def open_camera(self):
        """打开摄像头"""
        self.cap = cv2.VideoCapture(0)
        if self.cap.isOpened():
            self.ui.close_camera_btn.setEnabled(True)
            self.ui.open_camera_btn.setEnabled(False)
            self.timer.start(30)
        else:
            print("Error: 无法访问摄像头")

    def close_camera(self):
        """关闭摄像头"""
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.ui.open_camera_btn.setEnabled(True)
        self.ui.close_camera_btn.setEnabled(False)
        self.clear_video_labels()

    def update_frame(self):
        """更新并处理视频帧"""
        ret, frame = self.cap.read()
        if not ret:
            return

        # 创建原始帧的副本用于显示
        #original_frame = frame.copy()
        #original_frame = frame

        # 显示原视频帧到左侧
        self.display_frame(frame, self.ui.original_video_label)

        # 手部关键点检测
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        # 绘制关键点
        if results.multi_hand_landmarks:
            for landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(
                    frame,
                    landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing.DrawingSpec(color=(0,255,0), thickness=2, circle_radius=2),
                    self.mp_drawing.DrawingSpec(color=(255,0,0), thickness=2)
                )

        # 显示处理后的视频帧到右侧
        self.display_frame(frame, self.ui.processed_video_label)

    def display_frame(self, frame, target_label):
        """显示视频帧到指定的标签"""
        if frame is None or target_label is None:
            return  # 确保 frame 和 target_label 有效

        h, w, ch = frame.shape
        bytes_per_line = ch * w
        qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(qt_image).scaled(
            target_label.size(), aspectRatioMode=1  # 保持宽高比
        )
        target_label.setPixmap(pixmap)

    def clear_video_labels(self):
        """清除视频显示区域"""
        self.ui.original_video_label.clear()
        self.ui.original_video_label.setText("摄像头已关闭")
        self.ui.processed_video_label.clear()
        self.ui.processed_video_label.setText("摄像头已关闭")

    def closeEvent(self, event):
        self.close_camera()
        super().closeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())