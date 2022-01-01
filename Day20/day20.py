import math
import re
import numpy as np
from typing import List, Dict, Tuple, DefaultDict, Set
from collections import defaultdict, Counter
from copy import deepcopy
from parse_sample_image import SAMPLE_CORRECT_IMAGES

BORDER_IDX = {0: "top", 1: "bottom", 2: "left", 3: "right"}

MONSTER = "                  # \n#    ##    ##    ###\n #  #  #  #  #  #   "


def rotate(tile):
    for r in range(4):
        a = np.rot90(tile, r)
        yield a
        yield np.fliplr(a)
        yield np.flipud(a)
        yield np.flipud(np.fliplr(a))
        yield np.flip(a, 0)


def parse(filename):
    sample = True if "sample" in filename else False

    tiles_dict = {}

    with open(filename, "r") as f:
        tiles: List[str] = f.read().rstrip().split("\n\n")

    for tile in tiles:
        image = []
        for i, line in enumerate(tile.split("\n")):
            if i == 0:
                id = int(re.findall("\d+", line)[0])
            else:
                image.append(list(line))
        image = np.array(image)
        tiles_dict[id] = Tile(id, image)

    return tiles_dict


class Tile:
    orientations: np.ndarray
    neighbor_orient: DefaultDict[int, Set[Tuple]] = defaultdict(dict)

    def __init__(self, id: int, array: np.ndarray):
        self.final = None
        self.final_change_count = 0
        self.ID = id
        self.base = array
        self.found_orientation = False
        self.location: Tuple[int, int] = None
        self.get_orientations()
        self.neighbor_orient = deepcopy(self.neighbor_orient)
        self.neighbors = set()

    def get_orientations(self):
        rotation = self.base
        self.orientations = [rot for rot in rotate(rotation)]
        self.borders = list(
            get_borders(orient) for orient in self.orientations
        )

    def __repr__(self):
        return f"Tile with id: {self.ID}"


def get_borders(array: np.ndarray):
    top = "".join(list(array[0, :].ravel()))
    bottom = "".join(list(array[-1, :].ravel()))
    left = "".join(list(array[:, 0].ravel()))
    right = "".join(list(array[:, -1].ravel()))
    return [top, bottom, left, right]


def check_if_is_neighbor(tile1: Tile, tile2: Tile):
    for i, (or1, borders1) in enumerate(
        zip(tile1.orientations, tile1.borders)
    ):
        for (j, (or2, borders2)) in enumerate(
            zip(tile2.orientations, tile2.borders)
        ):
            common = set(borders1) & set(borders2)
            if len(common) > 0:
                common_border = common.pop()
                common_1_location = BORDER_IDX[borders1.index(common_border)]
                common_2_location = BORDER_IDX[borders2.index(common_border)]
                if common_1_location == common_2_location:
                    continue
                if (
                    common_1_location in {"top", "bottom"}
                    and common_2_location in {"left", "right"}
                    or common_2_location in {"top", "bottom"}
                    and common_1_location in {"left", "right"}
                ):
                    continue

                tile1.neighbor_orient[i][common_1_location] = (
                    tile2.ID,
                    j,
                    common_2_location,
                )
                tile2.neighbor_orient[j][common_2_location] = (
                    tile1.ID,
                    i,
                    common_1_location,
                )
                tile1.neighbors.add(tile2.ID)
                tile2.neighbors.add(tile1.ID)


def find_all_neighbors(tiles: Dict[str, Tile]):
    visited = set()
    for i, (id1, tile1) in enumerate(tiles.items()):
        if len(tile1.neighbor_orient) == 4:
            continue
        visited.add(id1)
        for j, (id2, tile2) in enumerate(tiles.items()):
            if id2 in visited:
                continue
            if tile1.ID != tile2.ID:
                if len(tile2.neighbor_orient) == 4:
                    continue
                if tile2.ID in tile1.neighbor_orient.keys():
                    # try:
                    assert (
                        tile1.ID in tile2.neighbor_orient.keys()
                    ), f"Tile with id {tile1.ID} is not in neighbors of {tile2.ID}. Opposite holds"
                    continue
                check_if_is_neighbor(tile1, tile2)


