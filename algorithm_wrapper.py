#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------
import os
import cv2
import numpy as np
from glob import glob
from scipy.io import loadmat
from multiprocessing import Pool, cpu_count
from face_recognition import face_locations, face_encodings, compare_faces


#------------------------------------------------------------------------------
#	Class of Algorithm APIs
#------------------------------------------------------------------------------
class AlgorithmAPIs(object):
	"""
	This class contains algorithm APIs.

	Arguments:
		template_dir : (str) Path to the directory containing templates.
		threshold : (float) Threshold for comparing embeddings.
		use_multiprocessing : (bool) Use multi-processing or not?
	"""
	def __init__(self, template_dir="templates", threshold=0.5,
				use_multiprocessing=False):
		# Parameters
		super(AlgorithmAPIs, self).__init__()
		self.template_dir = template_dir
		self.threshold = threshold
		self.use_multiprocessing = use_multiprocessing

		# # Create folder to store templates
		# if not os.path.exists(self.template_dir):
		# 	os.mkdir(self.template_dir)
		# 	print("[AlgorithmAPIs]Create folder %s" % (self.template_dir))

		# Setup multiprocessing
		if self.use_multiprocessing:
			self.n_cpus = cpu_count()
			self.pools = Pool(processes=self.n_cpus)
			print("[AlgorithmAPIs]Create %d pools" % (self.n_cpus))
		else:
			self.pools = None


	def find_bbox(self, image):
		"""
		Find bounding box(es) of face(s) within an image.

		Arguments:
			image : (ndarray) RGB image with shape of [width, height, channel].

		Return:
			face_locs : (list) Coordinates of the bounding box as the following
						[(y_top, x_right, y_bottom, x_left)].
		"""
		face_locs = face_locations(image)
		return face_locs


	def draw_bbox(self, image, face_locs, color="blue"):
		"""
		Draw bounding box(es) into an image.

		Arguments:
			image : (ndarray) RGB image with shape of [width, height, channel].
			face_locs : (list) Coordinates of the bounding box.
			color : (str) Color of bounding box, including "red", "green", and
					"blue". Default color is "blue"

		Return:
			image_drawn : (ndarray) The image drawn bounding box.
			corner1 : (ndarray) Left-Top coordinates of the bounding box.
			corner2 : (ndarray) Right-Bottom coordinates of the bounding box.
		"""
		image_drawn = np.copy(image)
		corner1, corner2 = None, None
		n_bbox = len(face_locs)
		colors = {"red": (255, 0, 0), "green": (0, 255, 0), "blue": (0, 0, 255)}
		if n_bbox:
			corner1 = np.zeros([n_bbox, 2], dtype=int)
			corner2 = np.zeros([n_bbox, 2], dtype=int)
			for i, (y_top, x_right, y_bottom, x_left) in enumerate(face_locs):
				c1, c2 = (x_left, y_top), (x_right, y_bottom)
				corner1[i,:], corner2[i,:] = c1, c2
				cv2.rectangle(image_drawn, c1, c2, colors[color], 3)
		return image_drawn, corner1, corner2


	def extract_embedding(self, image, face_locs):
		"""
		Extract embedding(s) corresponding to face(s) inside an image.

		Arguments:
			image : (ndarray) RGB image with shape of [width, height, channel].
			face_locs : (list) Coordinates of the bounding box.

		Return:
			embeddings : (list) List of embedding(s).
			faces : (list) List of cropped face(s).
		"""
		embeddings = []
		faces = []
		if face_locs is not None:
			for face_loc in face_locs:
				y_top, x_right, y_bottom, x_left = face_loc
				face_cropped = image[y_top:y_bottom+1, x_left:x_right+1]
				embedding = face_encodings(face_cropped)
				faces.append(face_cropped)
				embeddings.append(embedding)
		return embeddings, faces


	def check_embedding_exist(self, embedding):
		"""
		Check whether an embedding existing in the store.

		Arguments:
			embedding : (ndarray) The input embedding.

		Return:
			is_existed : (bool) Boolean result.
		"""
		files = glob(os.path.join(self.template_dir, "*.*"))
		is_existed = False
		for file in files:
			db_embedding = loadmat(file)["embedding"]
			if compare_faces(embedding, db_embedding, self.threshold)[0]:
				is_existed = True
				break
		return is_existed


	def pool_matching(self, embedding):
		"""
		Pool function of matching process.

		Arguments:
			embedding : (ndarray) The input embedding.

		Return:
			matched : (bool) Whether the input embedding matched with another.
			name : (str) Name of the matched person.
			face_reg : (ndarray) Registerd face of the matched person.
		"""
		matched, name, face_reg = False, '', []
		files = glob(os.path.join(self.template_dir, "*.*"))
		for file in files:
			db_data = loadmat(file)
			db_name = db_data["name"][0]
			db_embedding = db_data["embedding"][0]
			db_face = db_data["face"]
			### ======> Need to be repaired, using minimum distance <====== ###
			if compare_faces(embedding, db_embedding, self.threshold)[0]:
				matched, name, face_reg = True, db_name, db_face
				break
		return matched, name, face_reg


	def matching(self, embeddings):
		"""
		Matching process including two options: multi-processing and single
		processing.

		Arguments:
			embeddings : (list) List of input embeddings.

		Return:
			results : (list) List of (matched, name, face_reg).
		"""
		# If using multiprocessing
		if self.use_multiprocessing and len(embeddings)>1:
			args = embeddings
			results = self.pools.starmap(self.pool_matching, args)
			return results

		# If not using multiprocessing
		else:
			results = []
			for embedding in embeddings:
				result = self.pool_matching(embedding)
				results.append(result)
			return results