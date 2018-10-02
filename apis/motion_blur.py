#------------------------------------------------------------------------------
#	Libraries
import numpy as np 
import cv2
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
	shape_img= image.shape 		# [width, height, channel]= [640,480,3]	
	img_gray= cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
	FFT_image= np.fft.fft2(img_gray)
	mag_val= np.log(np.abs(FFT_image))
	mag_avg= np.mean((mag_val))

	thres= 7.089 					
	if mag_avg < thres:
		is_blur = True		# blurred
	else:
		is_blur = False		# unblurred
	return is_blur
	