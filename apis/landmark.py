import dlib
import cv2
from imutils import face_utils
import numpy as np


detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("apis/data_landmark/shape_predictor_5_face_landmarks.dat")


def rect_to_list(dets):
    face_locs = []
    for det in dets:
        (x, y, w, h) = face_utils.rect_to_bb(det)
        face_locs.append((y, x, w, h))
    return face_locs

def find_bbox(image):
    """
    Arguments:
        image : (ndarray) RGB image with shape of [width, height, channel].
    Return:
        face_locs : (list) Coordinates of the bounding box as the following
                    [(y_top, x_left, width, height)].
    """
    dets = detector(image, 0)
    face_locs = rect_to_list(dets)
    return face_locs


def list_to_rect(face_loc):
    assert len(face_loc) == 1
    y, x, w, h = face_loc[0]
    return dlib.rectangle(left=x, top=y, right=x+w, bottom=y+h)


#------------------------------------------------------------------------------
#	Draw bounding box(es) into an image.
#------------------------------------------------------------------------------
def draw_bbox(image, face_locs, color="blue"):
    """
    Arguments:
        image : (ndarray) RGB image with shape of [width, height, channel].
        face_locs : (list) Coordinates of the bounding box.
        color : (str) Color of bounding box, including "red", "green", and
                "blue". Default color is "blue"
    Return:
        image_drawn : (ndarray) The image drawn bounding box.
        corner1 : (ndarray) Left-Top coordinates of the bounding box.
        corner2 : (ndarray) Right-Bottom coordinates of the bounding box.
    """
    output = image.copy()
    if not isinstance(face_locs, list):
        face_locs = rect_to_list(face_locs)

    colors = {'blue': (255,0,0), 'green': (0,255,0), 'red': (0,0,255)}
    for face_loc in face_locs:
        top, left, width, height = face_loc
        corner1 = (left, top)
        corner2 = (left+width, top+height)
        cv2.rectangle(output, corner1, corner2, colors[color], 2)
    return output, corner1, corner2

#------------------------------------------------------------------------------
#	Verify whether a face is in front view
#------------------------------------------------------------------------------
def check_front_view(image, face_loc):
    """
    Arguments:
        image : (ndarray) RGB image with shape of [width, height, channel].
        face_loc : (list) Coordinates of a bounding box.
    Return:
        is_front_face : (bool) The face is in the front view or not?
        message : (str) 
    """
    assert len(face_loc) == 1
    assert image.shape[0] == 480

    top, left, width, _ = face_loc[0]
    if not (120 < left < 360 and 90 < top < 230):
        return 0, 'Put your face in the center'

    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    face_loc_rect = list_to_rect(face_loc)
    shape = predictor(gray, face_loc_rect)
    shape = face_utils.shape_to_np(shape)

    left_eye = shape[0]
    right_eye = shape[2]
    angle = angle_between_2_points(left_eye, right_eye)
    if angle > 10 :
        return 0, 'Keep your face straight'
    
    nose = shape[4][0]
    center = (left_eye[0] + right_eye[0])//2
    if(abs((nose - left) - (left + width - nose)) > 20 or \
        abs(nose - center) > 20):
        return 0, 'Dont rotate your face'

    return 1, 'OK'

#-------------------------------------------------
#  Calculate the angle
#-------------------------------------------------
def angle_between_2_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    tan = (y2 - y1) / (x2 - x1)
    return np.degrees(np.arctan(tan))