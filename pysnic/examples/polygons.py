from itertools import chain

from pkg_resources import resource_stream
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np
import skimage.color
from skimage.segmentation import mark_boundaries

from pysnic.algorithms.ramerDouglasPeucker import RamerDouglasPeucker
from pysnic.algorithms.snic import snic, compute_grid
from pysnic.algorithms.polygonize import polygonize


# load image
color_image = np.array(Image.open(resource_stream(__name__, "../data/orchid.jpg")))
lab_image = skimage.color.rgb2lab(color_image)
number_of_pixels = color_image.shape[0] * color_image.shape[1]

# SNIC parameters
number_of_segments = 100
compactness = 10.00

# compute grid
grid = compute_grid(color_image.shape, number_of_segments)
seeds = list(chain.from_iterable(grid))

segmentation, _, centroids = snic(
    lab_image.tolist(), seeds, compactness,
    update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))

rdp = RamerDouglasPeucker(5)
graphs = polygonize(segmentation, seeds, rdp)

for vertices, edges in graphs:
    fig = plt.figure("SNIC with %d segments" % len(centroids))
    plt.imshow(mark_boundaries(color_image, np.array(segmentation)))
    for x,y in vertices.keys():
        plt.scatter(x + 0.5, y + 0.5)
    for edge in edges:
        plt.plot([p[0] + 0.5 for p in edge], [p[1] + 0.5 for p in edge])
plt.show()
