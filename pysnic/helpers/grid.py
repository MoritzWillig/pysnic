from math import sqrt


def compute_grid(image_size, number_of_pixels):
    """

    :param image_size: [row, cols]
    :param number_of_pixels:
    :return:
    """
    image_size_y = float(image_size[0])
    image_size_x = float(image_size[1])

    # compute grid size
    image_ratio = image_size_x / image_size_y
    num_sqr = sqrt(number_of_pixels)

    grid_size = [int(max(1.0, num_sqr * image_ratio) + 1), int(max(1.0, num_sqr / image_ratio) + 1)]

    # create grid
    full_step = [image_size_x / float(grid_size[0]), image_size_y / float(grid_size[1])]
    half_step = [full_step[0] / 2.0, full_step[1] / 2.0]
    grid = [[[
        int(half_step[0] + x * full_step[0]),
        int(half_step[1] + y * full_step[1])
    ] for x in range(grid_size[0])] for y in range(grid_size[1])]
    return grid
