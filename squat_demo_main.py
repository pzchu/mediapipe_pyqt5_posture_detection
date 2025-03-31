# -*- coding: utf-8 -*-

import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow
from new_ui import Ui_MainWindow


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # 初始化 Mediapipe 和 OpenCV
        self.cap = cv2.VideoCapture(0)  # 打开摄像头
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 游戏状态
        self.game_started = False
        self.reps = 0  # 记录动作次数

        # 定时器，用于更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)  # 每 30 毫秒更新一次

    def update_frame(self):
        """更新视频帧"""
        ret, frame = self.cap.read()
        if not ret:
            print("Error: 无法读取摄像头帧。")
            return

        # 将帧转换为 RGB 格式
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb_frame)

        # 如果检测到骨骼点
        if results.pose_landmarks:
            # 绘制骨骼点
            self.mp_drawing.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)

            # 游戏逻辑：检测深蹲动作
            self.detect_squat(results.pose_landmarks)

        # 将帧转换为 QImage 格式以显示
        original_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        processed_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)

        # 更新 QLabel 显示
        self.ui.original_video_label.setPixmap(QPixmap.fromImage(original_image).scaled(
            self.ui.original_video_label.width(), self.ui.original_video_label.height()))
        self.ui.processed_video_label.setPixmap(QPixmap.fromImage(processed_image).scaled(
            self.ui.processed_video_label.width(), self.ui.processed_video_label.height()))

        # 在状态栏显示游戏状态
        self.ui.statusbar.showMessage(f"深蹲次数: {self.reps}")

    def detect_squat(self, landmarks):
        """检测深蹲动作"""
        # 获取关键点
        left_hip = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_HIP]
        left_knee = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_KNEE]
        left_ankle = landmarks.landmark[self.mp_pose.PoseLandmark.LEFT_ANKLE]

        # 计算膝盖角度
        angle = self.calculate_angle(left_hip, left_knee, left_ankle)

        # 判断深蹲动作
        if angle < 90 and not self.game_started:
            self.game_started = True
        elif angle > 160 and self.game_started:
            self.game_started = False
            self.reps += 1  # 增加深蹲次数

    @staticmethod
    def calculate_angle(a, b, c):
        """计算三个点之间的角度"""
        a = np.array([a.x, a.y])  # 第一个点
        b = np.array([b.x, b.y])  # 第二个点（角度的顶点）
        c = np.array([c.x, c.y])  # 第三个点

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)
        return np.degrees(angle)

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.cap.release()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())