def check_orientation_validity(
    tile,
    orient_idx,
    top_neighbor=None,
    bottom_neighbor=None,
    left_neighbor=None,
    right_neighbor=None,
):
    for i, neigh in enumerate(
        [top_neighbor, bottom_neighbor, left_neighbor, right_neighbor]
    ):
        if neigh == -1 and BORDER_IDX[i] in tile.neighbor_orient[orient_idx]:
            return False
        elif neigh and neigh != -1:
            if tile.neighbor_orient[orient_idx][BORDER_IDX[i]][0] != neigh:
                return False
    return True


def assemble_top_row_left_col(tiles, corner_ids, sample):
    placed = {}

    start = 1951 if sample else 2473
    curr_tile = tiles[start]
    potential_orientations = defaultdict(list)
    to_check = curr_tile.neighbor_orient.keys()
    for orient_idx in to_check:
        if check_orientation_validity(
            curr_tile, orient_idx, -1, None, -1, None
        ):
            potential_orientations[curr_tile.ID].append(orient_idx)

    # top row
    top_row = []
    curr_tile = tiles[start]
    while curr_tile:
        orientation = potential_orientations[curr_tile.ID].pop(0)
        top_row.append((curr_tile.ID, orientation))
        if curr_tile.ID in corner_ids and curr_tile.ID != start:
            break
        next_bottom_id, next_bottom_orient, _ = curr_tile.neighbor_orient[
            orientation
        ]["right"]
        if next_bottom_id in corner_ids:
            is_valid = check_orientation_validity(
                tiles[next_bottom_id],
                next_bottom_orient,
                -1,
                None,
                curr_tile.ID,
                -1,
            )
        else:
            is_valid = check_orientation_validity(
                tiles[next_bottom_id],
                next_bottom_orient,
                -1,
                None,
                curr_tile.ID,
                None,
            )
        if not is_valid:
            top_row.pop()
            continue
        else:
            curr_tile = tiles[next_bottom_id]
            potential_orientations[curr_tile.ID].append(next_bottom_orient)
    placed = {x[0] for x in top_row}

    # left_col
    left_col = []
    curr_tile = tiles[start]
    while curr_tile:
        if curr_tile.ID == start:
            orientation = top_row[0][1]
        else:
            orientation = potential_orientations[curr_tile.ID].pop()
        left_col.append((curr_tile.ID, orientation))
        if curr_tile.ID in corner_ids and curr_tile.ID != start:
            break
        next_bottom_id, next_bottom_orient, _ = curr_tile.neighbor_orient[
            orientation
        ]["bottom"]
        if next_bottom_id in placed:
            continue
        if next_bottom_id in corner_ids:
            is_valid = check_orientation_validity(
                tiles[next_bottom_id],
                next_bottom_orient,
                curr_tile.ID,
                -1,
                -1,
                None,
            )
        else:
            is_valid = check_orientation_validity(
                tiles[next_bottom_id],
                next_bottom_orient,
                curr_tile.ID,
                None,
                -1,
                None,
            )
        if not is_valid:
            left_col.pop()
            continue
        else:
            curr_tile = tiles[next_bottom_id]
            potential_orientations[curr_tile.ID].append(next_bottom_orient)

    assert len(tiles) == len(top_row) * len(left_col)
    top_row_ids = set([x[0] for x in top_row])
    top_col_ids = set([x[0] for x in left_col])
    assert not (top_row_ids & top_col_ids) - set([start])

    return top_row, left_col


def pprint_image_with_borders(image):
    def pprint_row(row, tile_n_rows):
        for i in range(tile_n_rows):
            print(" ".join(["".join(tile[i]) for tile in row]))

    pimage = deepcopy(image)
    tile_n_rows = pimage[0][0].shape[0]
    for row in pimage:
        pprint_row(row, tile_n_rows)
        print()


