# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        # 原始视频显示区域
        self.original_video_label = QtWidgets.QLabel(self.centralwidget)
        self.original_video_label.setGeometry(QtCore.QRect(10, 10, 380, 280))
        self.original_video_label.setObjectName("original_video_label")
        self.original_video_label.setStyleSheet("background-color: black;")
        self.original_video_label.setAlignment(QtCore.Qt.AlignCenter)

        # 处理后视频显示区域
        self.processed_video_label = QtWidgets.QLabel(self.centralwidget)
        self.processed_video_label.setGeometry(QtCore.QRect(400, 10, 380, 280))
        self.processed_video_label.setObjectName("processed_video_label")
        self.processed_video_label.setStyleSheet("background-color: black;")
        self.processed_video_label.setAlignment(QtCore.Qt.AlignCenter)

        # 打开摄像头按钮
        self.open_camera_btn = QtWidgets.QPushButton(self.centralwidget)
        self.open_camera_btn.setGeometry(QtCore.QRect(10, 310, 120, 40))
        self.open_camera_btn.setObjectName("open_camera_btn")

        # 关闭摄像头按钮
        self.close_camera_btn = QtWidgets.QPushButton(self.centralwidget)
        self.close_camera_btn.setGeometry(QtCore.QRect(140, 310, 120, 40))
        self.close_camera_btn.setObjectName("close_camera_btn")

        MainWindow.setCentralWidget(self.centralwidget)

        # 状态栏
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "手势识别"))
        self.original_video_label.setText(_translate("MainWindow", "原始视频"))
        self.processed_video_label.setText(_translate("MainWindow", "处理后视频"))
        self.open_camera_btn.setText(_translate("MainWindow", "打开摄像头"))
        self.close_camera_btn.setText(_translate("MainWindow", "关闭摄像头"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())