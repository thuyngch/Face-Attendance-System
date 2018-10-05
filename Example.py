from src.program.AttendanceChecking import AttendanceChecking
from src.program.AudioPlayback import AudioPlayback

file_path = "../data/AttendanceChecking.xlsx"
audios = ["../data/tone.mp3", "../data/face_stable.mp3", "../data/look_ahead.mp3"]
new_xlsx_path = "../data/new.xlsx"
mssv_array = [1512579, 1513372, 1512702, 1512489]

# Guide
# open file > instantiate object > get_total_absence > start_checking

# Example of read temporary local db file and add to excel file
# instantiate object
file1 = AttendanceChecking(file_path)

# get total of absence
print(file1.get_total_absence(1512489))
print(file1.get_total_mssv())

# start doing students' attendance check by adding array of MSSV
file1.start_checking(mssv_array)

# Example of create new standard excel file
AttendanceChecking.new_standard_file(new_xlsx_path)

# playsound
AudioPlayback(audios[2])

