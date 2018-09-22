# import the necessary packages
from scipy import misc
import numpy as np
import dlib
import cv2
import glob
import os


# initialize dlib's face detector (HOG-based) and then create
# the facial landmark predictor
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("data_landmark/shape_predictor_68_face_landmarks.dat"))

# coordinates of the eye
LEFT_EYE_INDICES = [36, 37, 38, 39, 40, 41]
RIGHT_EYE_INDICES = [42, 43, 44, 45, 46, 47]


def rect_to_tuple(rect):
    left = rect.left()
    right = rect.right()
    top = rect.top()
    bottom = rect.bottom()
    return left, top, right, bottom

def extract_eye(shape, eye_indices):
    points = map(lambda i: shape.part(i), eye_indices)
    return list(points)

def extract_eye_center(shape, eye_indices):
    points = extract_eye(shape, eye_indices)
    xs = map(lambda p: p.x, points)
    ys = map(lambda p: p.y, points)
    return sum(xs) // 6, sum(ys) // 6

def extract_left_eye_center(shape):
    return extract_eye_center(shape, LEFT_EYE_INDICES)

def extract_right_eye_center(shape):
    return extract_eye_center(shape, RIGHT_EYE_INDICES)

def angle_between_2_points(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    tan = (y2 - y1) / (x2 - x1)
    return np.degrees(np.arctan(tan))

def get_rotation_matrix(p1, p2):
    angle = angle_between_2_points(p1, p2)
    x1, y1 = p1
    x2, y2 = p2
    xc = (x1 + x2) // 2
    yc = (y1 + y2) // 2
    M = cv2.getRotationMatrix2D((xc, yc), angle, 1)
    return M

def crop_image(image, det):
    left, top, right, bottom = rect_to_tuple(det)
    return image[top:bottom, left:right]

def get_face(img):
	height, width = img.shape[:2]
	dets = detector(img, 1)
	if len(dets) > 1:
		return None
	for det in dets:
		shape = predictor(img, det)
		left_eye = extract_left_eye_center(shape)
		right_eye = extract_right_eye_center(shape)

		M = get_rotation_matrix(left_eye, right_eye)
		rotated = cv2.warpAffine(img, M, (width, height), flags=cv2.INTER_CUBIC)

		cropped = crop_image(rotated, det)
		cropped = misc.imresize(cropped, (160, 160), interp='bilinear')
		return cropped

def save_face(img, output_image_path):
	cv2.imwrite(output_image_path, img)


def main():
	# load input image, resize it, and convert it
	if not os.path.exists('dataset'):
		os.makedirs('dataset')

	path_sr = glob.glob(os.path.join('face-dataset','*'))
	for st in path_sr:
		# create destination folder 
		mssv = st.split(os.path.sep)[-1]
		path_des = os.path.join('dataset',mssv)
		if not os.path.exists(path_des):
			os.makedirs(path_des)
		# get image
		links_img = glob.glob(os.path.join(st,'*.png'))
		for link in sorted(links_img):
			start = os.times()[-1]
			name_face = link.split(os.path.sep)[-1]	
			img = cv2.imread(link)
			face = get_face(img)
			if not face is None:			
				save_face(face, os.path.join(path_des, name_face))
				print('image %s saved' % (name_face))
				end = os.times()[-1]
				print('Times cost: %.4f' % (end-start))
			else:
				print('skip image: %s' % name_face)
if __name__ == '__main__':
	main()
