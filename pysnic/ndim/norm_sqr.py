
def norm2_sqr_arr(a, b):
    x = a[0] - b[0]
    return x * x


def norm2_sqr(x, y):
    """
    Squared 2-norm for 2d vectors
    :param x:
    :param y:
    :return:
    """
    return (x * x) + (y * y)


def norm1_sqr_arr(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    return (x * x) + (y * y)


def norm3_sqr(x, y, z):
    """
    Squared 2-norm for 3d vectors
    :param x:
    :param y:
    :param z:
    :return:
    """
    return (x * x) + (y * y) + (z * z)


def norm3_sqr_arr(a, b):
    x = a[0] - b[0]
    y = a[1] - b[1]
    z = a[2] - b[2]
    return (x * x) + (y * y) + (z * z)


def norm_nd_sqr_arr(a, b):
    def sub_sqr(x, y):
        d = x - y
        return d * d
    return sum(map(sub_sqr, a, b))
