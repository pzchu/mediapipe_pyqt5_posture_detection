# import sys
# import cv2
# import mediapipe as mp
# from PyQt5.QtCore import QTimer
# from PyQt5.QtGui import QImage, QPixmap
# from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene
# from qview import Ui_MainWindow


# class MainApp(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.ui = Ui_MainWindow()
#         self.ui.setupUi(self)

#         # Initialize Mediapipe and OpenCV
#         self.cap = None
#         self.mp_hands = mp.solutions.hands
#         self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
#         self.mp_drawing = mp.solutions.drawing_utils

#         # Initialize scenes for QGraphicsView
#         self.original_scene = QGraphicsScene()
#         self.processed_scene = QGraphicsScene()
#         self.ui.original_video_view.setScene(self.original_scene)
#         self.ui.processed_video_view.setScene(self.processed_scene)

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
#         self.original_scene.clear()
#         self.processed_scene.clear()

#     def update_frame(self):
#         ret, frame = self.cap.read()
#         if not ret:
#             print("Error: Unable to read frame from the camera.")
#             return

#         # Process the frame
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#         results = self.hands.process(rgb_frame)

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

#         # Convert frames to QImage
#         original_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
#         processed_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)

#         # Update QGraphicsView
#         self.original_scene.clear()
#         self.processed_scene.clear()
#         self.original_scene.addPixmap(QPixmap.fromImage(original_image))
#         self.processed_scene.addPixmap(QPixmap.fromImage(processed_image))

#     def closeEvent(self, event):
#         self.close_camera()
#         super().closeEvent(event)


# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     main_window = MainApp()
#     main_window.show()
#     sys.exit(app.exec_())

import sys
import cv2
import mediapipe as mp
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsScene
from qview_ui import Ui_MainWindow


class MainApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Initialize Mediapipe and OpenCV
        self.cap = None
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.mp_drawing = mp.solutions.drawing_utils

        # Initialize scenes for QGraphicsView
        self.original_scene = QGraphicsScene()
        self.processed_scene = QGraphicsScene()
        self.ui.original_video_view.setScene(self.original_scene)
        self.ui.processed_video_view.setScene(self.processed_scene)

        # Timer for updating frames
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)

        # Connect buttons to their respective functions
        self.ui.open_camera_btn.clicked.connect(self.open_camera)
        self.ui.close_camera_btn.clicked.connect(self.close_camera)

    def open_camera(self):
        self.cap = cv2.VideoCapture(0)  # Open the default camera
        if not self.cap.isOpened():
            print("Error: Unable to access the camera.")
            return
        self.timer.start(30)  # Update every 30ms

    def close_camera(self):
        self.timer.stop()
        if self.cap:
            self.cap.release()
        self.original_scene.clear()
        self.processed_scene.clear()

    def update_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            print("Error: Unable to read frame from the camera.")
            return

        # Process the frame
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(rgb_frame)

        gesture = "未检测到手势"  # Default gesture text

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                self.mp_drawing.draw_landmarks(frame, hand_landmarks, self.mp_hands.HAND_CONNECTIONS)

                # Hand gesture recognition logic
                gesture = self.recognize_gesture(hand_landmarks)

        # Convert frames to QImage
        original_image = QImage(frame.data, frame.shape[1], frame.shape[0], QImage.Format_BGR888)
        processed_image = QImage(rgb_frame.data, rgb_frame.shape[1], rgb_frame.shape[0], QImage.Format_RGB888)

        # Update QGraphicsView
        self.original_scene.clear()
        self.processed_scene.clear()
        self.original_scene.addPixmap(QPixmap.fromImage(original_image))
        self.processed_scene.addPixmap(QPixmap.fromImage(processed_image))

        # Display recognized gesture in the status bar
        self.ui.statusbar.showMessage(f"识别到的手势: {gesture}")

    def recognize_gesture(self, hand_landmarks):
        """
        Recognize hand gestures based on Mediapipe hand landmarks.
        """
        # Get landmark positions
        landmarks = hand_landmarks.landmark

        # Calculate distances between key points for gesture recognition
        thumb_tip = landmarks[4]
        index_tip = landmarks[8]
        middle_tip = landmarks[12]
        ring_tip = landmarks[16]
        pinky_tip = landmarks[20]
        wrist = landmarks[0]

        # Example gesture recognition logic
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

    def closeEvent(self, event):
        self.close_camera()
        super().closeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainApp()
    main_window.show()
    sys.exit(app.exec_())