import sys
import heapq

from pysnic.helpers.grid import compute_grid
from ..ndim.operations_collections import nd_computations
from ..ndim.lerp import lerp2
from ..metric.snic import create_augmented_snic_distance


class Queue(object):
    def __init__(self, _buffer_size=0):
        # TODO we perform a lot of single insertions
        # it would be more efficient to use a cache class that already contains a buffer of the maximum  heap size
        # But since heapq is implemented in C, a custom python implementation will probably be slower
        self.heap = []
        self._sub_idx = 0

    def add(self, priority, value):
        heapq.heappush(self.heap, (priority, self._sub_idx, value))
        self._sub_idx += 1

    def is_empty(self):
        return len(self.heap) == 0

    def pop_value(self):
        return heapq.heappop(self.heap)[2]

    def pop(self):
        return heapq.heappop(self.heap)

    def length(self):
        return len(self.heap)


def get_4_neighbourhood_1(pos, image_size):
    # outputs candidates 1 pixel away from the image border.
    # this way we can use interp2d_lin_unsafe instead and safe costly boundary checks
    n = 0
    neighbourhood = [None, None, None, None]

    x = pos[0]
    y = pos[1]

    if x - 1 >= 0:
        neighbourhood[0] = [x - 1, y]
        n += 1

    if y - 1 >= 0:
        neighbourhood[n] = [x, y - 1]
        n += 1

    if x + 1 < image_size[1]:
        neighbourhood[n] = [x + 1, y]
        n += 1

    if y + 1 < image_size[0]:
        neighbourhood[n] = [x, y + 1]
        n += 1

    return neighbourhood, n


def snic(
        image,
        seeds,
        compactness,
        nd_computation=None,
        image_distance=None,
        update_func=None):
    """
    Computes a superpixelation from a given image.

    > author = {Achanta, Radhakrishna and Susstrunk, Sabine}
    > title = {Superpixels and Polygons using Simple Non-Iterative Clustering}
    > booktitle = {IEEE Conference on Computer Vision and Pattern Recognition (CVPR)}
    > year = {2017}

    -> https://ivrl.epfl.ch/research/snic_superpixels


    Added a few changes to improve performance:
    - removed normalization factors from metric (-> returned distance map has to be scaled by a constant factor)
    - added a distance map
      - this allows prechecking, if another candidate is already registered to a pixel with a smaller distance

    :param image: cielab image (as python list - no numpy! use to .tolist()). Choose a corresponding nd_computations for other image formats
    :param seeds: expected number of super pixels [int] or a iterable containing seeds
    :param compactness: compactness parameter (inverse color weight)
    :param nd_computation: NdComputations instance for interpolating and computing ndim distances in the image
    :param image_distance: function (int[2], int[2], color[n], color[n]) for computing a distance metric in the image
    :param update_func: optional function (percentage: float) which can be used to monitor progress
    :return: labeled image, distance map, centroids [position, average color, index]
    """
    image_size = [len(image), len(image[0])]
    label_map = [[-1] * image_size[1] for _ in range(image_size[0])]
    distance_map = [[sys.float_info.max] * image_size[1] for _ in range(image_size[0])]

    if nd_computation is None:
        nd_computation = nd_computations["nd"]
    lerp = nd_computation.lerp

    if type(seeds) is int:
        # generate  grid and flatten it into a list
        seeds = [seed for row in compute_grid(image_size, seeds) for seed in row]

        number_of_superpixels = len(seeds)
    else:
        # assume seeds is an iterable
        number_of_superpixels = len(seeds)

    if image_distance is None:
        image_distance = create_augmented_snic_distance(image_size, number_of_superpixels, compactness)

    # create centroids
    centroids = [[pos, image[pos[1]][pos[0]], 0] for pos in seeds]  # [position, avg color, #pixels]

    # create priority queue
    queue = Queue(image_size[0] * image_size[1] * 4)  # [position, color, centroid_idx]
    q_add = queue.add  # cache some functions
    q_pop = queue.pop
    # we create a priority queue and fill with the centroids itself. Since the python priority queue can not
    # handle multiple entries with the same key, we start inserting the super pixel seeds with negative values. This
    # makes sure they get processed before any other pixels. Since distances can not be negative, all new
    # pixels will have a positive value, and therefore will be handled only after all seeds have been processed.
    for k in range(number_of_superpixels):
        init_centroid = centroids[k]

        q_len = -queue.length()
        q_add(q_len, [init_centroid[0], init_centroid[1], k])
        distance_map[init_centroid[0][1]][init_centroid[0][0]] = q_len

    # classification
    classified_pixels = 0
    # while not q_empty(): -> replaced with "try: while True:" to speed-up code (~1sec with 50k iterations)
    try:
        while True:
            # get pixel that has the currently smallest distance to a centroid
            item = q_pop()
            candidate_distance = item[0]
            candidate = item[2]
            candidate_pos = candidate[0]

            # test if pixel is not already labeled
            # if label_map[candidate_pos[1] * im_width + candidate_pos[0]] == -1:
            if label_map[candidate_pos[1]][candidate_pos[0]] == -1:
                centroid_idx = candidate[2]

                # label new pixel
                label_map[candidate_pos[1]][candidate_pos[0]] = centroid_idx
                #
                distance_map[candidate_pos[1]][candidate_pos[0]] = candidate_distance
                # label_map[candidate_pos[1] * im_width + candidate_pos[0]] = centroid_idx
                classified_pixels += 1

                # online update of centroid
                centroid = centroids[centroid_idx]
                num_pixels = centroid[2] + 1
                lerp_ratio = 1 / num_pixels

                # adjust centroid position
                centroid[0] = lerp2(centroid[0], candidate_pos, lerp_ratio)
                # update centroid color
                centroid[1] = lerp(centroid[1], candidate[1], lerp_ratio)
                # adjust number of pixels counted towards this super pixel
                centroid[2] = num_pixels

                # add new candidates to queue
                neighbours, neighbour_num = get_4_neighbourhood_1(candidate_pos, image_size)
                for i in range(neighbour_num):
                    neighbour_pos = neighbours[i]
                    # Check if neighbour is already labeled, as these pixels would get discarded later on.
                    # We filter them here as queue insertions are expensive
                    npx = neighbour_pos[0]
                    npy = neighbour_pos[1]
                    # if label_map[neighbour_pos[1] * im_width + neighbour_pos[0]] == -1:
                    if label_map[npy][npx] == -1:
                        neighbour_color = image[npy][npx]
                        neighbour = [neighbour_pos, neighbour_color, centroid_idx]

                        distance = image_distance(neighbour_pos, centroid[0], neighbour_color, centroid[1])

                        # test if another candidate with a lower distance, is not already
                        # registered to this pixel
                        if distance_map[npy][npx] >= distance:
                            distance_map[npy][npx] = distance
                            q_add(distance, neighbour)

                # status update
                if (update_func is not None) and (classified_pixels % 10000 == 0):
                    update_func(classified_pixels)
    except IndexError:
        pass

    # do a 100% status update (if we haven't done it already in the last iteration)
    if (update_func is not None) and (classified_pixels % 10000 != 0):
        update_func(classified_pixels)

    return label_map, distance_map, centroids
