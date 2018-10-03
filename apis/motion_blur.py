#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------
import numpy as np 
import cv2


#------------------------------------------------------------------------------
#	Detect the motion blur in an RGB image.
#------------------------------------------------------------------------------
def detect_blur(image, thres=7.965):
	"""
	Arguments:
		image : (ndarray) RGB image with shape of [width, height, channel].
		thres : (int) The threshold to indicate whether an image is blur.

	Return:
		is_blur : (bool) The image is blur or not?
	"""
	img_gray= cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
	FFT_image= np.fft.fft2(img_gray)
	mag_val= np.log(np.abs(FFT_image))
	mag_avg= np.mean((mag_val))

	is_blur = True if mag_avg<thres else False
	return is_blur