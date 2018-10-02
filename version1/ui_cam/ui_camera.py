# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'camera.ui'
#
# Created by: PyQt5 UI code generator 5.11.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Camera(object):
    def setupUi(self, Camera):
        Camera.setObjectName("Camera")
        Camera.resize(870, 560)
        self.centralwidget = QtWidgets.QWidget(Camera)
        self.centralwidget.setObjectName("centralwidget")
        self.captureWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.captureWidget.setGeometry(QtCore.QRect(670, 59, 188, 451))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(1)
        sizePolicy.setHeightForWidth(self.captureWidget.sizePolicy().hasHeightForWidth())
        self.captureWidget.setSizePolicy(sizePolicy)
        self.captureWidget.setObjectName("captureWidget")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(self.tab_2)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 5, 0, 1, 1)
        self.clearButton = QtWidgets.QPushButton(self.tab_2)
        self.clearButton.setObjectName("clearButton")
        self.gridLayout.addWidget(self.clearButton, 8, 0, 1, 1)
        self.absenceNumber = QtWidgets.QLCDNumber(self.tab_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.absenceNumber.sizePolicy().hasHeightForWidth())
        self.absenceNumber.setSizePolicy(sizePolicy)
        self.absenceNumber.setObjectName("absenceNumber")
        self.gridLayout.addWidget(self.absenceNumber, 2, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.tab_2)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 0, 1, 1)
        self.takeImageButton = QtWidgets.QPushButton(self.tab_2)
        self.takeImageButton.setObjectName("takeImageButton")
        self.gridLayout.addWidget(self.takeImageButton, 0, 0, 1, 1)
        self.progressBar = QtWidgets.QProgressBar(self.tab_2)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setObjectName("progressBar")
        self.gridLayout.addWidget(self.progressBar, 9, 0, 1, 1)
        self.lcdNumber_2 = QtWidgets.QLCDNumber(self.tab_2)
        self.lcdNumber_2.setObjectName("lcdNumber_2")
        self.gridLayout.addWidget(self.lcdNumber_2, 4, 0, 1, 1)
        self.SaveButton = QtWidgets.QPushButton(self.tab_2)
        self.SaveButton.setObjectName("SaveButton")
        self.gridLayout.addWidget(self.SaveButton, 1, 0, 1, 1)
        self.dial = QtWidgets.QDial(self.tab_2)
        self.dial.setMaximum(10)
        self.dial.setObjectName("dial")
        self.gridLayout.addWidget(self.dial, 6, 0, 1, 1)
        self.captureWidget.addTab(self.tab_2, "")
        self.trainButton = QtWidgets.QPushButton(self.centralwidget)
        self.trainButton.setGeometry(QtCore.QRect(670, 30, 91, 25))
        self.trainButton.setObjectName("trainButton")
        self.img_label = QtWidgets.QLabel(self.centralwidget)
        self.img_label.setGeometry(QtCore.QRect(10, 30, 640, 480))
        self.img_label.setFrameShape(QtWidgets.QFrame.Box)
        self.img_label.setObjectName("img_label")
        self.startButton = QtWidgets.QPushButton(self.centralwidget)
        self.startButton.setGeometry(QtCore.QRect(770, 30, 89, 25))
        self.startButton.setObjectName("startButton")
        Camera.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(Camera)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 870, 22))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuDevices = QtWidgets.QMenu(self.menubar)
        self.menuDevices.setObjectName("menuDevices")
        Camera.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(Camera)
        self.statusbar.setObjectName("statusbar")
        Camera.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(Camera)
        self.actionExit.setObjectName("actionExit")
        self.actionStartCamera = QtWidgets.QAction(Camera)
        self.actionStartCamera.setObjectName("actionStartCamera")
        self.actionStopCamera = QtWidgets.QAction(Camera)
        self.actionStopCamera.setObjectName("actionStopCamera")
        self.actionSettings = QtWidgets.QAction(Camera)
        self.actionSettings.setObjectName("actionSettings")
        self.actionOpen_File = QtWidgets.QAction(Camera)
        self.actionOpen_File.setObjectName("actionOpen_File")
        self.menuFile.addAction(self.actionStartCamera)
        self.menuFile.addAction(self.actionStopCamera)
        self.menuFile.addAction(self.actionOpen_File)
        self.menuFile.addSeparator()
        self.menuFile.addSeparator()
        self.menuFile.addAction(self.actionExit)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuDevices.menuAction())

        self.retranslateUi(Camera)
        self.captureWidget.setCurrentIndex(0)
        self.actionExit.triggered.connect(Camera.close)
        self.trainButton.clicked.connect(Camera.train)
        self.actionSettings.triggered.connect(Camera.configureCaptureSettings)
        self.actionStartCamera.triggered.connect(Camera.startCamera)
        self.actionStopCamera.triggered.connect(Camera.stopCamera)
        self.actionOpen_File.triggered.connect(Camera.configureOpenExcels)
        self.takeImageButton.clicked.connect(Camera.takeImage)
        QtCore.QMetaObject.connectSlotsByName(Camera)

    def retranslateUi(self, Camera):
        _translate = QtCore.QCoreApplication.translate
        Camera.setWindowTitle(_translate("Camera", "Camera"))
        self.label_2.setText(_translate("Camera", "Absent Threshold"))
        self.clearButton.setText(_translate("Camera", "Clear"))
        self.label.setText(_translate("Camera", "The number of absences"))
        self.takeImageButton.setText(_translate("Camera", "Capture Photo"))
        self.SaveButton.setText(_translate("Camera", "Save"))
        self.captureWidget.setTabText(self.captureWidget.indexOf(self.tab_2), _translate("Camera", "Image"))
        self.trainButton.setText(_translate("Camera", "Train"))
        self.img_label.setText(_translate("Camera", "TextLabel"))
        self.startButton.setText(_translate("Camera", "Start"))
        self.menuFile.setTitle(_translate("Camera", "File"))
        self.menuDevices.setTitle(_translate("Camera", "Devices"))
        self.actionExit.setText(_translate("Camera", "Exit"))
        self.actionStartCamera.setText(_translate("Camera", "Start Camera"))
        self.actionStopCamera.setText(_translate("Camera", "Stop Camera"))
        self.actionSettings.setText(_translate("Camera", "Settings"))
        self.actionOpen_File.setText(_translate("Camera", "Open File"))
