from PyQt5.QtCore import QByteArray, QTimer
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap
from PyQt5.QtMultimedia import QCamera
from PyQt5.QtWidgets import QAction, QActionGroup, QMainWindow, QMessageBox
from PyQt5.QtWidgets import QWidget, QInputDialog, QFileDialog
from PyQt5.QtGui import QImage
from PyQt5 import QtCore, QtWidgets
from ui_camera import Ui_Camera
from apis.motion_blur import detect_blur
from apis.landmark import find_bbox, draw_bbox, check_front_view
from apis.recognition import Recognizer
from AudioPlayback import AudioPlayback
from AttendanceChecking import AttendanceChecking
import os, sys, sqlite3, cv2

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
	"""[get absent times]
	
	[fetch absent value from excels file and screen them]
	
	Arguments:
		filepath {[string]} -- [excels file]
		mssv {[int]} -- [student ID]
	"""
	file1 = AttendanceChecking(filepath)
	absent=file1.get_total_absence(mssv)
	Camera.display_absences(camera,absent)
	

class OpenExcels(QWidget):
 
	def __init__(self):
		super().__init__()
		self.title = 'Open Excel Files'
		self.left = 10
		self.top = 10
		self.width = 640
		self.height = 480
  
 
	def openinitUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.openFileNameDialog() 
		self.show()


	def saveinitUI(self):
		self.setWindowTitle(self.title)
		self.setGeometry(self.left, self.top, self.width, self.height)
		self.saveFileDialog()
		self.show()
 

	def openFileNameDialog(self):
		"""[show dialog to open file]
		
		[Unless the file is correct in terms of content and form, progress will not start ]
		"""

		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getOpenFileName(self,"Open Excels", "","Excel Workbook (*.xlsx)", options=options)
		camera.file_path = os.path.join(fileName)

		while camera.file_path:
			if not camera.file_path.endswith('.xlsx'):
				QMessageBox.warning(self, 'File Type Warning', ' Wrong Type Selected') 
				fileName, _ = QFileDialog.getOpenFileName(self,"Open Excels", "","Excel Workbook (*.xlsx)", options=options)		
				camera.file_path = os.path.join(fileName)
				if camera.file_path == "":
					break
				continue
			file2= AttendanceChecking(camera.file_path)
			if not file2.if_standard_excel():
				QMessageBox.warning(self, 'File Content Warning', ' Wrong File Content') 
				fileName, _ = QFileDialog.getOpenFileName(self,"Open Excels", "","Excel Workbook (*.xlsx)", options=options)		
				camera.file_path = os.path.join(fileName)
				continue
			else:
				break
		if camera.file_path:	
			camera.check_db_table(camera.file_path)
			camera.timer.start(5)


	def saveFileDialog(self):
		"""[show dialog to save file]
		
		[Save exist template to location as specified by the user
		the type of file is .xlsx]
		"""

		options = QFileDialog.Options()
		options |= QFileDialog.DontUseNativeDialog
		fileName, _ = QFileDialog.getSaveFileName(self,"Save Template","","All Files (*);;Excel Files (*.xlsx)", options=options)
		if fileName:
		    camera.save_path = os.path.join(fileName)
		    file3= AttendanceChecking(camera.save_path)		    
		    if not camera.save_path.endswith('.xlsx'):
		    	camera.save_path+=".xlsx"
		    file3.new_standard_file(camera.save_path)


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
		'''[setup camera]
		
		[correct camera parameters]
		
		Arguments:
			cameraDevice -- [laptop camera]
		'''
		 
		self.camera = cv2.VideoCapture(0)
		self.image = None
		self.camera.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
		self.camera.set(cv2.CAP_PROP_FRAME_WIDTH,640)
		self.timer = QTimer()
		self.timer.timeout.connect(self.update_frame)
		self.timer.stop()


	def check_db_table(self,filepath):
		'''[check if there is table.]
		
		[if there is table, save to excel then blank new table, if there isn't table create new table.]
		
		Arguments:
			filepath {[string]} -- [excel path]
		'''
		
		mssv=[]
		with sqlite3.connect('.TempExcels.db') as db:
			c = db.cursor()
		c.execute("SELECT name FROM sqlite_master WHERE type='table';")
		exist = c.fetchone()
		if exist :
			self.ui.textBrowser.append("unsolved data")
			c.execute("SELECT * FROM Temp")
			for row in c.fetchall():
				mssv.append(row)
			filecheck = AttendanceChecking(filepath)
			failcases=filecheck.start_checking(mssv)
			fail_str = "Incomplete IDs:\n"
			if failcases:
				for failcase in failcases:
					fail_str= fail_str + str(failcase)+"\n"
				
				QMessageBox.warning(self, 'Failcase list', fail_str)
				
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
		'''[process frame]
		
		[face recognition ]
		'''
		
		ret,self.image= self.camera.read(0)
		self.image=cv2.flip(self.image,1)
		# Remove motion-blur frame
		if not detect_blur(self.image, thres=5.0):
			face_locs = find_bbox(self.image)
			n_faces = len(face_locs)
			# Remove multi-face frame
			if 0<n_faces<=3:
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
							self.checked = True
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
									if mssv_check:
										self.insert_to_db(mssv_check)
										# display the number of absences
										get_total(self.file_path,id)
										self.check_list.append(mssv_check)
										#print(self.check_list)
										self.checked = False
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
				dis_str= "Require no more than 3 faces"
				self.ui.textBrowser.append(dis_str)
		else:
			dis_str= "Frame is montion-blurred"
			self.ui.textBrowser.append(dis_str)
		self.displayImage(self.image,1)


	def displayImage(self,img,window=1):

		"""[display frame]
		
		[correct image type and on-screen display]
		
		Arguments:
			img {[cv2 image]} -- [processed frame]
		
		Keyword Arguments:
			window {number} -- [description] (default: {1})
		"""
		
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

		"""[config to open File]
		
		"""
		settingsopenexcelDialog = OpenExcels()
		settingsopenexcelDialog.openinitUI()


	def configureSavetemplate(self):

		"""[config to save File]
		
		"""
		settingssaveexcelDialog= OpenExcels()
		settingssaveexcelDialog.saveinitUI()


	def insert_to_db(self,in_value):
		"""[save value to .db file]
		
		[Student IDs received after recognising will be saved to a temp table called Temp ]
		
		Arguments:
			in_value {[int]} -- [(int)value to save into .db file ]
		"""
		with sqlite3.connect('.TempExcels.db') as db:
			c = db.cursor()
			c.execute('insert into Temp values(?)',(in_value,))
			db.commit()
			c.close()


	def display_absences(self,absences):
		"""[display the number of absences]
		
		[The number of absences of each ID will be on-screen 
		if absent times >= threshold, a notification will appear on the screen]
		
		Arguments:
			absences {[int]} -- [absent times]
		"""
		self.ui.absenceNumber.display(absences)
		if absences == 3:
			QMessageBox.warning(self, 'Absent Warning', 'This is your last absence') 
		elif absences > 3:
			QMessageBox.critical(None,'Absent Fail',"Your absences exceeded the allowable threshold", QMessageBox.Abort)
	

	def startCamera(self):
		"""[start camera]
		
		[Unless file path is invalid, camera is closed]
		"""
		if not self.file_path:
			QMessageBox.warning(self, "Missing Excel file", "Open Excel File to Start Camera")
		else:
			self.timer.start(5)


	def stopCamera(self):
		self.timer.stop()


	def displayCameraError(self):
		QMessageBox.warning(self, "Camera error", self.camera.errorString())


	def updateCameraDevice(self, action):
		"""[update camera]
		
		[Look for active cameras]
		
		Arguments:
			action  -- [flag of a active camera]
		"""
		self.setCamera(action.data())


	def close(self):
		"""[close event]
		
		[if there is a close event,data in the table will be saved to excel file  ]
		"""
		QtCore.QCoreApplication.instance().quit
		reply = QMessageBox.question(self, 'Message',
			"Are you sure to quit?", QMessageBox.Yes | 
			QMessageBox.No, QMessageBox.No)
		if reply == QMessageBox.Yes:
			if self.file_path:
				self.Save_to_excel(self.file_path)
			sys.exit()


	def closeEvent(self, event):
		"""[close event ]
		
		[if we have a force exit event, a notification will be display for checking quit action
		if event is accepted, data will be saved and program close ]
		
		Arguments:
			event {[event]} -- [exit event from click (X)]
		"""
		
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
		"""[save data to excels]
		
		[Fetch data from table and save them to Excels]
		
		Arguments:
			filepath {[string]} -- [Excel file path]
		"""

		if self.file_path:
			mssv=[]
			with sqlite3.connect('.TempExcels.db') as db:
				c = db.cursor()
				c.execute("SELECT * FROM Temp")
				for row in c.fetchall():
					mssv.append(row[0])
				if mssv:
					filecheck = AttendanceChecking(self.file_path)
					failcases=filecheck.start_checking(mssv)
					fail_str = "Incomplete IDs:\n"
					if failcases:
						for failcase in failcases:
							fail_str= fail_str + str(failcase)+"\n"
						
						QMessageBox.warning(self, 'Failcase list', fail_str)
					c.execute('drop table if exists Temp')
					c.execute('create table if not exists Temp(mssv INT NOT NULL)')
				else:
					self.ui.textBrowser.append("There is nothing to save")
			db.commit()
			c.close()
			db.close()
		else:
			self.ui.textBrowser.append("Open Excel File to process")


	def correct_mssv(self,mssv):
		"""[confirm student ID]
		
		[confirm recognised student ID
		if ID is wrong, fill out another one and press Enter]
		
		Arguments:
			mssv {[int]} -- [student ID]
		"""
		mssv_check, okPressed = QInputDialog.getInt(self, "Student confirm","MSSV:", mssv, 0, 100000000, 1)
		if okPressed:
			return(mssv_check)
		else:
			return(0)





if __name__ == '__main__':

	app = QApplication(sys.argv)
	camera = Camera()
	camera.show()
	if(sys.exit(app.exec_())):
		camera.close()
