import copy
import copyreg
from typing import List, Dict, Tuple

from collections import defaultdict, Counter

def parse(filename):
    with open(filename, "r") as f:
        input = f.read().strip().split("\n")
    return input


def move_step(move: str, x: int, y: int):
    move = list(move)
    start_x, start_y = x, y
    odd = False if y % 2 == 0 else True

    if move == ["e"]:
        x += 1
    elif move == ["w"]:
        x -= 1

    else: #sw, se...
        if "n" in move:
            y -= 1
        if "s" in move:
            y += 1
        if odd:
            if "e" in move:
                x += 1
        else:
            if "w" in move:
                x -= 1
    return x, y


def get_moves_from_string(string: str):
    moves = list(string)
    final_moves = []
    idx = 0
    while idx < len(moves):
        if moves[idx] in {"s", "n"}:
            final_moves.append(moves[idx] + moves[idx + 1])
            idx += 2
        else:
            final_moves.append(moves[idx])
            idx += 1
    return final_moves


def update_tile_state(string: str, states: Dict, states_changes_counter):
    from copy import deepcopy
    initial_states = deepcopy(states)
    moves = get_moves_from_string(string)
    # assert("".join(moves) == string)
    idx = 0
    x, y = 3, 3
    while idx < len(moves):
        x, y = move_step(moves[idx], x, y)
        idx += 1
    flip(x, y, states)


def run_part_1(inputs: List[str]):
    states = defaultdict(lambda: "w")
    states_changes_counter = defaultdict(lambda: 0)
    for tile in inputs:
        update_tile_state(tile, states, states_changes_counter)

    values = Counter(states.values())
    return values['b'], states

#p2

def check_if_exists_and_append_to_neighbors(i, j, neighbors: List, grid:Dict):
    # if (i, j) in grid.keys():
    neighbors.append((i, j))


def get_neighbors(i: int, j: int, grid: Dict[Tuple, str]) -> List[Tuple[int, int]]:
    neighbors = []
    check_if_exists_and_append_to_neighbors(i + 1, j, neighbors, grid)
    check_if_exists_and_append_to_neighbors(i - 1, j, neighbors, grid)
    check_if_exists_and_append_to_neighbors(i, j - 1, neighbors, grid)
    check_if_exists_and_append_to_neighbors(i, j + 1, neighbors, grid)
    if j % 2 == 0:
        # even
        check_if_exists_and_append_to_neighbors(i - 1, j - 1, neighbors, grid)
        check_if_exists_and_append_to_neighbors(i - 1, j + 1, neighbors, grid)
    else:
        # odd
        check_if_exists_and_append_to_neighbors(i + 1, j - 1, neighbors, grid)
        check_if_exists_and_append_to_neighbors(i + 1, j + 1, neighbors, grid)
    return neighbors


def flip(i: int, j: int, grid: Dict):
    if grid[(i, j)] == "b":
        grid[(i, j)] = "w"
    else:
        grid[(i, j)] = "b"


def to_flip(i, j, grid: Dict, to_change: Dict) -> Dict[Tuple[int, int], bool]:
    neighbors = get_neighbors(i, j, grid)
    neighbors_2 = [neighbor for neighbor in neighbors if neighbor in grid.keys()]
    n_blacks = sum([True for neighbor in neighbors_2 if grid[neighbor] == "b"])

    if grid[(i, j)] == "b":
        if n_blacks == 0 or n_blacks > 2:
            to_change[(i, j)] = True
    else:
        if n_blacks == 2:
            to_change[(i, j)] = True

def flip_from_to_change(grid: Dict, to_flip: Dict):
    for key in to_flip.keys():
        if to_flip[key]:
            flip(*key, grid)


def get_elements_to_explore(grid):
    discovered = grid.keys()
    new_neighbors = set()
    for i, j in discovered:
        neighbors = get_neighbors(i, j, grid)
        for neigh in neighbors:
            if neigh not in new_neighbors:
                new_neighbors.add(neigh)

    return list(discovered) + list(new_neighbors)


def run2(grid: Dict, days):
    initial_grid = copy.deepcopy(grid)
    for i in range(1, days + 1):
        print(i)
        to_change = defaultdict(lambda: False)

        discovered = get_elements_to_explore(grid)

        for coords in discovered:
            to_flip(*coords, grid, to_change)
        flip_from_to_change(grid, to_change)
        n_blacks = Counter(grid.values())["b"]
        print()
    print()








if __name__ == "__main__":

    sample = 'sample.txt'
    input = 'input.txt'

    inp = input
    lines = parse(input)
    n_black, grid = run_part_1(lines)
    print(f"p1:{n_black}")
    run2(grid, 100)
