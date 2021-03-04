import numpy as np
import time
from tetrominoes import rotate, tetrominoes
from copy import copy, deepcopy
from statistics import stdev


def get_candidates(matrix):
    candidates = []
    for i in range(22):
        for j in range(10):
            if matrix[(i, j)] is None:
                if i == 21:
                    candidates.append((i, j))
                    continue
                if i != 21 and matrix[(i + 1, j)] is not None:
                    candidates.append((i, j))
                    continue
                if i != 0 and matrix[(i - 1, j)] is not None:
                    candidates.append((i, j))
                    continue
                if j != 9 and matrix[(i, j + 1)] is not None:
                    candidates.append((i, j))
                    continue
                if j != 0 and matrix[(i, j - 1)] is not None:
                    candidates.append((i, j))
                    continue
    return candidates


def get_piece_arrays(tetromino):
    arr = []
    for i in range(4):
        current = []
        for j in range(len(tetromino)):
            for k in range(len(tetromino[j])):
                if tetromino[j][k] == "X":
                    current.append([j, k])
        for j in range(len(current)):
            y, x = current[j]
            cpy = deepcopy(current)
            for k in range(len(cpy)):
                cpy[k][0] -= y
                cpy[k][1] -= x
            arr.append(cpy)
        tetromino = rotate(tetromino)
    return arr

# TODO calc holes using dynamic programming
# go from rows bottom to top and from columns left and right to middle
# hole(r, c) = (hole(r - 1, c) or filled(r - 1, c)) and (hole(r, c - 1) or filled(r, c - 1)) and (hole(r, c + 1) or filled(r, c + 1))
# OR: only holes are in type 1 twice and type 2 or if on the rim type 1 once and type 2


"https://www.diva-portal.org/smash/get/diva2:815662/FULLTEXT01.pdf"
def score_board(matrix):
    heights = []
    for x in range(10):
        broken = False
        for y in range(22):
            if matrix[(y, x)] is not None:
                heights.append(22 - y)
                broken = True
                break
        if not broken:
            heights.append(0)
    type_1_holes = []
    type_2_holes = []
    #type_1_weight = lambda x : 1
    #type_2_weight = lambda x : 200
    type_1_weight = lambda x : 0
    type_2_weight = lambda x : 50
    for r in range(-(max(heights) - 22), 22):
        for c in range(10):
            if matrix[(r, c)] is None:
                if c != 0 and heights[c - 1] >= 22 - r:
                    type_1_holes.append(22 - r)
                if c != 9 and heights[c + 1] >= 22 - r:
                    type_1_holes.append(22 - r)
                if heights[c] > 22 - r:
                    type_2_holes.append(22 - r)
    sum = 0
    for i in type_1_holes:
        sum += type_1_weight(i)
    for i in type_2_holes:
        sum += type_2_weight(i)
    return sum + height_diff(heights)

"""
def score_board(matrix):
    max_height = -10000
    for r in range(22):
        for c in range(10):
            if matrix[(r, c)] is not None:
                max_height = max(max_height, 22 - r)
    return max_height
"""
def get_move(game):
    candidates = get_candidates(game.matrix)
    piece_arrays = get_piece_arrays(game.current_tetromino.shape)
    best_piece = None
    best_score = 999999999
    for candidate in candidates:
        for piece_array in piece_arrays:
            piece = [[sq[0] + candidate[0], sq[1] + candidate[1]] for sq in piece_array]
            if can_put(piece, game.matrix):
                m = copy(game.matrix)
                for sq in piece:
                    m[(sq[0], sq[1])] = 1
                remove_rows(m)
                score = score_board(m)
                if score < best_score:
                    best_piece = piece
                    best_score = score
    for sq in best_piece:
        game.matrix[(sq[0], sq[1])] = ("block", game.tetromino_block)
        game.remove_lines()
        game.set_tetrominoes()


def remove_rows(matrix):
    for r in range(22):
        broken = False
        for c in range(10):
            if matrix[(r, c)] is None:
                broken = True
                break
        if not broken:
            for i in range(r, 0, -1):
                for j in range(10):
                    matrix[(i, j)] = matrix[(i - 1, j)]


def can_put(piece, matrix):
    under = False
    for sq in piece:
        # out of bounds
        if sq[0] < 0 or sq[0] > 21 or sq[1] < 0 or sq[1] > 9:
            return False
        # square already filled
        if matrix[(sq[0], sq[1])] is not None:
            return False
        # there is a square under the piece
        if sq[0] == 21 or matrix[(sq[0] + 1, sq[1])] is not None:
            under = True
    return under


def height_diff(heights):
    """
    sum = 0
    for i in range(len(heights)):
        for j in range(i, len(heights)):
            sum += (heights[i] - heights[j]) ** 2
    return sum
    """
    sum = 0
    for i in range(len(heights) - 1):
        sum += (heights[i] - heights[i + 1]) ** 2
    return sum


"""
matrix = {}
for i in range(22):
    for j in range(10):
        matrix[(i, j)] = None

matrix[(21, 4)] = 1
matrix[(21, 5)] = 1
matrix[(21, 6)] = 1
matrix[(21, 7)] = 1

print(can_put([[20, 4], [20, 5], [20, 6], [19, 5]], matrix)) # true
print(can_put([[21, 4], [20, 5], [20, 6], [19, 5]], matrix)) # false
print(can_put([[19, 4], [19, 5], [19, 6]], matrix)) # false


def print_matrix(matrix):
    for i in range(22):
        for j in range(10):
            print(matrix[(i, j)], end="\t")
        print()

matrix = {}
for i in range(22):
    for j in range(10):
        matrix[(i, j)] = None
for i in range(10):
    matrix[(21, i)] = 1
matrix[(20, 2)] = 1
matrix[(20, 5)] = 1
print_matrix(matrix)
remove_rows(matrix)
print_matrix(matrix)
"""