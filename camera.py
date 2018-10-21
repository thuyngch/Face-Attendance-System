
#############################################################################
from PyQt5.QtCore import QByteArray, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QAudioEncoderSettings, QCamera, QImageEncoderSettings
from PyQt5.QtWidgets import QAction, QActionGroup, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog
from PyQt5.QtGui import QImage
from PyQt5 import QtCore, QtWidgets
from ui_camera import Ui_Camera

import os, sys, sqlite3, cv2

from apis.motion_blur import detect_blur
from apis.landmark import find_bbox, draw_bbox, check_front_view
from apis.recognition import Recognizer

from AudioPlayback import AudioPlayback
from AttendanceChecking import AttendanceChecking

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
			camera.file_path = os.path.join(fileName)
			camera.check_db_table(camera.file_path)
			camera.timer.start(5)



class Camera(QMainWindow):

	def __init__(self, parent=None):
		super(Camera, self).__init__(parent)		
		self.ui = Ui_Camera()
		self.pre_id=0
		self.cur_id=0
		self.count=0
		self.checked=0
		self.audio_settime = 0
		self.allow_flag=1
		self.check_list=[]
		self.camera = None
		self.imageCapture = None
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
		self.setCamera(cameraDevice)

		# Create and load model
		path_pretrained = "apis/models/facenet/20180402-114759.pb"
		path_SVM = "apis/models/SVM/SVM.pkl"
		self.recognizer = Recognizer()
		self.recognizer.create_graph(path_pretrained, path_SVM)

		# Others
		self.file_path = ""
		self.audios = ["../data/tone.mp3", "../data/face_stable.mp3", "look_ahead.mp3"]


	def setCamera(self, cameraDevice):
		 
		self.camera = cv2.VideoCapture(0)
		self.image = None
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_frame)
		self.timer.stop()



	def check_db_table(self,filepath):
		
		mssv=[]
		with sqlite3.connect('.TempExcels.db') as db:
			c = db.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		exist = c.fetchone()
		if exist :
			self.ui.textBrowser.append("unsolved data")
			# print("unsolved data")
			c.execute("SELECT * FROM Temp")
			for row in c.fetchall():
				mssv.append(row)
			filecheck = AttendanceChecking(filepath)
			failcases=filecheck.start_checking(mssv)


			self.ui.textBrowser.append("completely solved")
			c.execute('drop table if exists Temp')
			c.execute('create table if not exists Temp(mssv INT NOT NULL)')
			self.ui.textBrowser.append("create a new table - Ready to start")
		else:
			self.ui.textBrowser.append("Data cleared - Ready to start")
			c.execute('create table if not exists Temp(mssv INT NOT NULL)')
		db.commit()
		c.close()
		db.close()



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
					id, score = self.recognizer.recognize(image, face_locs, 0.18825)
					self.pre_id= self.cur_id
					self.cur_id = id
					dis_str= "Student ID: %s, Score: %.4f" % (id, score)

					# Verification: ID was checked or not 
					self.ui.textBrowser.append(dis_str)
					for check_idx in self.check_list:
						if check_idx == id  :
							self.checked =1
						else:
							pass
					# Process if ID has not been checked
					if not self.checked:
						if not id== "unknown":

							# positive ID 
							if self.pre_id==self.cur_id:
								self.count+=1

								# popup after 5 times 
								if self.count ==5:
									id = int(id)
									mssv_check=self.correct_mssv(int(id))
									self.insert_to_db(mssv_check)

									# display the number of absences
									get_total(self.file_path,id)
									self.check_list.append(id)
								else:
									pass
							else:
								self.count =0
						else:
							pass
					else:
						self.ui.textBrowser.append("Student ID had been checked")    
				else:
					dis_str= "Face is not in frontal view"

					self.audio_settime+=1
					if self.audio_settime >= 40:
						self.allow_flag=1
					
					if self.allow_flag:
						AudioPlayback(self.audios[2])
						self.audio_settime=0
						self.allow_flag = 0
					else:
						pass

					self.ui.textBrowser.append(dis_str)
			else:
				dis_str= "Require 1 face in the camera"
				self.ui.textBrowser.append(dis_str)
		else:
			dis_str= "Frame is montion-blurred"
			self.ui.textBrowser.append(dis_str)

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


		
	def configureOpenExcels(self):
		settingsopenexcelDialog = OpenExcels()
		settingsopenexcelDialog.initUI()

	def insert_to_db(self,in_value):
		with sqlite3.connect('.TempExcels.db') as db:
			c = db.cursor()
			c.execute('insert into Temp values(?)',(in_value,))
			db.commit()
			c.close()
			# db.close()

	def display_absences(self,absences):    
		self.ui.absenceNumber.display(absences)
		if absences == 3:
			QMessageBox.warning(self, 'Absent Warning', 'This is your last absence') 
		elif absences > 3:
			QMessageBox.critical(None,'Absent Fail',"Your absences exceeded the allowable threshold", QMessageBox.Abort)
	

	def startCamera(self):
		if not self.file_path:
			QMessageBox.warning(self, "Missing Excel file", "Open Excel File to Start Camera")
		else:
			self.timer.start(5)

	def stopCamera(self):
		self.timer.stop()


	def displayCameraError(self):
		QMessageBox.warning(self, "Camera error", self.camera.errorString())

	def updateCameraDevice(self, action):
		self.setCamera(action.data())


	def close(self):
		QtCore.QCoreApplication.instance().quit
		if self.file_path:
			self.Save_to_excel(self.file_path)
		sys.exit()

	def closeEvent(self, event):
		
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.No)

		if reply == QMessageBox.Yes:
			if self.file_path:
				self.Save_to_excel(self.file_path)
			event.accept()
		else:
			event.ignore()  

	def Save_to_excel(self,filepath):
		if self.file_path:
			mssv=[]
			with sqlite3.connect('.TempExcels.db') as db:
				c = db.cursor()
				c.execute("SELECT * FROM Temp")
				for row in c.fetchall():
					mssv.append(row[0])
				if mssv:
					filecheck = AttendanceChecking(filepath)
					failcases=filecheck.start_checking(mssv)
					c.execute('drop table if exists Temp')
				else:
					self.ui.textBrowser.append("There is nothing to save")
			db.commit()
			c.close()
			db.close()
		else:
			self.ui.textBrowser.append("Open Excel File to process")


	def correct_mssv(self,mssv):
		mssv_check, okPressed = QInputDialog.getInt(self, "Student confirm","MSSV:", mssv, 0, 100000000, 1)
		if okPressed:
			return(mssv_check)





if __name__ == '__main__':

	app = QApplication(sys.argv)
	camera = Camera()
	camera.show()
	if(sys.exit(app.exec_())):
		camera.close()