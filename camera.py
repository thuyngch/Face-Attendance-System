
##
#############################################################################
from PyQt5.QtCore import QByteArray, qFuzzyCompare, Qt, QTimer
from PyQt5.QtWidgets import QApplication, QLCDNumber
from PyQt5.QtGui import QPalette, QPixmap
from PyQt5.QtMultimedia import (QAudioEncoderSettings, QCamera,QCameraImageCapture, QImageEncoderSettings, QMediaMetaData,
        QMediaRecorder, QMultimedia, QVideoEncoderSettings)
from PyQt5.QtWidgets import (QAction, QActionGroup, QApplication, QDialog,QMainWindow, QMessageBox)
from ui_camera import Ui_Camera
# from ui_imagesettings import Ui_ImageSettingsUi
from PyQt5.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtGui import QImage
from AttendanceChecking import AttendanceChecking
from PyQt5 import QtCore, QtGui , QtWidgets
from cv2 import *
from PIL import Image
from scipy.io import savemat
from matplotlib import pyplot as plt
from algorithm_wrapper import AlgorithmAPIs
import os
import numpy as np
import sys
import sqlite3
import cv2

from apis.motion_blur import detect_blur
from apis.landmark import find_bbox, draw_bbox, check_front_view
from apis.recognition import Recognizer


try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtWidgets.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtWidgets.QApplication.translate(context, text, disambig)

def db():
    with sqlite3.connect('.TempExcels.db') as db:
        c = db.cursor()
    c.execute('create table if not exists Temp(name TEXT NOT NULL, gender TEXT NOT NULL,absent INT NOT NULL)')
    db.commit()
    c.close()
    db.close()





def get_total(filepath,mssv):
    file1 = AttendanceChecking(filepath)
    absent=file1.get_total_absence(mssv)
    # failcase=file1.start_checking([mssv])
    Camera.display_absences(camera,absent)


class OpenExcels(QWidget):
 
    def __init__(self):
        super().__init__()
        self.title = 'Open Excel Files'
        self.left = 10
        self.top = 10
        self.width = 640
        self.height = 480
  
 
    def initUI(self):
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
 
        self.openFileNameDialog()
 
        self.show()
 
    def openFileNameDialog(self):    
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"Open Excels", "","All Files (*);;Excel Workbook (*.xlsx);;Excel 97-2003 Workbook (*.xls);;XML Data (*.xml);;CSV file (*.csv)", options=options)
        if fileName:
            print(fileName)
            file_path = os.path.join(fileName)
            get_total(file_path, 1512872)
            # new_path = '../data/new.xlsx'


class ImageSettings(QDialog):

    def __init__(self, imageCapture, parent=None):
        super(ImageSettings, self).__init__(parent)

        self.ui = Ui_ImageSettingsUi()
        self.imagecapture = imageCapture

        self.ui.setupUi(self)

        self.ui.imageCodecBox.addItem("Default image format", "")
        for codecName in self.imagecapture.supportedImageCodecs():
            description = self.imagecapture.imageCodecDescription(codecName)
            self.ui.imageCodecBox.addItem(codecName + ": " + description,
                    codecName)

        self.ui.imageQualitySlider.setRange(0, QMultimedia.VeryHighQuality)

        self.ui.imageResolutionBox.addItem("Default resolution")
        supportedResolutions, _ = self.imagecapture.supportedResolutions()
        for resolution in supportedResolutions:
            self.ui.imageResolutionBox.addItem(
                    "%dx%d" % (resolution.width(), resolution.height()),
                    resolution)

    def imageSettings(self):
        settings = self.imagecapture.encodingSettings()
        settings.setCodec(self.boxValue(self.ui.imageCodecBox))
        settings.setQuality(
                QMultimedia.EncodingQuality(
                        self.ui.imageQualitySlider.value()))
        settings.setResolution(self.boxValue(self.ui.imageResolutionBox))

        return settings

    def setImageSettings(self, settings):
        self.selectComboBoxItem(self.ui.imageCodecBox, settings.codec())
        self.selectComboBoxItem(self.ui.imageResolutionBox,
                settings.resolution())
        self.ui.imageQualitySlider.setValue(settings.quality())

    @staticmethod
    def boxValue(box):
        idx = box.currentIndex()
        if idx == -1:
            return None

        return box.itemData(idx)

    @staticmethod
    def selectComboBoxItem(box, value):
        for i in range(box.count()):
            if box.itemData(i) == value:
                box.setCurrentIndex(i)
                break




