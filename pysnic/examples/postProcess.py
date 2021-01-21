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
target_number_of_segments = 100
compactness = 10.00


segmentation, _, centroids = snic(
    lab_image, target_number_of_segments, compactness,
    update_func=lambda num_pixels: print("processed %05.2f%%" % (num_pixels * 100 / number_of_pixels)))
actual_number_of_segments = len(centroids)

# show the output of SNIC
fig = plt.figure("SNIC with %d segments" % actual_number_of_segments)
plt.imshow(mark_boundaries(color_image, np.array(segmentation)))
plt.show()

# to numpy: segmentation.shape = (400, 600, 3)
segmentation = np.array(segmentation)

# create segment masks
segment_masks = [segmentation == segment_idx for segment_idx in range(actual_number_of_segments)]
# select pixels per segment. [number_of_segments](n, 3) [n=number of pixels per segment]
segment_vectors = [color_image[segment_masks[segment_idx], :] for segment_idx in range(actual_number_of_segments)]

# post-process the individual segment vectors (N, 3)
post_image = np.empty_like(color_image)
for segment_idx in range(actual_number_of_segments):
    average = np.mean(segment_vectors[segment_idx], 0)

    print(f"Segment {segment_idx} average: {average}")
    post_image[segment_masks[segment_idx], :] = average

fig = plt.figure("Post-processed image")
plt.imshow(post_image)
plt.show()
