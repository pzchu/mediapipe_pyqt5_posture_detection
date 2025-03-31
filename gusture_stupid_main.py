# # -*- coding: utf-8 -*-

# import sys
# import cv2
# import mediapipe as mp
# from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from camera import Ui_MainWindow


# class MainApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)

#         # Mediapipe and OpenCV initialization
#         self.cap = None
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#         self.mp_drawing = mp.solutions.drawing_utils

#         # Timer for updating frames
#         self.timer = QTimer()
#         self.timer.timeout.connect(self.update_frame)

#         # Connect buttons to their respective functions
#         self.ui.open_camera_btn.clicked.connect(self.open_camera)
#         self.ui.close_camera_btn.clicked.connect(self.close_camera)

#     def open_camera(self):
#         self.cap = cv2.VideoCapture(0)  # Open the default camera
#         if not self.cap.isOpened():
#             print("Error: Unable to access the camera.")
#             return
#         self.timer.start(30)  # Update every 30ms

#     def close_camera(self):
#         self.timer.stop()
#         if self.cap:
#             self.cap.release()
#         self.ui.original_video_label.setText("等待摄像头开启")
#         self.ui.processed_video_label.setText("等待手势识别")

#     def update_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             print("Error: Unable to read frame from the camera.")
#             return

#         # Process the frame for Mediapipe
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.hands.process(rgb_frame)

#         # Draw hand landmarks on the frame
#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

#         # Convert frames to display in PyQt5
#         original_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
#         processed_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)

#         # Update the labels
#         self.ui.original_video_label.setPixmap(QPixmap.fromImage(original_image).scaled(
#             self.ui.original_video_label.width(), self.ui.original_video_label.height()))
#         self.ui.processed_video_label.setPixmap(QPixmap.fromImage(processed_image).scaled(
#             self.ui.processed_video_label.width(), self.ui.processed_video_label.height()))

#     def closeEvent(self, event):
#         self.close_camera()
#         super().closeEvent(event)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainApp()
#     main_window.show()
#     sys.exit(app.exec_())


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

        # 初始化 Mediapipe 和 OpenCV
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # 定时器，用于更新视频帧
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # 连接按钮的点击事件
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
        """更新视频帧"""
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

                # 调用手势识别逻辑
                gesture = self.recognize_gesture(hand_landmarks)

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

    def recognize_gesture(self, hand_landmarks):
        """
        根据 Mediapipe 手部关键点识别手势
        """
        # 获取关键点位置
        landmarks = hand_landmarks.landmark

        # 计算关键点之间的距离，用于手势识别
        thumb_tip = landmarks[4]  # 拇指尖
        index_tip = landmarks[8]  # 食指尖
        middle_tip = landmarks[12]  # 中指尖
        ring_tip = landmarks[16]  # 无名指尖
        pinky_tip = landmarks[20]  # 小指尖
        wrist = landmarks[0]  # 手腕

        # 手势识别逻辑
        if (
            thumb_tip.y < index_tip.y < middle_tip.y < ring_tip.y < pinky_tip.y
            and abs(thumb_tip.x - pinky_tip.x) > 0.3
        ):
            return "张开手掌"  # Open hand
        elif (
            thumb_tip.y > index_tip.y
            and middle_tip.y > index_tip.y
            and ring_tip.y > index_tip.y
            and pinky_tip.y > index_tip.y
        ):
            return "握拳"  # Fist
        elif (
            abs(thumb_tip.x - index_tip.x) < 0.05
            and abs(thumb_tip.y - index_tip.y) < 0.05
            and middle_tip.y > index_tip.y
        ):
            return "OK手势"  # OK gesture
        else:
            return "未知手势"  # Unknown gesture
        
    def clear_video_labels(self):
        """清除视频显示区域"""
        self.ui.original_video_label.clear()
        self.ui.original_video_label.setText("摄像头已关闭")
        self.ui.processed_video_label.clear()
        self.ui.processed_video_label.setText("摄像头已关闭")

    def closeEvent(self, event):
        """关闭窗口事件"""
        self.close_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())