class Camera(QMainWindow):

    def __init__(self, parent=None):
        super(Camera, self).__init__(parent)
        global API
        API = AlgorithmAPIs(template_dir="templates",
                    threshold=0.5,
                    use_multiprocessing=False)
        
        self.ui = Ui_Camera()
        
        self.camera = None
        self.imageCapture = None
        # self.mediaRecorder = None
        self.isCapturingImage = False
        self.applicationExiting = False

        self.imageSettings = QImageEncoderSettings()
        self.audioSettings = QAudioEncoderSettings()
        self.ui.setupUi(self)
        cameraDevice = QByteArray()
        videoDevicesGroup = QActionGroup(self)
        videoDevicesGroup.setExclusive(True)

        for deviceName in QCamera.availableDevices():
            description = QCamera.deviceDescription(deviceName)
            videoDeviceAction = QAction(description, videoDevicesGroup)
            videoDeviceAction.setCheckable(True)
            videoDeviceAction.setData(deviceName)

            if cameraDevice.isEmpty():
                cameraDevice = deviceName
                videoDeviceAction.setChecked(True)

            self.ui.menuDevices.addAction(videoDeviceAction)

        videoDevicesGroup.triggered.connect(self.updateCameraDevice)

        self.ui.lcdNumber_2.display(0)
        
        self.ui.dial.valueChanged.connect(self.dial_display)
        
        global dial_value
        dial_value =3
        self.ui.lcdNumber_2.display(dial_value)
        self.setCamera(cameraDevice)


        # Create and load model
        path_pretrained = "apis/models/facenet/20180402-114759.pb"
        path_SVM = "apis/models/SVM/SVM.pkl"
        self.recognizer = Recognizer()
        self.recognizer.create_graph(path_pretrained, path_SVM)


    def setCamera(self, cameraDevice):
         
        self.camera = cv2.VideoCapture(0)
        self.image = None
        self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(5)

    def dial_display(self,value):
        self.ui.lcdNumber_2.display(value)
        global dial_value
        dial_value = value


    def update_frame(self):
        
        ret,self.image= self.camera.read(0)
        self.image=cv2.flip(self.image,1)

        # Remove motion-blur frame
        if not detect_blur(self.image, thres=5.0):
            face_locs = find_bbox(self.image)
            n_faces = len(face_locs)
            # Remove multi-face frame
            if n_faces==1:
                is_frontal, _ = check_front_view(self.image, face_locs)
                # Remove non-frontal-view frame
                if is_frontal:
                    self.image, _, _ = draw_bbox(self.image, face_locs, color="green")
                    image = cv2.cvtColor(self.image, cv2.COLOR_BGR2RGB)
                    id, score = self.recognizer.recognize(image, (0,0,182,182), 0.29) 
                    print("Student ID: %s, Score: %.4f" % (id, score))
                else:
                    print("Face is not in frontal view")
            else:
                print("Many faces in a frame")
        else:
            print("Frame is montion-blur")



        self.displayImage(self.image,1)

    def displayImage(self,img,window=1):
        
        qformat= QImage.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat= QImage.Format_RGBA8888
            else:
                qformat = QImage.Format_RGB888
        outImage=QImage(img,img.shape[1],img.shape[0],img.strides[0],qformat)
        outImage = outImage.rgbSwapped()
        if window ==1:
            
            self.ui.img_label.setPixmap(QPixmap.fromImage(outImage))
            self.ui.img_label.setScaledContents(True)


    def configureCaptureSettings(self):
        if self.camera.isOpened():
            self.configureImageSettings()
        
    def configureOpenExcels(self):
        settingsopenexcelDialog = OpenExcels()
        settingsopenexcelDialog.initUI()


    def configureImageSettings(self):
        settingsDialog = ImageSettings(self.imageCapture)
        settingsDialog.setImageSettings(self.imageSettings)
        if settingsDialog.exec_():
            self.imageSettings = settingsDialog.imageSettings()
            self.imageCapture.setEncodingSettings(self.imageSettings)



    def train(self):
        PIL_obj = Image.open("images/putin/putin1.jpg")
        img = np.array(PIL_obj)

        # Bounding box
        face_locs = API.find_bbox(img)
        img_draw_bbox, _, _ = API.draw_bbox(img, face_locs, color="green")

        # Extract embedding
        embeddings, faces = API.extract_embedding(img, face_locs)
        n_embeddings = len(embeddings)
        print("Number of embeddings: %d" % (n_embeddings))

        # Save template
        template = {
            "name": "putin",
            "embedding": embeddings[0],
            "face": faces[0]
        }
        savemat(os.path.join(API.template_dir, "putin.mat"), template)
        plt.figure(1)
        plt.imshow(faces[0])
        plt.axis('off')
        plt.title("Registration face")
        plt.show()

    
    def starttest(self):
        PIL_obj = Image.open("images/putin/putin2.jpg")
        img = np.array(PIL_obj)

        # Bounding box
        face_locs = API.find_bbox(img)
        img_draw_bbox, _, _ = API.draw_bbox(img, face_locs, color="green")

        # Extract embedding
        embeddings, faces = API.extract_embedding(img, face_locs)
        n_embeddings = len(embeddings)
        print("Number of embeddings: %d" % (n_embeddings))

        # Identify person
        results = API.matching(embeddings)
        matched, name, face_reg = results[0]
        print("Identified name: %s" % (name))
        if name!="":
            plt.figure(1)
            plt.subplot(1,2,1); plt.title("Input image"); plt.axis('off')
            plt.imshow(img_draw_bbox)
            plt.subplot(1,2,2); plt.title("Registration face"); plt.axis('off')
            plt.imshow(face_reg)
            plt.show()

    def display_absences(self,absences):    
        self.ui.absenceNumber.display(absences)
        if absences == dial_value:

            QMessageBox.warning(self, 'Absent Warning', 'This is your last absence') 
        elif absences > dial_value:
            QMessageBox.critical(None,'Absent Fail',"Your absences exceeded the allowable threshold", QMessageBox.Abort)
    
    def takeImage(self):
        
        self.isCapturingImage = True
        # self.imageCapture.capture()
        s,capture_img = self.camera.read()  # 0 -> index of camera
        if s:     # Camera initialized without any errors
            namedWindow("capture_image",WINDOW_AUTOSIZE)
            imshow("capture_image",capture_img)
            cv2.waitKey(0)
        cv2.destroyWindow("capture_image")
        self.imageSaved("capture_img.png",capture_img)
    

    def startCamera(self):
        self.timer.start(5)

    def stopCamera(self):
        self.timer.stop()


    def displayCameraError(self):
        QMessageBox.warning(self, "Camera error", self.camera.errorString())

    def updateCameraDevice(self, action):
        self.setCamera(action.data())


    def close(self):
        QtCore.QCoreApplication.instance().quit
        sys.exit()

    def imageSaved(self, id, fileName):
        cv2.imwrite(id,fileName)



if __name__ == '__main__':

    app = QApplication(sys.argv)
    camera = Camera()
    camera.show()
    if(sys.exit(app.exec_())):
        camera.close()