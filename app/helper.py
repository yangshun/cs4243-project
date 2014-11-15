
MAX_FLOAT32_COORD = 1e11


def box_coord(a):
    if a > MAX_FLOAT32_COORD:
        return MAX_FLOAT32_COORD
    elif a < -MAX_FLOAT32_COORD:
        return -MAX_FLOAT32_COORD
    return a