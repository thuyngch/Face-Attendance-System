#------------------------------------------------------------------------------
#	Libraries
#------------------------------------------------------------------------------
import os
import numpy as np
from PIL import Image
from scipy.io import savemat
from matplotlib import pyplot as plt
from algorithm_wrapper import AlgorithmAPIs


#------------------------------------------------------------------------------
#	Create an APIs instance
#------------------------------------------------------------------------------
API = AlgorithmAPIs(template_dir="templates",
					threshold=0.5,
					use_multiprocessing=True)


#------------------------------------------------------------------------------
#	Registration section
#------------------------------------------------------------------------------
# Load image
PIL_obj = Image.open("images/putin/putin1.jpg")
img = np.array(PIL_obj)

# Bounding box
face_locs = API.find_bbox(img)
img_draw_bbox, _, _ = API.draw_bbox(img, face_locs, color="green")

# Extract embedding
embeddings, faces = API.extract_embedding(img, face_locs)
n_embeddings = len(embeddings)
print("Number of embeddings: %d" % (n_embeddings))

# Save template
template = {
	"name": "putin",
	"embedding": embeddings[0],
	"face": faces[0]
}
savemat(os.path.join(API.template_dir, "putin.mat"), template)
plt.figure(1)
plt.imshow(faces[0])
plt.axis('off')
plt.title("Registration face")
plt.show()


#------------------------------------------------------------------------------
#	Identification section
#------------------------------------------------------------------------------
# Load image
PIL_obj = Image.open("images/putin/putin2.jpg")
img = np.array(PIL_obj)

# Bounding box
face_locs = API.find_bbox(img)
img_draw_bbox, _, _ = API.draw_bbox(img, face_locs, color="green")

# Extract embedding
embeddings, faces = API.extract_embedding(img, face_locs)
n_embeddings = len(embeddings)
print("Number of embeddings: %d" % (n_embeddings))

# Identify person
results = API.matching(embeddings)
matched, name, face_reg = results[0]
print("Identified name: %s" % (name))
if name!="":
	plt.figure(1)
	plt.subplot(1,2,1); plt.title("Input image"); plt.axis('off')
	plt.imshow(img_draw_bbox)
	plt.subplot(1,2,2); plt.title("Registration face"); plt.axis('off')
	plt.imshow(face_reg)
	plt.show()