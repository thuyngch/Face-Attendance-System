# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written in Python.


## Introduction
* This is our final project in the course "***Artificial Intelligence in Control Engineering***" (August-December 2018), guided by **Dr. Cuong Pham-Viet** (Faculty of Electrical and Electronics Engineering, Ho Chi Minh city University of Technology, Vietnam).

* We have developed an automatic Attendance Checking System that can be used in classes by teachers to check attendances of their students.

* Face is used as clue for indentifying who a person is.

* An easy-to-use GUI is integrated so that users can use the system effortlessly without any specialized knowledge.

* Underlying the GUI, Deep Facial Recognition techniques are exploited as backbone of the system.

* The system is deployed in standard portable laptops, which are commonly used by Vietnamese lecturers as well as students. Webcam integrated in laptops is to capture input images.


## Algorithm description
* The whole system can be modeled as the figure below. There are four stages, namely blur detection, face detection, landmark detection, and face recognition. These four blocks are in the descending order of size in the direction from input to output. This points out that our system is tougher to input frames from the camera when such frames passed through the system. Therefore, best frames are likely to be processed, which may improve both the final recognition accuracy and processing time.
<p align="center">
  <img src="https://github.com/AntiAegis/Face-Attendance-System/blob/master/report/img/system-pipeline.png" width="700" alt="accessibility text">
</p>

* First, given an input frame from the webcam, the **Blur Detection** is reponsible for removing blur frames due to motions of scanned people in front of the camera.

* Second, the **Face Detection** is to localize region containing face in the image. Besides, our system only accepts frames that have one face. Therefore, frames with more than two faces are ignored, yet warnings are also notified.

* Subsequently, frames are passed through the **Lankmark Detection** stage. In here, coordinates of salient points in a face (e.g., eye centers, nose, and mouth corners) are pointed out. The algorithm employs this information to check whether a person is in frontal view of the camera. If not satisfy the condition, the frame is bypassed.

* Finally, blur-clean, one-face, and frontal-view frames are processed in the **Face Recognition** stage to identify who a person is. Because during the training phase, we explored outlier distribution of identities (registered people), then the system is able to recognize people that have not registered in the system before.


## GUI description
* The GUI (shown in the figure below) in Python is designed and programmed with the PyQT5 package.
<p align="center">
  <img src="https://github.com/AntiAegis/Face-Attendance-System/blob/master/report/img/user_guide.png" width="550" alt="accessibility text">
</p>

* The GUI can communicate to get frames from the webcam and call APIs of algorithm to process these frames.

* To boost the convenience of use, the GUI is facilitated with an **Attendance Management** module. More specifically, the GUI uses algorithm APIs to identify checked people and manages these results in an Excel file. Thus, owner of the program just need to open the Excel file after the checking procedure to see who attended class.

* In addition, to make sure people joining the checking procedure stand in the best view to the camera, we continued introducing an **Attention** module, which informs (with voice) checkees whether they are in the accepted view of the system, so that they can change their position to match to requirements of the system.


## Setup guidance
* Install dependences:
```
sudo apt-get install -y python-pip python3-pip cmake
```
* Create a folder containing virtual environments:
```
mkdir ~/.virtualenvs
cd ~/.virtualenvs
```
* Install virtual-environment packages:
```
sudo /usr/local/bin/pip install virtualenv virtualenvwrapper
sudo /usr/local/bin/pip3 install virtualenv virtualenvwrapper
```
* Using a text editor, open file "~/.bashrc", then add the following text into the end of the file, and save the file:
```
# virtualenv and virtualenvwrapper
export WORKON_HOME=$HOME/.virtualenvs
export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
source /usr/local/bin/virtualenvwrapper.sh
```
* Create a virtual environment, named *face_attendace*:
```
source ~/.bashrc
/usr/local/bin/virtualenv -p /usr/bin/python3 face_attendace
workon face_attendace
```
* Change to the directory containing your downloaded project, then install requirements:
```
cd <dir_to_project>
pip install -r requirements.txt
```


## Demo
* [Small demo](https://www.youtube.com/watch?v=XzDDHDtsNwk)


## Team members
* **Nguyen Chinh Thuy** - *work generally*, *arrage tasks*
* **Do Tieu Thien** - *responsible for algorithms*, *implement the Face Recognition stage*
* **Nguyen Tan Sy** - *implement GUI*
* **Le Van Hoang Phuong** - *implement the Attendace Management and Attention modules in GUI*
* **Nguyen Van Qui** - *implement the Face and Lanmark Detection stages*
* **Nguyen Tan Phu** - *implement the Blur Detection stage*
