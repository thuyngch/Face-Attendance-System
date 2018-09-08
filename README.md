# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written by Python.


# Setup guidance
* Install virtualenv:
```
sudo pip3 install virtualenv
```
* Create virtual environment folder:
```
mkdir ~/.virtualenvs
cd ~/.virtualenvs
```
* Create a virtual environment, named *face_attendace*:
```
virtualenv -p python3 face_attendace
workon face_attendace
```
* Change to the directory containing our porject, then install requirements:
```
cd dir_to_project
pip install -r requirements.txt
```
* Check the result:
```
pip freeze
```
If the printed result is as the following, your setup is successful
```
click==6.7
dlib==19.15.0
face-recognition==1.2.1
face-recognition-models==0.3.0
numpy==1.15.1
opencv-python==3.3.1.11
Pillow==5.2.0
scipy==1.1.0
```
