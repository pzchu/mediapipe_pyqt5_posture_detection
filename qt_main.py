import sys
import cv2
import mediapipe as mp
import numpy as np
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from camera import Ui_MainWindow  # 导入UI类
from PIL import Image, ImageDraw, ImageFont
import os
from PyQt5 import QtGui, QtCore, QtWidgets

class VideoThread(QThread):
    original_frame_signal = pyqtSignal(np.ndarray)
    processed_frame_signal = pyqtSignal(np.ndarray)
    
    def __init__(self):
        super().__init__()
        self.running = False
        
        # 初始化MediaPipe手部检测
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
    
    def run(self):
        # 打开摄像头
        cap = cv2.VideoCapture(0)
        
        while self.running:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 转换为RGB格式（MediaPipe需要RGB格式）
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # 处理帧以检测手部
            results = self.hands.process(rgb_frame)
            
            # 创建处理后的帧（复制原始帧）
            processed_frame = rgb_frame.copy()
            
            # 如果检测到手部，绘制手部标记
            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    # 在处理后的帧上绘制手部标记
                    self.mp_drawing.draw_landmarks(
                        processed_frame,
                        hand_landmarks,
                        self.mp_hands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()
                    )
                    
                    # 识别手势（这里可以添加更复杂的手势识别逻辑）
                    self.recognize_gesture(processed_frame, hand_landmarks)
            
            # 发送信号更新UI
            self.original_frame_signal.emit(rgb_frame)
            self.processed_frame_signal.emit(processed_frame)
        
        # 释放摄像头
        cap.release()
    
    def recognize_gesture(self, frame, landmarks):
        """简单的手势识别逻辑，可以根据需要扩展"""
        # 获取手指关键点
        thumb_tip = landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
        index_tip = landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
        middle_tip = landmarks.landmark[self.mp_hands.HandLandmark.MIDDLE_FINGER_TIP]
        ring_tip = landmarks.landmark[self.mp_hands.HandLandmark.RING_FINGER_TIP]
        pinky_tip = landmarks.landmark[self.mp_hands.HandLandmark.PINKY_TIP]
        
        # 获取手腕位置作为参考点
        wrist = landmarks.landmark[self.mp_hands.HandLandmark.WRIST]
        
        # 计算手指是否伸展（简化版）
        h, w, _ = frame.shape
        fingers_extended = []
        
        # 检查拇指是否伸展（水平方向）
        if thumb_tip.x < wrist.x:  # 左手
            fingers_extended.append(thumb_tip.x < landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].x)
        else:  # 右手
            fingers_extended.append(thumb_tip.x > landmarks.landmark[self.mp_hands.HandLandmark.THUMB_IP].x)
        
        # 检查其他手指是否伸展（垂直方向）
        for finger_tip, finger_pip in [
            (index_tip, self.mp_hands.HandLandmark.INDEX_FINGER_PIP),
            (middle_tip, self.mp_hands.HandLandmark.MIDDLE_FINGER_PIP),
            (ring_tip, self.mp_hands.HandLandmark.RING_FINGER_PIP),
            (pinky_tip, self.mp_hands.HandLandmark.PINKY_PIP)
        ]:
            fingers_extended.append(finger_tip.y < landmarks.landmark[finger_pip].y)
        
        # 识别手势
        gesture = "Unknown"
        if all(fingers_extended):
            gesture = "Open Hand"
        elif not any(fingers_extended):
            gesture = "Fist"
        elif fingers_extended[1] and not any(fingers_extended[0:1] + fingers_extended[2:]):
            gesture = "Index Finger"
        elif fingers_extended[1] and fingers_extended[2] and not any(fingers_extended[0:1] + fingers_extended[3:]):
            gesture = "Victory"
        
        
        cv2.putText(
            frame, 
            f"Gesture: {gesture}", 
            (int(wrist.x * w), int(wrist.y * h - 20)), 
            cv2.FONT_HERSHEY_SIMPLEX, 
            0.8, 
            (255, 0, 0), 
            2
        )
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()
class GestureRecognitionUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

class GestureRecognitionApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.ui = GestureRecognitionUI()
        self.video_thread = VideoThread()
        
        # 连接信号和槽
        self.ui.ui.open_camera_btn.clicked.connect(self.start_camera)
        self.ui.ui.close_camera_btn.clicked.connect(self.stop_camera)
        self.video_thread.original_frame_signal.connect(self.ui.update_original_frame)
        self.video_thread.processed_frame_signal.connect(self.ui.update_processed_frame)
    def update_original_frame(self, frame):
        """更新原始视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(convert_to_qt_format)
        self.ui.ui.original_video_label.setPixmap(pixmap)
    
    def update_processed_frame(self, frame):
        """更新处理后的视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(convert_to_qt_format)
        self.ui.ui.processed_video_label.setPixmap(pixmap)
    def start_camera(self):
        """开始摄像头捕获"""
        self.video_thread.running = True
        self.video_thread.start()
        self.ui.ui.open_camera_btn.setEnabled(False)
        self.ui.ui.close_camera_btn.setEnabled(True)
    
    # def stop_camera(self):
    #     """停止摄像头捕获"""
    #     self.video_thread.stop()
    #     self.ui.ui.open_camera_btn.setEnabled(True)
    #     self.ui.ui.close_camera_btn.setEnabled(False)
    #     # 重置视频标签
    #     self.ui.ui.original_video_label.clear()
    #     self.ui.ui.processed_video_label.clear()
    #     self.ui.ui.original_video_label.setText('等待摄像头开启...')
    #     self.ui.ui.processed_video_label.setText('等待手势识别...')

    def stop_camera(self):
    
        self.video_thread.stop()
        self.ui.ui.open_camera_btn.setEnabled(True)
        self.ui.ui.close_camera_btn.setEnabled(False)
        
        # 创建空白图像替代视频帧
        blank_image = np.zeros((450, 570, 3), dtype=np.uint8)
        blank_image.fill(240)  # 填充浅灰色背景
        
        # 在空白图像上添加文字
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(blank_image, "Waiting for camera...", (150, 225), font, 0.8, (0, 0, 0), 2)
        
        # 将空白图像设置到标签上
        h, w, ch = blank_image.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(blank_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(convert_to_qt_format)
        
        self.ui.ui.original_video_label.setPixmap(pixmap)
        
        # 为第二个标签也创建空白图像
        blank_image2 = np.zeros((450, 570, 3), dtype=np.uint8)
        blank_image2.fill(240)
        cv2.putText(blank_image2, "Waiting for gesture recognition...", (100, 225), font, 0.7, (0, 0, 0), 2)
        
        convert_to_qt_format2 = QtGui.QImage(blank_image2.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap2 = QtGui.QPixmap.fromImage(convert_to_qt_format2)
        
        self.ui.ui.processed_video_label.setPixmap(pixmap2)
    
    def run(self):
        """运行应用程序"""
        self.ui.show()
        return self.app.exec_()

if __name__ == "__main__":
    app = GestureRecognitionApp()
    sys.exit(app.run())