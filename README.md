# Face-Attendance-System
An Attendance Checking System using Deep Facial Recognition, written in Python.


# Branch description
In this branch, an Algorithm wrapper is developed in order to create an intermediate communication layer between the Technical team and Algorithm team. There are two key files, namely *"algorithm_wrapper.py"* and *"test-bench.py"*.
* *"algorithm_wrapper.py"* contains algorithm-wrapper APIs.
* *"test-bench.py"* is a test-bench example for using algorithm-wrapper APIs in the file *"algorithm_wrapper.py"*.


# Setup guidance

* If you have not set up the virtual environment *face_attendance*, please follow this [link](https://github.com/AntiAegis/Face-Attendance-System/blob/collect_data_tool/README.md) to setup it.
* Change to the directory containing your downloaded project, and activate the virtual environment *face_attendance*:
```
cd <dir_to_project>
workon face_attendance
```
* Install requirement packages:
```
pip install -r requirements.txt
```


# Team members

* **Nguyen Chinh Thuy** - *Technical*, *Functional management*
* **Le Van Hoang Phuong** - *Technical*, *Attendance management*
* **Nguyen Tan Sy** - *Technical*, *GUI*
* **Do Tieu Thien** - *Algorithm*, *Face recognition*
* **Nguyen Van Qui** - *Algorithm*, *Face detection and normalization*
* **Nguyen Tan Phu** - *Algorithm*, *Blur removal*