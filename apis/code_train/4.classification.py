#----------------------------------------------------------------------------------------------
# Import 
#----------------------------------------------------------------------------------------------
import tensorflow as tf
from tensorflow.contrib.tensorboard.plugins import projector
import numpy as np
import lib.facenet as facenet
import lib.detect_face as detect_face
from config import path_pretrained, path_train_data, path_valid_data, path_test_data, path_SVM, path_train_thres, path_log
import os
import math
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import pickle 
import scipy.io as sio
np.random.seed(0) 

#----------------------------------------------------------------------------------------------
# Class 
#----------------------------------------------------------------------------------------------
class classifier:
	def __init__(self, path_aligned_faces):
		# Base on your hardware to select a reasonable batch size 
		self.batch_size = 128

	def extract_features(self, path_pretrained, path_aligned_faces, path_matfile):
		with tf.Graph().as_default():
			gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=0.5)
			sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
			with tf.Session() as sess:
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

	def train_SVM(self, embs_train, labels_train, embs_valid, labels_valid, path_SVM):
		classifier_filename = path_SVM
		classifier_filename_exp = os.path.expanduser(classifier_filename)
		print('Training classifier...')
		model = SVC(kernel='linear', probability=True)
		# train SVM 
		model.fit(embs_train, labels_train)
		# validation  
		labels_predict = model.predict(embs_valid) 
		acc = accuracy_score(labels_valid, labels_predict) 
		print("Accuracy of SVM model is %f" % acc) 
		# Create a list of class names
		class_names = [cls.name.replace('_', ' ') for cls in self.dataset]
		# Saving classifier model
		with open(classifier_filename_exp, 'wb') as outfile:
			pickle.dump((model, class_names), outfile)
			print('Saved classifier model to file "%s"' % classifier_filename_exp)

	def get_thres(self, emb_array, labels, path_SVM):
		num_embs = len(labels) 
		classifier_filename_exp = os.path.expanduser(path_SVM) 
		thres = np.arange(0, 1, 0.001) 
		with open(classifier_filename_exp, 'rb') as infile:
			(model, class_names) = pickle.load(infile) 
			predictions = model.predict_proba(emb_array) 
			best_class_indices = np.argmax(predictions, axis=1) 
			acc_max = 0 
			best_thres = 0 
			for i in thres:
				new_indices = np.zeros(num_embs)
				acc = 0 
				for j in range(num_embs):
					label_true = labels[j] 
					label_predict = best_class_indices[j] 
					proba = predictions[j, label_predict] 
					if (proba >= i) and (label_predict == label_true):
						acc = acc + 1
				if acc >= acc_max:
					acc_max = acc 
					best_thres = i 
		return best_thres  

	def validate(self, test_embs, test_labels, thres, path_SVM):
		num_embs = len(test_labels)
		unknown = max(test_labels) 
		classifier_filename_exp = os.path.expanduser(path_SVM)
		with open(classifier_filename_exp, 'rb') as infile:
			(model, class_names) = pickle.load(infile)
			predictions = model.predict_proba(test_embs) 
			best_class_indices = np.argmax(predictions, axis=1)
			for i in range(num_embs):
				if predictions[i, best_class_indices[i]] < thres:
					best_class_indices[i] = unknown
		acc = accuracy_score(test_labels, best_class_indices) 
		print("Accuracy of validation is %f" % acc) 	

	def visualize(self, train_embs, train_labels, log_dir):
		metadata = os.path.join(log_dir, 'metadata.tsv')
		embs = tf.Variable(train_embs, name='embs')
		with open(metadata, 'w') as metadata_file:
		    for label in train_labels:
		        metadata_file.write('%d\n' % label) 
		with tf.Session() as sess:
		    saver = tf.train.Saver([embs]) 
		    sess.run(embs.initializer)
		    saver.save(sess, os.path.join(log_dir, 'embs.ckpt'))
		    config = projector.ProjectorConfig()
		    # One can add multiple embeddings.
		    embedding = config.embeddings.add()
		    embedding.tensor_name = embs.name
		    # Link this tensor to its metadata file (e.g. labels).
		    embedding.metadata_path = metadata
		    # Saves a config file that TensorBoard will read during startup.
		    projector.visualize_embeddings(tf.summary.FileWriter(log_dir), config)

#----------------------------------------------------------------------------------------------
# Main 
#----------------------------------------------------------------------------------------------
classifier = classifier(path_train_data)   
if not os.path.exists("features/test.mat"):
	test_embs, test_labels = classifier.extract_features(path_pretrained, path_test_data, "features/test.mat") 
else:
	test_data = sio.loadmat("features/test.mat") 
	test_embs = test_data["embs"] 
	test_labels = test_data["labels"][0]

if not os.path.exists("features/train.mat"):
	train_embs, train_labels = classifier.extract_features(path_pretrained, path_train_data, "features/train.mat") 
else:
	train_data = sio.loadmat("features/train.mat")
	train_embs = train_data["embs"] 
	train_labels = train_data["labels"][0]

if not os.path.exists("features/valid.mat"):
	valid_embs, valid_labels = classifier.extract_features(path_pretrained, path_valid_data, "features/valid.mat") 
else:
	valid_data = sio.loadmat("features/valid.mat") 
	valid_embs = valid_data["embs"] 
	valid_labels = valid_data["labels"][0]  
classifier.train_SVM(train_embs, train_labels, valid_embs, valid_labels, path_SVM)
# data for traning thres 
x = np.concatenate((train_embs, valid_embs), axis=0)
y = np.concatenate((train_labels, valid_labels), axis=0) 
num_embs = np.shape(y)[0]
# shuffle data 
index = np.array(np.arange(num_embs)) 
np.random.shuffle(index) 
batch_train_thres = 512  
final_thres = 0 
num_batch = round(num_embs/batch_train_thres)
x_t = [] 
y_t = [] 
for i in range(num_embs):
	x_t.append(x[index[i],:])
	y_t.append(y[index[i]])
# train thres 
for j in range(num_batch):
	embs = x_t[(j*batch_train_thres):((j+1)*batch_train_thres)] 
	labels = y_t[(j*batch_train_thres):((j+1)*batch_train_thres)] 
	thres = classifier.get_thres(embs, labels, path_SVM) 
	final_thres = final_thres + thres
	print(thres)  
final_thres = final_thres/num_batch
print(final_thres) 
# validating on thres subset
classifier.validate(x_t, y_t, final_thres, path_SVM)
# validating on test subset 
classifier.validate(test_embs, test_labels, final_thres, path_SVM)
# visualization 
if not os.path.exists(path_log):
	os.makedirs(path_log)
classifier.visualize(train_embs, train_labels, path_log)