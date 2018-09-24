#----------------------------------------------------------------------------------------------
# Import 
#----------------------------------------------------------------------------------------------
import tensorflow as tf
import numpy as np
from scipy import misc
import API.lib.facenet as facenet
import API.lib.detect_face as detect_face
import os
import pickle 
import alignment 
import cv2 

#----------------------------------------------------------------------------------------------
# Main 
#----------------------------------------------------------------------------------------------
class face_recognition:
	def create_graph(self, path_mtcnn, path_pretrained, path_SVM): 
		# create graph for face detection 
		aligner = alignment.face_alignment() 
		aligner.create_mtcnn_graph(path_mtcnn) 
		self.minsize = aligner.minsize
		self.pnet = aligner.pnet 
		self.rnet = aligner.rnet 
		self.onet = aligner.onet 
		self.threshold = aligner.threshold
		self.factor = aligner.factor
		self.image_size = aligner.image_size 
		# load FaceNet model as extractor 
		facenet.load_model(path_pretrained) 
		self.images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
		self.embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
		self.phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")
		self.embedding_size = self.embeddings.get_shape()[1]
		# load SVM model 
		classifier_filename = path_SVM
		self.classifier_filename_exp = os.path.expanduser(classifier_filename)
		self.sess = tf.Session() 

	def recognize(self):
		HumanNames = ["1", "2"]
		with open(self.classifier_filename_exp, 'rb') as infile:
			(model, class_names) = pickle.load(infile)
		camera = cv2.VideoCapture(0) 
		print("Recognition") 
		while True:
			ret, frame = camera.read() 
			if not ret:
				continue 
			if frame.ndim == 2:
				frame = facenet.to_rgb(frame)
			frame = frame[:, :, 0:3]
			bounding_boxes, _ = detect_face.detect_face(frame, self.minsize, self.pnet, self.rnet, self.onet, self.threshold, self.factor)
			nrof_faces = bounding_boxes.shape[0]
			if nrof_faces > 0:
				det = bounding_boxes[:, 0:4]
				img_size = np.asarray(frame.shape)[0:2]
				cropped = []
				scaled = []
				scaled_reshape = []
				bb = np.zeros((nrof_faces,4), dtype=np.int32)
				for i in range(nrof_faces):
					emb_array = np.zeros((1, self.embedding_size))
					bb[i][0] = det[i][0]
					bb[i][1] = det[i][1]
					bb[i][2] = det[i][2]
					bb[i][3] = det[i][3]
					# inner exception 
					if bb[i][0] <= 0 or bb[i][1] <= 0 or bb[i][2] >= len(frame[0]) or bb[i][3] >= len(frame):
						print('face is inner of range!')
						continue
					# crop face region
					cropped.append(frame[bb[i][1]:bb[i][3], bb[i][0]:bb[i][2], :])
					cropped[0] = facenet.flip(cropped[0], False)
					scaled.append(misc.imresize(cropped[0], (self.image_size, self.image_size), interp='bilinear'))
					scaled[0] = cv2.resize(scaled[0], (160, 160), interpolation=cv2.INTER_CUBIC)
					scaled[0] = facenet.prewhiten(scaled[0])
					scaled_reshape.append(scaled[0].reshape(-1, 160, 160,3))
					feed_dict = {self.images_placeholder: scaled_reshape[0], self.phase_train_placeholder: False}
					emb_array[0, :] = self.sess.run(self.embeddings, feed_dict=feed_dict)
					predictions = model.predict_proba(emb_array)
					best_class_indices = np.argmax(predictions, axis=1)
					best_class_probabilities = predictions[np.arange(len(best_class_indices)), best_class_indices]
					cv2.rectangle(frame, (bb[i][0], bb[i][1]), (bb[i][2], bb[i][3]), (0, 255, 0), 2)    
					#plot result idx under box
					text_x = bb[i][0]
					text_y = bb[i][3] + 20
                    # print('result: ', best_class_indices[0])
					for H_i in HumanNames:
						if HumanNames[best_class_indices[0]] == H_i:
							result_names = HumanNames[best_class_indices[0]]
							cv2.putText(frame, result_names, (text_x, text_y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 
								1, (255, 0, 0), thickness=1, lineType=2)
			else:
				print('Unable to align')
			cv2.imshow('Video', frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
		camera.release() 
		cv2.destroyAllWindows() 

# a = face_recognition()
# a.create_graph("pretrained_models/mtcnn", "pretrained_models/20180402-114759/20180402-114759.pb", "pretrained_models/SVM/SVM.pkl")
# a.recognize() 