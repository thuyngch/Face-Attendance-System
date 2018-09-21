#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------
import cv2
from algorithm_wrapper import AlgorithmAPIs


#------------------------------------------------------------------------------
#	Create an APIs instance
#------------------------------------------------------------------------------
API = AlgorithmAPIs(template_dir="templates",
					threshold=0.5,
					use_multiprocessing=True)


#------------------------------------------------------------------------------
#	Main execution
#------------------------------------------------------------------------------
cap = cv2.VideoCapture("video.mp4")
while(cap.isOpened()):
    _, frame = cap.read()

    cv2.imshow('screen', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()