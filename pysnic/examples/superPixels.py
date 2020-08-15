from pkg_resources import resource_stream
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import skimage.color
from skimage.segmentation import mark_boundaries
from timeit import default_timer as timer
from itertools import chain
from pysnic.algorithms.snic import snic, compute_grid
from pysnic.ndim.operations_collections import nd_computations
from pysnic.metric.snic import create_augmented_snic_distance

# load image
color_image = np.array(Image.open(resource_stream(__name__, "../data/orchid.jpg")))
number_of_pixels = color_image.shape[0] * color_image.shape[1]

# SNIC parameters
numSegments = 100
compactness = 10.0

# compute grid
grid = compute_grid(color_image.shape, numSegments)
seeds = list(chain.from_iterable(grid))
seed_len = len(seeds)

# choose a distance metric
distance_metric = create_augmented_snic_distance(color_image.shape, seed_len, compactness)


start = timer()

segmentation, distances, centroids = snic(
    skimage.color.rgb2lab(color_image).tolist(),
    seeds,
    compactness, nd_computations["3"], distance_metric,
    update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))

end = timer()
print("superpixelation took: %fs" % (end - start))

# show the output of SNIC
plt.figure("SNIC with %d segments" % len(centroids))
plt.imshow(mark_boundaries(color_image, np.array(segmentation)))
plt.show()

plt.figure("segmentations")
plt.imshow(segmentation, cmap="prism")
plt.show()

# show the distance map
plt.figure("Distances")
plt.imshow(distances, cmap="gray")
plt.show()
