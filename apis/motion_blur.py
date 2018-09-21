#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------


#------------------------------------------------------------------------------
#	Detect the motion blur in an RGB image.
#------------------------------------------------------------------------------
def detect_blur(image, thres=0):
	"""
	Arguments:
		image : (ndarray) RGB image with shape of [width, height, channel].
		thres : (int) The threshold to indicate whether an image is blur.

	Return:
		is_blur : (bool) The image is blur or not?
	"""
	pass