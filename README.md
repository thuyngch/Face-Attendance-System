# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written in Python.
[Small demo](https://www.youtube.com/watch?v=XzDDHDtsNwk)


## Introduction
* This is our final project in the course "*Artificial Intelligence in Control Engineering*" (August-December 2018), guided by Dr. Cuong Pham-Viet (Faculty of Electrical and Electronics Engineering, HoChiMinh city University of Technology, Vietnam).
* We have developed an automatic Attendance Checking System that can be used in classes by teachers to check attendances of their students.
* Face is used as clue for indentifying who a person is.
* An easy-to-use GUI is integrated so that users can use the system effortlessly without any specialized knowledge.
* Underlying the GUI, Deep Facial Recognition techniques are exploited as backbone of the system.


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


## Team members

* **Nguyen Chinh Thuy** - *Technical*, *Functional management*
* **Le Van Hoang Phuong** - *Technical*, *Attendance management*
* **Nguyen Tan Sy** - *Technical*, *GUI*
* **Do Tieu Thien** - *Algorithm*, *Face recognition*
* **Nguyen Van Qui** - *Algorithm*, *Face detection and normalization*
* **Nguyen Tan Phu** - *Algorithm*, *Blur removal*
