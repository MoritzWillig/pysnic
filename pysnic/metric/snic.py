from ..ndim.norm_sqr import norm2_sqr, norm_nd_sqr_arr
from math import sqrt


def snic_distance_mod(pos_i, pos_j, col_i, col_j, si, mi):
    """
    Computes the SNIC pixel distance
    None of the components can be negative -> omitting the root does not change item order
    :param pos_i: position of pixel i
    :param pos_j: position of pixel j
    :param col_i: color of pixel i
    :param col_j: color of pixel j
    :param si: inverted spatial normalization factor = 1 / np.sqrt(num_pixels_in_image/num_super_pixels)
    :param mi: inverted (-> 1/x) user provided (color) compactness factor - higher -> more compact, poorer boundary adherence
    :return: distance value
    """

    pos_d = norm2_sqr(pos_j[0] - pos_i[0], pos_j[1] - pos_i[1]) * si
    col_d = norm_nd_sqr_arr(col_i, col_j) * mi
    distance = pos_d + col_d
    return distance


def create_augmented_snic_distance(image_size, number_of_superpixels, compactness):
    # compute normalization factors
    si = 1 / sqrt((image_size[0] * image_size[1]) / number_of_superpixels)
    mi = 1 / float(compactness)

    def snic_distance_augmented(pa, pb, ca, cb, ss=si, mm=mi):
        return snic_distance_mod(pa, pb, ca, cb, ss, mm)
    return snic_distance_augmented
