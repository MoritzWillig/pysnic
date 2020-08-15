# 0 = RIGHT, 1 = TOP, 2 = LEFT, 3 = BOTTOM
vel = [
    (1, 0),
    (0, -1),
    (-1, 0),
    (0, 1)
]


def trace_edges(segmentation):
    """
    Traces segments, assumes a 4-connectivity between pixels.
    Pixel centers lie at [x.5, y.5], vertices are at [x.0, y.0].
    :param segmentation:
    :return:
    """

    edges = []

    height = len(segmentation)
    width = len(segmentation[0])
    widthp = width + 1
    heightp = height + 1

    lower_right_idx = ((height - 1 + 1) * widthp) + (-1 + 1)

    # end_points contains all unprocessed corner directions. The lower right
    # corner always has the directions right and top.
    end_points = dict()
    end_points[lower_right_idx] = [0]  # due to ccw border tracing, we leave out TOP direction
    queue = [lower_right_idx]

    while len(queue) != 0:
        while True:
            # get next corner and check remaining directions
            idx = queue[-1]
            directions = end_points[idx]

            l_dirs = len(directions)
            if l_dirs <= 1:
                idx = queue.pop()
            if l_dirs != 0:
                direction = directions.pop()
                break

        # compute starting coordinates
        px = (idx % widthp) - 1
        py = (idx // widthp) - 1

        line = [(px, py)]

        # adjust offset for position
        if direction == 0:  # RIGHT
            px += 1
        elif direction == 1:  # TOP
            pass
            #px += 1
        elif direction == 2:  # LEFT
            py += 1
        elif direction == 3:  # BOTTOM
            px += 1
            py += 1
        else:
            raise ValueError(f"Encountered invalid direction value ({direction})")

        is_inner_corner = False

        # follow line
        while True:
            # compute offset pixel position that we need for detecting corners
            vx, vy = vel[direction]

            if is_inner_corner:
                px += vx
                py += vy

            # pixel "in front"
            fr_x = px + vx
            fr_y = py + vy
            # pixel "to the right"
            perp_x = px - vy
            perp_y = py + vx

            # labels we expect
            flabel = segmentation[py][px]
            if perp_x < 0 or perp_x == width or perp_y < 0 or perp_y == height:
                plabel = -1
            else:
                plabel = segmentation[perp_y][perp_x]

            # follow direction until we encounter an inner or outer corner
            # inner corner = pixel to the right changes label
            # outer corner = pixel ahead changes label
            is_inner_corner = False
            if direction == 0:  # RIGHT
                while True:
                    # inner edge
                    if perp_y < height and segmentation[perp_y][perp_x] != plabel:
                        new_direction = 3
                        is_inner_corner = True
                        off_x, off_y = (-1, 0)
                        break
                    # outer edge
                    elif fr_x == width or segmentation[fr_y][fr_x] != flabel:
                        new_direction = 1
                        off_x, off_y = (0, 0)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 1:  # TOP
                while True:
                    # inner edge
                    if perp_x < width and segmentation[perp_y][perp_x] != plabel:
                        new_direction = 0
                        off_x, off_y = (0, 0)
                        is_inner_corner = True
                        break
                    # outer edge
                    elif fr_y < 0 or segmentation[fr_y][fr_x] != flabel:
                        new_direction = 2
                        off_x, off_y = (0, -1)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 2:  # LEFT
                while True:
                    # inner edge
                    if perp_y != -1 and segmentation[perp_y][perp_x] != plabel:
                        new_direction = 1
                        is_inner_corner = True
                        off_x, off_y = (0, -1) #!!
                        break
                    # outer edge
                    elif fr_x < 0 or segmentation[fr_y][fr_x] != flabel:
                        new_direction = 3
                        off_x, off_y = (-1, -1)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 3:  # BOTTOM
                while True:
                    # inner edge
                    if perp_x != -1 and segmentation[perp_y][perp_x] != plabel:
                        new_direction = 2
                        off_x, off_y = (-1, -1)
                        is_inner_corner = True
                        break
                    # outer edge
                    elif fr_y == height or segmentation[fr_y][fr_x] != flabel:
                        new_direction = 0
                        off_x, off_y = (-1, 0)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            else:
                raise ValueError(f"Encountered invalid direction value ({direction})")

            # add corner to line
            px = fr_x - vx
            py = fr_y - vy

            ex = px + off_x
            ey = py + off_y

            line.append((ex, ey))

            # If we end up at an image border, we have always encountered a vertex.
            # If we are at an position 'inside' the image we are either at a
            # vertex (3 or 4 edges) or the line just changes direction (2 edges).

            # To prevent extra checks during line tracing,
            # we remove clock-wise directions from positions at the image borders.
            # This way the pivot pixel always stays within the image.
            is_left_border = (ex == -1)
            is_right_border = (ex == width - 1)
            is_top_border = (ey == -1)
            is_bottom_border = (ey == height - 1)
            is_image_corner = (is_left_border or is_right_border) and (is_top_border or is_bottom_border)
            is_vertex = True
            if is_image_corner:
                if is_left_border:
                    if is_top_border:
                        directions = [3]
                    else:
                        directions = [0]
                else:
                    # right border
                    if is_top_border:
                        directions = [2]
                    else:
                        directions = [1]
            elif is_left_border:
                directions = [0, 3]
            elif is_right_border:
                directions = [1, 2]
            elif is_top_border:
                directions = [2, 3]
            elif is_bottom_border:
                directions = [0, 1]
            else:
                # image inside
                directions = get_vertex_directions_unsafe(ex, ey, segmentation)
                assert len(directions) != 0
                is_vertex = (len(directions) != 2)

            if is_vertex:
                edges.append(line)

                # check if end point is already known
                idx = ((ey + 1) * widthp) + (ex + 1)
                if idx not in end_points:
                    end_points[idx] = directions
                    queue.append(idx)
                else:
                    directions = end_points[idx]

                # remove the direction we came from
                # we need this pre check for border vertices, which
                # lack cw directions to ensure, ccw border tracing
                opp_dir = (direction + 2) % 4
                if opp_dir in directions:
                    directions.remove(opp_dir)
                break

            direction = new_direction

    vertices = dict()
    for edge in edges:
        vertices[edge[0]] = edge
        vertices[edge[-1]] = edge
    return vertices, edges


def trace_isles(vertices, seeds, segmentation):
    """
    Searches for undetected edges in the segmentation.

    When searching for edges with trace_edges, the algorithm starts at the image border.
    Segments that are however enclosed by another segment can not be reached via an edge and
    have to be searched separately.

    To avoid a full image search, we make use of the super-pixel seeds, which are
    known to always lie within the super-pixels.

    This is a simplified trace_edges that does not perform bounds checks,
    since we assume that all these areas have already been found by trace_edges

    :param vertices: list of vertices that already got discovered
    :param seeds: List of position that lie within each area
    :param segmentation: Image segmentation
    :return:
    """
    height = len(segmentation)
    width = len(segmentation[0])

    # find indices we did not capture
    seed_idcs = {segmentation[seed[1]][seed[0]]: i for i, seed in enumerate(seeds)}
    missing_seed_ids = set(range(len(seeds)))
    discovered_idcs = set([
        seed_idcs[idx]
        for px, py in vertices
        for idx in get_neighbourhood(px, py, width, height, segmentation)
        if idx != -1
        ])
    missing_seed_ids = missing_seed_ids.difference(discovered_idcs)

    graphs = []
    while len(missing_seed_ids) != 0:
        idx2 = missing_seed_ids.pop()
        px, py = seeds[idx2]
        idx = segmentation[py][px]

        # move upwards until we encounter a boundary
        while segmentation[py][px] == idx:
            py -= 1
        py += 1

        # move left, so that we start at a corner
        while True:
            if segmentation[py-1][px] == idx:
                # inner corner
                direction = 1
                py -= 1
                break
            if segmentation[py][px-1] != idx:
                direction = 3
                py -= 1
                px -= 1
                break
            px -= 1

        vertices, edges = trace_edges_unsafe(px, py, direction, segmentation)
        graphs.append((vertices, edges))

        discovered_idcs = set([
            seed_idcs[idx]
            for pxx, pyy in vertices
            for idx in get_neighbourhood_unsafe(pxx, pyy, segmentation)])
        missing_seed_ids = missing_seed_ids.difference(discovered_idcs)

    return graphs


def trace_edges_unsafe(ex, ey, direction, segmentation):
    """
    Traces segments, assumes a 4-connectivity between pixels.
    Pixel centers lie at [x.5, y.5], vertices are at [x.0, y.0].

    (px, py) must lie at a corner of an area boundary.
    Does not perform bounds checks
    :param segmentation:
    :return:
    """

    edges = []

    height = len(segmentation)
    width = len(segmentation[0])
    widthp = width + 1
    heightp = height + 1

    start_x = ex
    start_y = ey

    starting_idx = ((ey + 1) * widthp) + (ex + 1)

    # end_points contains all unprocessed corner directions. The lower right
    # corner always has the directions right and top.
    end_points = dict()
    end_points[starting_idx] = [direction]  # due to ccw border tracing, we leave out TOP direction
    queue = [starting_idx]

    while len(queue) != 0:
        while True:
            # get next corner and check remaining directions
            idx = queue[-1]
            directions = end_points[idx]

            l_dirs = len(directions)
            if l_dirs <= 1:
                idx = queue.pop()
            if l_dirs != 0:
                direction = directions.pop()
                break

        # compute starting coordinates
        px = (idx % widthp) - 1
        py = (idx // widthp) - 1

        line = [(px, py)]

        # adjust offset for position
        if direction == 0:  # RIGHT
            px += 1
        elif direction == 1:  # TOP
            pass
        elif direction == 2:  # LEFT
            py += 1
        elif direction == 3:  # BOTTOM
            px += 1
            py += 1
        else:
            raise ValueError(f"Encountered invalid direction value ({direction})")

        is_inner_corner = False

        # follow line
        while True:
            # compute offset pixel position that we need for detecting corners
            vx, vy = vel[direction]

            if is_inner_corner:
                px += vx
                py += vy

            # pixel "in front"
            fr_x = px + vx
            fr_y = py + vy
            # pixel "to the right"
            perp_x = px - vy
            perp_y = py + vx

            # labels we expect
            flabel = segmentation[py][px]
            plabel = segmentation[perp_y][perp_x]

            # follow direction until we encounter an inner or outer corner
            # inner corner = pixel to the right changes label
            # outer corner = pixel ahead changes label
            is_inner_corner = False
            if direction == 0:  # RIGHT
                while True:
                    # inner edge
                    if segmentation[perp_y][perp_x] != plabel:
                        new_direction = 3
                        is_inner_corner = True
                        off_x, off_y = (-1, 0)
                        break
                    # outer edge
                    elif segmentation[fr_y][fr_x] != flabel:
                        new_direction = 1
                        off_x, off_y = (0, 0)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 1:  # TOP
                while True:
                    # inner edge
                    if segmentation[perp_y][perp_x] != plabel:
                        new_direction = 0
                        off_x, off_y = (0, 0)
                        is_inner_corner = True
                        break
                    # outer edge
                    elif segmentation[fr_y][fr_x] != flabel:
                        new_direction = 2
                        off_x, off_y = (0, -1)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 2:  # LEFT
                while True:
                    # inner edge
                    if segmentation[perp_y][perp_x] != plabel:
                        new_direction = 1
                        is_inner_corner = True
                        off_x, off_y = (0, -1) #!!
                        break
                    # outer edge
                    elif segmentation[fr_y][fr_x] != flabel:
                        new_direction = 3
                        off_x, off_y = (-1, -1)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            elif direction == 3:  # BOTTOM
                while True:
                    # inner edge
                    if segmentation[perp_y][perp_x] != plabel:
                        new_direction = 2
                        off_x, off_y = (-1, -1)
                        is_inner_corner = True
                        break
                    # outer edge
                    elif segmentation[fr_y][fr_x] != flabel:
                        new_direction = 0
                        off_x, off_y = (-1, 0)
                        break

                    fr_x += vx
                    fr_y += vy
                    perp_x += vx
                    perp_y += vy
            else:
                raise ValueError(f"Encountered invalid direction value ({direction})")

            # add corner to line
            px = fr_x - vx
            py = fr_y - vy

            ex = px + off_x
            ey = py + off_y

            line.append((ex, ey))

            # image inside
            directions = get_vertex_directions_unsafe(ex, ey, segmentation)
            assert len(directions) != 0
            is_vertex = (len(directions) != 2)
            is_starting_point = (ex == start_x) and (ey == start_y)
            if is_vertex or is_starting_point:
                edges.append(line)

                # check if end point is already known
                idx = ((ey + 1) * widthp) + (ex + 1)
                if idx not in end_points:
                    end_points[idx] = directions
                    queue.append(idx)
                else:
                    directions = end_points[idx]

                # remove the direction we came from
                # we need this pre check for border vertices, which
                # lack cw directions to ensure, ccw border tracing
                opp_dir = (direction + 2) % 4
                if opp_dir in directions:
                    directions.remove(opp_dir)
                break

            direction = new_direction

    vertices = dict()
    for edge in edges:
        vertices[edge[0]] = edge
        vertices[edge[-1]] = edge
    return vertices, edges


def polygonize(segmentation, seeds, curve_simplification=None):
    vertices, edges = trace_edges(segmentation)
    graphs = trace_isles(vertices, seeds, segmentation)
    graphs.append((vertices, edges))

    if curve_simplification is not None:
        for i, graph in enumerate(graphs):
            graphs[i] = (graph[0], [curve_simplification(edge) for edge in graph[1]])
    return graphs


def get_neighbourhood(px, py, width, height, segmentation):
    # [top_left, top_right, bottom_left, bottom_right]
    neighbourhood = [-1, -1, -1, -1]
    if py == -1:
        # top border
        if px == -1:
            # top left corner
            neighbourhood[3] = segmentation[py + 1][px + 1]
        else:
            if px == width - 1:
                # top right corner
                neighbourhood[2] = segmentation[py + 1][px]
            else:
                # top 'center' border
                neighbourhood[2] = segmentation[py + 1][px]
                neighbourhood[3] = segmentation[py + 1][px + 1]
    else:
        # below top border
        if py == height - 1:
            # bottom border
            if px == -1:
                # bottom left corner
                neighbourhood[1] = segmentation[py][px + 1]
            else:
                if px == width - 1:
                    # bottom right corner
                    neighbourhood[0] = segmentation[py][px]
                else:
                    # bottom 'center' border
                    neighbourhood[0] = segmentation[py][px]
                    neighbourhood[1] = segmentation[py][px + 1]
        else:
            # between top and bottom border
            if px == -1:
                # left "middle" border
                neighbourhood[1] = segmentation[py][px + 1]
                neighbourhood[3] = segmentation[py + 1][px + 1]
                pass
            else:
                if px == width - 1:
                    # right "middle" border
                    neighbourhood[0] = segmentation[py][px]
                    neighbourhood[2] = segmentation[py + 1][px]
                else:
                    # inside
                    neighbourhood[0] = segmentation[py][px]
                    neighbourhood[1] = segmentation[py][px + 1]
                    neighbourhood[2] = segmentation[py + 1][px]
                    neighbourhood[3] = segmentation[py + 1][px + 1]
    return neighbourhood


def get_neighbourhood_unsafe(px, py, segmentation):
    return [
        segmentation[py][px],
        segmentation[py][px + 1],
        segmentation[py + 1][px],
        segmentation[py + 1][px + 1]
    ]


def get_vertex_directions(px, py, width, height, segmentation):
    neighbourhood = get_neighbourhood(px, py, width, height, segmentation)

    directions = []
    if neighbourhood[1] != neighbourhood[3]:
        directions.append(0)
    if neighbourhood[0] != neighbourhood[1]:
        directions.append(1)
    if neighbourhood[0] != neighbourhood[2]:
        directions.append(2)
    if neighbourhood[2] != neighbourhood[3]:
        directions.append(3)

    return directions


def get_vertex_directions_unsafe(px, py, segmentation):
    """
    Checks edges around a pixel position.
    Does not perform bound checks!
    :param px:
    :param py:
    :param segmentation:
    :return:
    """
    neighbourhood = get_neighbourhood_unsafe(px, py, segmentation)

    directions = []
    if neighbourhood[1] != neighbourhood[3]:
        directions.append(0)
    if neighbourhood[0] != neighbourhood[1]:
        directions.append(1)
    if neighbourhood[0] != neighbourhood[2]:
        directions.append(2)
    if neighbourhood[2] != neighbourhood[3]:
        directions.append(3)

    return directions
