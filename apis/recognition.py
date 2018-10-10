#----------------------------------------------------------------------------------------------
# Import 
#----------------------------------------------------------------------------------------------
from .lib import facenet
import tensorflow as tf 
import pickle
from scipy import misc
import os 
import cv2 
import numpy as np 


#----------------------------------------------------------------------------------------------
# Main  
#----------------------------------------------------------------------------------------------
class Recognizer:
	def create_graph(self, path_pretrained, path_SVM):
		# load FaceNet model as extractor 
		facenet.load_model(path_pretrained) 
		self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
		self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
		self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
		embedding_size = self.embeddings.get_shape()[1]
		self.emb_array = np.zeros((1, embedding_size))
		if (tf.test.is_gpu_available()):
			config = tf.ConfigProto()
			config.gpu_options.allow_growth = True
			self.session = tf.Session(config=config)
		else:
			self.sess = tf.Session()
		# load SVM model 
		classifier_filename = path_SVM
		classifier_filename_exp = os.path.expanduser(classifier_filename)
		with open(classifier_filename_exp, 'rb') as infile:
			(self.model, self.class_names) = pickle.load(infile)


	def recognize(self, frame, face_location, thres):
		"""
		Arguments:
			image : (ndarray) RGB image with shape of [width, height, channel].
			face_loc : (list) Coordinates of a bounding box of the format
			(y_top, x_left, width, height).
		Return:
			student_id : (str) Student id of the recognized person.
		"""
		y_left_top = face_location[0] 
		x_left_top = face_location[1] 
		height = face_location[3] 
		width = face_location[2] 
		cropped = []
		scaled = []
		scaled_reshape = []
		cropped.append(frame[y_left_top:(y_left_top + height), x_left_top:(x_left_top + width), :])
		cropped[0] = facenet.flip(cropped[0], False) 
		scaled.append(misc.imresize(cropped[0], (182, 182), interp='bilinear'))
		scaled[0] = cv2.resize(scaled[0], (160, 160), interpolation=cv2.INTER_CUBIC)
		scaled[0] = facenet.prewhiten(scaled[0])
		scaled_reshape.append(scaled[0].reshape(-1, 160, 160,3)) 
		# feed forward 
		feed_dict = {self.images_placeholder: scaled_reshape[0], self.phase_train_placeholder: False}
		self.emb_array[0, :] = self.sess.run(self.embeddings, feed_dict=feed_dict)
		predictions = self.model.predict_proba(self.emb_array)
		best_class_indices = np.argmax(predictions, axis=1) 
		best_class_probabilities = predictions[0, best_class_indices]  
		if best_class_probabilities < thres:
			result_name = "unknown" 
		else:
			result_name = self.dataset[best_class_indices[0]].name 
		return result_name, best_class_probabilities


#----------------------------------------------------------------------------------------------
# Test 
#----------------------------------------------------------------------------------------------
# path_pretrained = "apis/models/facenet/20180402-114759.pb"
# path_SVM = "apis/models/SVM/SVM.pkl"
# recognizer = Recognizer() 
# recognizer.create_graph(path_pretrained, path_SVM) 


# frame = cv2.imread("/home/thiendt/Documents/BK_documents/AI/Face-Attendance-System/dataset/test/unknown/Abdullah_Gul_0013.png") 
# frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# id = recognizer.recognize(frame, (0,0,182,182), 0.29) 
# print(id) 