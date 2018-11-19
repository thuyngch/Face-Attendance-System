#----------------------------------------------------------------------------------------------
# Import 
#----------------------------------------------------------------------------------------------
from scipy import misc
import os
import tensorflow as tf
import numpy as np
import lib.facenet as facenet
import lib.detect_face as detect_face
import random

#----------------------------------------------------------------------------------------------
# Main 
#----------------------------------------------------------------------------------------------
class face_aligner:
	# default parameters 
	def __init__(self):
		# minimum size of faces 
		self.minsize = 20 
		# three step's threshold of mtcnn
		self.threshold = [0.6, 0.7, 0.7] 
		# scale factor 
		self.factor = 0.709 
		self.margin = 44
		self.image_size = 182

	def create_mtcnn_graph(self, path_mtcnn):
		print('Creating Multi Tasks networks and loading parameters...')
		with tf.Graph().as_default():
		    gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
		    sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False)) 
		    with sess.as_default():
		        self.pnet, self.rnet, self.onet = detect_face.create_mtcnn(sess, path_mtcnn) 

	def align(self, path_input, path_output):
		# get dataset 
		dataset = facenet.get_dataset(path_input)
		# create output dir 
		if not os.path.exists(path_output):
			os.makedirs(path_output)
        # Add a random key to the filename to allow alignment using multiple processes
		random_key = np.random.randint(0, high=99999)
		bounding_boxes_filename = os.path.join(path_output, 'bounding_boxes_%05d.txt' % random_key)
		with open(bounding_boxes_filename, "w") as text_file:
			# number of images 
			nrof_images_total = 0
			# number of successfully alinged faces 
			nrof_successfully_aligned = 0
			for cls in dataset:
				path_output_class = os.path.join(path_output, cls.name)
				if not os.path.exists(path_output_class):
					os.makedirs(path_output_class)
				for image_path in cls.image_paths:
					nrof_images_total += 1
					filename = os.path.splitext(os.path.split(image_path)[1])[0]
					output_filename = os.path.join(path_output_class, filename + '.png')
					print(image_path)
					if not os.path.exists(output_filename):
					    try:
					        img = misc.imread(image_path)
					        print('read data dimension: ', img.ndim)
					    except (IOError, ValueError, IndexError) as e:
					        errorMessage = '{}: {}'.format(image_path, e)
					        print(errorMessage)
					    else:
					        if img.ndim < 2:
					            print('Unable to align "%s"' % image_path)
					            text_file.write('%s\n' % (output_filename))
					            continue
					        if img.ndim == 2:
					        	img = facenet.to_rgb(img)
					        	print('to_rgb data dimension: ', img.ndim)
					        img = img[:, :, 0:3]
					        # bounding boxes 
					        bounding_boxes, _ = detect_face.detect_face(img, self.minsize, self.pnet, self.rnet, 
					        											self.onet, self.threshold, self.factor)
					        nrof_faces = bounding_boxes.shape[0]
					        print('detected_face: %d' % nrof_faces)
					        if nrof_faces > 0:
					        	det = bounding_boxes[:, 0:4]
					        	img_size = np.asarray(img.shape)[0:2]
					        	if nrof_faces > 1:
					        		bounding_box_size = (det[:, 2] - det[:, 0]) * (det[:, 3] - det[:, 1])
					        		img_center = img_size / 2
							        offsets = np.vstack([(det[:, 0] + det[:, 2]) / 2 - img_center[1],
							                             (det[:, 1] + det[:, 3]) / 2 - img_center[0]])
							        offset_dist_squared = np.sum(np.power(offsets, 2.0), 0)
							        index = np.argmax(bounding_box_size - offset_dist_squared * 2.0)  # some extra weight on the centering
							        det = det[index, :]
						        det = np.squeeze(det)
						        bb_temp = np.zeros(4, dtype=np.int32)
						        bb_temp[0] = np.maximum(det[0], 0)
						        bb_temp[1] = np.maximum(det[1], 0)
						        bb_temp[2] = np.minimum(det[2], img_size[1])
						        bb_temp[3] = np.minimum(det[3], img_size[0])
						        cropped_temp = img[bb_temp[1]:bb_temp[3], bb_temp[0]:bb_temp[2], :]
						        scaled_temp = misc.imresize(cropped_temp, (self.image_size, self.image_size), interp='bilinear')
						        nrof_successfully_aligned += 1
						        misc.imsave(output_filename, scaled_temp)
						        text_file.write('%s %d %d %d %d\n' % (output_filename, bb_temp[0], bb_temp[1], bb_temp[2], bb_temp[3]))
					        else:
					        	print('No faces to align "%s"' % image_path)
					        	text_file.write('%s\n' % (output_filename))
		print('Total number of images: %d' % nrof_images_total)
		print('Number of successfully aligned images: %d' % nrof_successfully_aligned)

#----------------------------------------------------------------------------------------------
# Test 
#----------------------------------------------------------------------------------------------
aligner = face_aligner() 
aligner.create_mtcnn_graph("models/mtcnn")
aligner.align("pre_dataset/raw_dataset", "pre_dataset/aligned_dataset") 