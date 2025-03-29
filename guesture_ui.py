import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QImage, QPixmap

class GestureRecognitionUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):
        # 设置窗口标题和大小
        self.setWindowTitle('手势识别系统')
        self.setGeometry(100, 100, 1200, 600)
        
        # 创建主窗口部件和布局
        main_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # 创建按钮布局
        button_layout = QHBoxLayout()
        
        # 创建打开摄像头按钮
        self.open_camera_btn = QPushButton('打开摄像头')
        self.open_camera_btn.setFixedSize(150, 40)
        
        # 创建关闭摄像头按钮
        self.close_camera_btn = QPushButton('关闭摄像头')
        self.close_camera_btn.setFixedSize(150, 40)
        self.close_camera_btn.setEnabled(False)  # 初始状态下禁用
        
        # 添加按钮到布局
        button_layout.addWidget(self.open_camera_btn)
        button_layout.addWidget(self.close_camera_btn)
        button_layout.addStretch()
        
        # 创建视频显示布局
        video_layout = QHBoxLayout()
        
        # 创建原始视频显示标签
        self.original_video_label = QLabel('等待摄像头开启...')
        self.original_video_label.setAlignment(Qt.AlignCenter)
        self.original_video_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        self.original_video_label.setMinimumSize(QSize(540, 400))
        
        # 创建处理后视频显示标签
        self.processed_video_label = QLabel('等待手势识别...')
        self.processed_video_label.setAlignment(Qt.AlignCenter)
        self.processed_video_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        self.processed_video_label.setMinimumSize(QSize(540, 400))
        
        # 添加视频标签到布局
        video_layout.addWidget(self.original_video_label)
        video_layout.addWidget(self.processed_video_label)
        
        # 添加所有布局到主布局
        main_layout.addLayout(button_layout)
        main_layout.addLayout(video_layout)
        
        # 设置主窗口布局
        main_widget.setLayout(main_layout)
        self.setCentralWidget(main_widget)
    
    def update_original_frame(self, frame):
        """更新原始视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(convert_to_qt_format)
        self.original_video_label.setPixmap(pixmap)
    
    def update_processed_frame(self, frame):
        """更新处理后的视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QImage(frame.data, w, h, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(convert_to_qt_format)
        self.processed_video_label.setPixmap(pixmap)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ui = GestureRecognitionUI()
    ui.show()
    sys.exit(app.exec_())