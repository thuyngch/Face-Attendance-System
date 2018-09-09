# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written in Python.


# Setup guidance
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
sudo pip install virtualenv virtualenvwrapper
sudo pip3 install virtualenv virtualenvwrapper
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
virtualenv -p /usr/bin/python3 face_attendace
workon face_attendace
```
* Change to the directory containing your downloaded porject, then install requirements:
```
cd <dir_to_project>
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


## Team members

* **Nguyen Chinh Thuy** - *Technical*, *Functional management*
* **Le Van Hoang Phuong** - *Technical*, *Attendance management*
* **Nguyen Tan Sy** - *Technical*, *GUI*
* **Do Tieu Thien** - *Algorithm*, *Face recognition*
* **Nguyen Van Qui** - *Algorithm*, *Face detection and normalization*
* **Nguyen Tan Phu** - *Algorithm*, *Blur removal*
