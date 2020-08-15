from math import sqrt


def get_segment_distance(begin, end, point):
    """
    Computes the closest distance between the line segment (begin, end) and a given point.
    :param begin: Start of the line segment.
    :type begin: [float, float]
    :param end: End of the line segment.
    :type end: [float, float]
    :param point: Position to measure the distance to.
    :type point: [float, float]
    :return: Closest distance between the point and the line segment.
    """
    ex = end[0] - begin[0]
    ey = end[1] - begin[1]
    px = point[0] - begin[0]
    py = point[1] - begin[1]

    # project point onto line
    norm = (ex**2 + ey**2)
    # If the normalization value is zero: begin == end
    # In this case we compute the point-point distance
    if norm < 1e-10:
        return sqrt(px**2 + py**2)
    t = ((px * ex) + (py * ey)) / norm

    if t <= 0:
        # nearest point is at the start
        return sqrt(px**2 + py**2)
    if t >= 1:
        # nearest point is at the start
        return sqrt((px - ex)**2 + (py - ey)**2)

    ix = t * ex
    iy = t * ey
    return sqrt((px - ix)**2 + (py - iy)**2)


class RamerDouglasPeucker:

    def __init__(self, epsilon):
        self.epsilon = epsilon

    def __call__(self, line):
        if len(line) == 2:
            return line.copy()

        begin = line[0]
        end = line[-1]

        max_dist = -1
        max_i = -1
        for i, position in enumerate(line[1:-1]):
            distance = get_segment_distance(begin, end, position)

            if distance > max_dist:
                max_dist = distance
                max_i = i
        max_i += 1

        if max_dist < self.epsilon:
            resulting = [line[0], line[-1]]
        else:
            resulting = self(line[:max_i+1])
            resulting.pop()  # both lines contain the splitting vertex
            resulting.extend(self(line[max_i:]))
        return resulting
