
def lerp1(a, b, w):
    return (a * (1 - w)) + (b * w)


def lerp2(a, b, w):
    return [
        (a[0] * (1 - w)) + (b[0] * w),
        (a[1] * (1 - w)) + (b[1] * w)]


def lerp3(a, b, w):
    return [
        (a[0] * (1 - w)) + (b[0] * w),
        (a[1] * (1 - w)) + (b[1] * w),
        (a[2] * (1 - w)) + (b[2] * w)]


def lerp_nd(a, b, w):
    u = 1 - w

    def lerp1_w(x, y):
        return (x * u) + (y * w)
    return list(map(lerp1_w, a, b))
