# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1200, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        
        # 打开摄像头按钮
        self.open_camera_btn = QtWidgets.QPushButton(self.centralwidget)
        self.open_camera_btn.setGeometry(QtCore.QRect(20, 20, 150, 40))
        self.open_camera_btn.setObjectName("open_camera_btn")
        
        # 关闭摄像头按钮
        self.close_camera_btn = QtWidgets.QPushButton(self.centralwidget)
        self.close_camera_btn.setGeometry(QtCore.QRect(190, 20, 150, 40))
        self.close_camera_btn.setEnabled(False)
        self.close_camera_btn.setObjectName("close_camera_btn")
        
        # 原始视频显示标签
        self.original_video_label = QtWidgets.QLabel(self.centralwidget)
        self.original_video_label.setGeometry(QtCore.QRect(20, 80, 570, 450))
        self.original_video_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        self.original_video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.original_video_label.setObjectName("original_video_label")
        
        # 处理后视频显示标签
        self.processed_video_label = QtWidgets.QLabel(self.centralwidget)
        self.processed_video_label.setGeometry(QtCore.QRect(610, 80, 570, 450))
        self.processed_video_label.setStyleSheet("border: 2px solid #cccccc; background-color: #f0f0f0;")
        self.processed_video_label.setAlignment(QtCore.Qt.AlignCenter)
        self.processed_video_label.setObjectName("processed_video_label")
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1200, 26))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "手势识别系统"))
        self.open_camera_btn.setText(_translate("MainWindow", "打开摄像头"))
        self.close_camera_btn.setText(_translate("MainWindow", "关闭摄像头"))
        self.original_video_label.setText(_translate("MainWindow", "等待摄像头开启..."))
        self.processed_video_label.setText(_translate("MainWindow", "等待手势识别..."))


# 添加更新视频帧的方法
class GestureRecognitionUI(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
    
    def update_original_frame(self, frame):
        """更新原始视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(convert_to_qt_format)
        scaled_pixmap = pixmap.scaled(self.ui.original_video_label.width(), 
                                      self.ui.original_video_label.height(), 
                                      QtCore.Qt.KeepAspectRatio)
        self.ui.original_video_label.setPixmap(scaled_pixmap)
    
    def update_processed_frame(self, frame):
        """更新处理后的视频帧"""
        h, w, ch = frame.shape
        bytes_per_line = ch * w
        convert_to_qt_format = QtGui.QImage(frame.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(convert_to_qt_format)
        scaled_pixmap = pixmap.scaled(self.ui.processed_video_label.width(), 
                                      self.ui.processed_video_label.height(), 
                                      QtCore.Qt.KeepAspectRatio)
        self.ui.processed_video_label.setPixmap(scaled_pixmap)


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    ui = GestureRecognitionUI()
    ui.show()
    sys.exit(app.exec_())