#----------------------------------------------------------------------------------------------
# Import 
#----------------------------------------------------------------------------------------------
import tensorflow as tf
import numpy as np
import funcs.lib.facenet as facenet
import funcs.lib.detect_face as detect_face
import os
import math
from sklearn.svm import SVC
import pickle 

#----------------------------------------------------------------------------------------------
# Main 
#----------------------------------------------------------------------------------------------
class classifier:
	def __init__(self):
		# Base on your hardware to select a reasonable batch size 
		self.batch_size = 128

	def extract_features(self, path_pretrained, path_aligned_faces):
		with tf.Graph().as_default():
			gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
			sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
			with tf.Session() as sess:
				self.dataset = facenet.get_dataset(path_aligned_faces)
				paths, self.labels = facenet.get_image_paths_and_labels(self.dataset)
				print('Loading features extraction model...')
				facenet.load_model(path_pretrained) 
				images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
				""" 
				"embeddings:0" is name of the last layer with size is 512
				"""
				embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
				phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
				embedding_size = embeddings.get_shape()[1]
				# Run forward pass to calculate embeddings
				print('Extracting features for images...') 
				# number of images 
				nrof_images = len(paths)
				# number of batches per epoch
				nrof_batches_per_epoch = int(math.ceil(1.0 * nrof_images / self.batch_size))
				self.emb_array = np.zeros((nrof_images, embedding_size))
				for i in range(nrof_batches_per_epoch):
					start_index = i * self.batch_size
					end_index = min((i + 1) * self.batch_size, nrof_images)
					# paths of images in a batch 
					paths_batch = paths[start_index:end_index]
					# 160 is a fixed size of input of pre-trained graph 
					images = facenet.load_data(paths_batch, False, False, 160)
					# feed dictionary 
					feed_dict = {images_placeholder: images, phase_train_placeholder: False}
					self.emb_array[start_index:end_index, :] = sess.run(embeddings, feed_dict=feed_dict)
		return self.emb_array, self.labels

	def train_SVM(self, path_SVM):
		classifier_filename = path_SVM
		classifier_filename_exp = os.path.expanduser(classifier_filename)
		print('Training classifier...')
		model = SVC(kernel='linear', probability=True)
		model.fit(self.emb_array, self.labels)
		# Create a list of class names
		class_names = [cls.name.replace('_', ' ') for cls in self.dataset]
		# Saving classifier model
		with open(classifier_filename_exp, 'wb') as outfile:
			pickle.dump((model, class_names), outfile)
			print('Saved classifier model to file "%s"' % classifier_filename_exp)