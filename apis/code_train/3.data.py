import os 
import cv2 
import numpy as np 
path_data = "pre_dataset/aligned_dataset"
path_out_1 = "dataset/train" 
path_out_2 = "dataset/valid"
path_out_3 = "dataset/test"
# path_out_4 = "dataset/train_thres" 
path_idens = [os.path.join(path_data, file) for file in os.listdir(path_data)] 
np.random.shuffle(path_idens) 
for path_iden in path_idens:
	name_iden = os.path.split(path_iden)[1] 
	output_path_1 = os.path.join(path_out_1, name_iden)
	output_path_2 = os.path.join(path_out_2, name_iden) 
	output_path_3 = os.path.join(path_out_3, name_iden) 
	# output_path_4 = os.path.join(path_out_4, name_iden)  
	if not os.path.exists(output_path_1):
		os.makedirs(output_path_1) 
	if not os.path.exists(output_path_2):
		os.makedirs(output_path_2)
	if not os.path.exists(output_path_3):
		os.makedirs(output_path_3)
	# if not os.path.exists(output_path_4):
	# 	os.makedirs(output_path_4)
	path_images = [os.path.join(path_iden, file) for file in os.listdir(path_iden)]
	count = 0 
	for path_image in path_images:
		if (count >= 30) and (count < 40):
			name_image = os.path.split(path_image)[1] 
			print(name_image)
			image = cv2.imread(path_image) 
			cv2.imwrite("dataset/valid/" + name_iden + '/' + name_image, image)

		if (count >= 40) and (count < 60):
			name_image = os.path.split(path_image)[1] 
			print(name_image)
			image = cv2.imread(path_image) 
			cv2.imwrite("dataset/test/" + name_iden + '/' + name_image, image)

		# if (count >= 60) and (count < 90):
		# 	name_image = os.path.split(path_image)[1] 
		# 	print(name_image)
		# 	image = cv2.imread(path_image) 
		# 	cv2.imwrite("dataset/train_thres/" + name_iden + '/' + name_image, image)

		if count < 30: 
			name_image = os.path.split(path_image)[1] 
			print(name_image)
			image = cv2.imread(path_image) 
			cv2.imwrite("dataset/train/" + name_iden + '/' + name_image, image)
		count = count + 1			