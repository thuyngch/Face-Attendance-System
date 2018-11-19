#----------------------------------------------------------------------------------------------
# 		Import 
#----------------------------------------------------------------------------------------------
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import numpy as np
import lib.facenet as facenet
import lib.detect_face as detect_face
from config import path_pretrained, path_train_data, path_valid_data, path_test_data, path_SVM, path_train_thres
import os
import math
from sklearn.svm import SVC
from logger import Logger
from sklearn.metrics import accuracy_score
import pickle 
import scipy.io as sio

#----------------------------------------------------------------------------------------------
# 		Main 
#----------------------------------------------------------------------------------------------
# calculate loss 
class classifier:
	def __init__(self):
		# Base on your hardware to select a reasonable batch size 
		self.batch_size = 128

	def extract_features(self, path_pretrained, path_aligned_faces, path_matfile):
		with tf.Graph().as_default():
			gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
			sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
			with sess:
				self.dataset = facenet.get_dataset(path_aligned_faces)
				paths, labels = facenet.get_image_paths_and_labels(self.dataset)
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
				emb_array = np.zeros((nrof_images, embedding_size))
				for i in range(nrof_batches_per_epoch):
					start_index = i * self.batch_size
					end_index = min((i + 1) * self.batch_size, nrof_images)
					# paths of images in a batch 
					paths_batch = paths[start_index:end_index]
					# 160 is a fixed size of input of pre-trained graph 
					images = facenet.load_data(paths_batch, False, False, 160)
					# feed dictionary 
					feed_dict = {images_placeholder: images, phase_train_placeholder: False}
					emb_array[start_index:end_index, :] = sess.run(embeddings, feed_dict=feed_dict)
					# save features 
		sio.savemat(path_matfile, mdict={"embs": emb_array, "labels": labels})
		return emb_array, labels 

	def train_SVM(self, embs_train, labels_train, embs_valid, labels_valid, epoch, path_SVM):
		# num of embs valid 
		size_valid = len(labels_valid) 
		# num of embs train 
		size = len(labels_train) 
		# create mask 
		index_mask = np.zeros((size, 52))  
		index_mask_valid = np.zeros((size_valid, 52)) 
		for i in range(size): 
			index_mask[i,labels_train[i,0]] = 1
		for i in range(size_valid): 
			index_mask_valid[i,labels_valid[i,0]] = 1
		logger_train = Logger("models/log/metrics/train") 
		logger_valid = Logger("models/log/metrics/valid")  
		# create session 
		sess = tf.Session(config=tf.ConfigProto(log_device_placement=True))
		# batch size 
		batch_size = self.batch_size 
		# create placeholder 
		x_data = tf.placeholder(shape=[None, 512], dtype=tf.float32)
		mask = tf.placeholder(shape=[None, 52], dtype=tf.float32)
		y_target = tf.placeholder(shape=[None, 1], dtype=tf.int64)
		# random paramter for linear kernel 
		A = tf.Variable(tf.random_normal(shape=[512,52]))
		b = tf.Variable(tf.random_normal(shape=[1,1])) 
		# output of model SVM (probabilities) 
		model_output = tf.subtract(tf.matmul(x_data, A), b)
		# loss function with linear kernel 
		true_scores = tf.reduce_sum(tf.multiply(model_output, mask), axis=1)
		true_scores = tf.tile(tf.expand_dims(true_scores, axis=1), [1,52]) 
		loss = tf.reduce_sum(tf.maximum(0., tf.subtract(tf.add(1., model_output), true_scores))) 
		# prediction 
		prediction = {
						"probability": tf.reduce_max(model_output, axis=1),
						"class": tf.argmax(model_output, axis=1)} 
		# evaluate metrics 
		acc_train = (batch_size - tf.count_nonzero(tf.subtract(prediction["class"], tf.transpose(y_target))))/batch_size 

		# Declare optimizer
		opt = tf.train.AdamOptimizer(learning_rate=0.01) 
		train_step = opt.minimize(loss) 
		# Initialize variables
		init = tf.global_variables_initializer()
		sess.run(init)
		print('Training classifier...')
		for i in range(epoch):
			# get batch 
			rand_index = np.random.choice(len(labels_train), size=batch_size)
			rand_x = embs_train[rand_index]
			rand_mask = index_mask[rand_index]
			rand_y = labels_train[rand_index] 
			# train 
			sess.run(train_step, feed_dict={x_data: rand_x, mask: rand_mask, y_target: rand_y}) 
			# loss value 
			loss_value = sess.run(loss, feed_dict={x_data: rand_x, mask: rand_mask, y_target: rand_y})
			predict = sess.run(acc_train, feed_dict={x_data: rand_x, mask: rand_mask, y_target: rand_y})  
			print("[{}/{}], loss {:.4f}, accuracy {:.4f}".format(i+1, epoch, loss_value, predict)) 
			if i % 10 == 0:
				acc_valid = 0 
				for j in range(round(size_valid/batch_size)):
					rand_index_valid = np.random.choice(len(labels_valid), size=batch_size)
					rand_x_valid = embs_valid[rand_index_valid] 
					rand_mask_valid = index_mask_valid[rand_index_valid] 
					rand_y_valid = labels_valid[rand_index_valid] 
					# validate
					predict_valid = sess.run(acc_train, feed_dict={
														x_data: rand_x_valid,
														mask: rand_mask_valid, 
														y_target: rand_y_valid})
					acc_valid = acc_valid + predict_valid
				acc_valid = acc_valid/round(size_valid/batch_size)
				# log valid acc 
				logger_valid.scalar_summary('accuracy', acc_valid, i) 


			# log train metrics 
			info = { 'loss': loss_value, 'accuracy': predict} 
			for tag, value in info.items():
				logger_train.scalar_summary(tag, value, i)

#----------------------------------------------------------------------------------------------
# 		Test 
#----------------------------------------------------------------------------------------------
# train data 
train_data = sio.loadmat("features/train.mat")
train_embs = train_data["embs"] 
train_labels = np.transpose(train_data["labels"]) 
# valid data 
valid_data = sio.loadmat("features/valid.mat")
valid_embs = valid_data["embs"] 
valid_labels = np.transpose(valid_data["labels"]) 
print(np.shape(train_labels))
# training 
classifier = classifier() 
classifier.train_SVM(train_embs, train_labels, valid_embs, valid_labels, 500, path_SVM)