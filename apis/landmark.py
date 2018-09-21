#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#	Find bounding box(es) of face(s) within an image.
#------------------------------------------------------------------------------
def find_bbox(image):
	"""
	Arguments:
		image : (ndarray) RGB image with shape of [width, height, channel].

	Return:
		face_locs : (list) Coordinates of the bounding box as the following
					[(y_top, x_left, width, height)].
	"""
	pass


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
	pass


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
	"""
	pass