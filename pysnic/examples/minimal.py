from pkg_resources import resource_stream
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import skimage.color
from skimage.segmentation import mark_boundaries
from pysnic.algorithms.snic import snic


# load image
color_image = np.array(Image.open(resource_stream(__name__, "../data/orchid.jpg")))
lab_image = skimage.color.rgb2lab(color_image).tolist()
number_of_pixels = color_image.shape[0] * color_image.shape[1]

# SNIC parameters
number_of_segments = 100
compactness = 10.00


segmentation, _, number_of_segments = snic(
    lab_image, number_of_segments, compactness,
    update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))

# show the output of SNIC
fig = plt.figure("SNIC with %d segments" % number_of_segments)
plt.imshow(mark_boundaries(color_image, np.array(segmentation)))
plt.show()
