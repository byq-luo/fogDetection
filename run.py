#!/usr/bin/python3
# -*- coding: utf-8 -*-
import sys, os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import cv2
import numpy as np

"""主函数"""
app = QApplication(sys.argv)
app.setApplicationName("雾霾检测")
app.setQuitOnLastWindowClosed(True)

from src import *

if getattr(sys, 'frozen', False):
    rootPath = os.path.dirname(sys.executable)
elif __file__:
    rootPath = os.path.dirname(__file__)  
print("根目录:", rootPath)


class MainWindow(QMainWindow, QWidget):
    """主窗口"""
    def __init__(self):
        super().__init__()  
        self.imgArray = np.array([]) # 存储图像的矩阵
        self.calcDetectResultThreadRunning = 0 # 为1,线程正在运行
        self.ui = mainWindowUi.MainWindowUi()
        self.connectSignalSlot()
        self.ui.showUi()
        
    def connectSignalSlot(self):
        """连接信号与槽"""
        self.ui.openAFrameImageButton.clicked.connect(self.openAFrameImage) 
        self.ui.calcResultButton.clicked.connect(self.startCalcDetectResult) 
        self.ui.openLocalCameraButton.clicked.connect(self.openLocalCamera) 
        self.ui.closeLocalCameraButton.clicked.connect(self.closeLocalCamera) 
        
    def openAFrameImage(self):
        """打开单张图片"""
        fileName, fileType = QFileDialog.getOpenFileName(self, "Open file", "./img", "Image files(*.bmp; *.jpg)")
        if self.ui.imageToShow.load(fileName):
            self.ui.imageToShowLabel.setPixmap(QPixmap.fromImage(self.ui.imageToShow))
        # 原图提取    
        self.imgArray = cv2.imread(fileName)
        
        
    def openVideo(self):
        pass
        
    def openLocalCamera(self):
        """打开本地摄像头"""
        self.localCamera = camera.LocalCamera()
        self.localCamera.refreshLocalCameraImgSignal.connect(self.refreshLocalCameraImg)
        self.localCamera.localCameraTimer.start()
        
    def closeLocalCamera(self):
        """关闭本地摄像头"""
        if not self.localCamera.localCameraTimer.isStoped():
            self.localCamera.localCameraTimer.stop()
        # 销毁本地摄像头对象
        del self.localCamera
        
        
    def refreshLocalCameraImg(self):
        
        while not self.localCamera.imageQueue.empty():
            image = self.localCamera.imageQueue.get()
            self.ui.imageToShowLabel.setPixmap(QPixmap.fromImage(image))
        
        
    def startCalcDetectResult(self): 
        """开始计算检测结果,建立一个新线程"""
        if self.imgArray.size > 0 and (not self.calcDetectResultThreadRunning): # 图像矩阵非空
            self.calcDetectResultThreadRunning = 1
            self.calcDetectResultThread = detector.CalcDetectResultThread(self.imgArray)         
            self.calcDetectResultThread.resultSignal.connect(self.refreshDetectResult)
            self.calcDetectResultThread.start()

        
        
    def refreshDetectResult(self, resultNums, resultClassify):
        """更新检测结果"""

        self.calcDetectResultThreadRunning = 0
        # self.ui.resultNumLineEdit.setText('{:.4f}'.format(resultNums))
        self.ui.resultNumLineEdit.setText(resultNums)
        self.ui.resultTextLineEdit.setText(str(resultClassify))
        
            
  
"""主函数"""
window = MainWindow()
sys.exit(app.exec_())