def crop_borders_and_merge_image(image):
    cropped_image = [
        [None for _ in range(len(image[0]))] for _ in range(len(image))
    ]

    for i in range(len(image)):
        for j in range(len(image[0])):
            cropped_image[i][j] = image[i][j][1:-1, 1:-1]
    pprint_image_with_borders(cropped_image)

    final_rows = []
    for row in cropped_image:
        final_rows.append(np.hstack(row))
    merged = np.vstack(final_rows)
    print("\nfinal")
    pprint(merged)

    return merged


def pprint(image):
    dct = {0: ".", 1: "#", 5: "O", ".": ".", "#": "#"}
    print()
    for row in image:
        print("".join([dct[el] for el in row]))


def assemble_image(tiles, corner_ids, sample):

    top_row, left_col = assemble_top_row_left_col(tiles, corner_ids, sample)

    image_tile_ids = [
        [None for _ in range(len(top_row))] for _ in range(len(left_col))
    ]
    image = [[None for _ in range(len(top_row))] for _ in range(len(left_col))]

    # set top row - left col
    for i in range(len(top_row)):
        image_tile_ids[0][i] = top_row[i]

    for i in range(len(left_col)):
        image_tile_ids[i][0] = left_col[i]

    # fill ids
    for i in range(1, len(left_col)):
        for j in range(1, len(top_row)):
            left_id, left_orient = image_tile_ids[i][j - 1]
            top_id, top_orient = image_tile_ids[i - 1][j]
            new_val = tiles[left_id].neighbor_orient[left_orient]["right"][:2]
            assert (
                new_val
                == tiles[top_id].neighbor_orient[top_orient]["bottom"][:2]
            )
            image_tile_ids[i][j] = new_val

    # fill complete
    for i in range(len(left_col)):
        for j in range(len(top_row)):
            id, orient = image_tile_ids[i][j]
            image[i][j] = tiles[id].orientations[orient]

    pprint_image_with_borders(image)

    final_image = crop_borders_and_merge_image(image)
    return final_image


def convolve(i, j, img, kernel):
    M, N = kernel.shape
    window = img[i : i + M, j : j + N]
    assert window.shape == kernel.shape
    result = (window * kernel).sum()
    if result == kernel.sum():
        return True
    return False


def find_monsters(img):
    # convert to binary --> # == 1
    img = np.array(
        [
            [0 if img[i][j] != "#" else 1 for j in range(len(img[0]))]
            for i in range(len(img))
        ]
    )

    kernel = np.array([list(row) for row in MONSTER.split("\n")])
    kernel = np.array(
        [
            [0 if kernel[i][j] != "#" else 1 for j in range(len(kernel[0]))]
            for i in range(len(kernel))
        ]
    )

    kernel_hash_pos = []
    for i in range(kernel.shape[0]):
        for j in range(kernel.shape[1]):
            if kernel[i][j] == 1:
                kernel_hash_pos.append((i, j))

    found_rotation = False
    monster_offsets = []
    for rot_img in rotate(img):
        for i in range(len(img) - kernel.shape[0]):
            for j in range(len(img) - kernel.shape[1]):
                if convolve(i, j, img, kernel):
                    found_rotation = True
                    monster_offsets.append((i, j))
        if found_rotation:
            break
    # replace offsets with zero
    for i, j in monster_offsets:
        for k, l in kernel_hash_pos:
            rot_img[i + k][j + l] = 5
    pprint(rot_img)
    hash_count = Counter("".join([str(el) for el in rot_img]))
    return hash_count["1"]


if __name__ == "__main__":
    sample = "sample.txt"
    input = "input.txt"

    inp = sample
    sample = True if "sample" in inp else False
    from time import time

    start = time()

    TILES: Dict[str, Tile] = parse(inp)
    find_all_neighbors(TILES)

    corners = [tile for tile in TILES.values() if len(tile.neighbors) == 2]
    corners_ids = [tile.ID for tile in corners]
    from functools import reduce

    end = time()
    print(f"part1: {reduce(lambda x, y: x * y, corners_ids)}")
    # p2
    assembled_img = assemble_image(TILES, corners_ids, sample)
    print(f"part2: {find_monsters(assembled_img)}")

    print(end - start)

    print()
