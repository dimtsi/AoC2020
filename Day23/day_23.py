from typing import List, Dict

from collections import Counter

def rotate(l, n):
    l = l[-n:] + l[:-n]
    return l


def get_next_three_values_and_remove(i, array, k):
    idxs = get_next_three_idx(i, array, k)
    to_remove = [array[i] for i in idxs]
    [array.remove(elem) for elem in to_remove]
    return array, to_remove

def get_next_three_idx(i, array, k):
    j = i + 1
    out = []
    while j < i + k + 1:
        out.append(j % len(array))
        j += 1
    return out


def get_next_dest(curr_cup, array, to_move):
    dest = curr_cup - 1
    while True:
        if dest < min(array) and dest < min(to_move):
            dest = max(array)
            break
        elif dest in to_move:
            dest -= 1
        else:
            break
    return dest, array.index(dest)

def play_round(curr_cup, array):
    input_arr = array[:]

    curr_cup_idx = array.index(curr_cup)
    array, next_three = get_next_three_values_and_remove(
        curr_cup_idx, array, 3
    )
    dest, dest_index = get_next_dest(curr_cup, array, next_three)
    for elem in reversed(next_three):
        array.insert(dest_index + 1, elem)
    new_input_arr = array[:]

    new_curr_cup_idx = array.index(curr_cup)
    if new_curr_cup_idx != curr_cup_idx:
        diff = new_curr_cup_idx - curr_cup_idx
        rotated_array = rotate(array, -diff)
        array = rotated_array
    final_array = array[:]
    return array[(array.index(curr_cup) + 1) % len(array)], array



def get_final_string(array):
    idx_one = array.index(1)
    original = array[:]
    final = rotate(array, -idx_one - 1)[:-1]
    return "".join([str(x) for x in final])



if __name__ == "__main__":

    sample = '389125467'
    input = '318946572'
    inp = list(map(int, list(input)))

    prev_curr_cup, prev_curr_cup_idx = None, None
    curr_cup = inp[0]
    for i in range(1000000):
        curr_cup, inp = play_round(curr_cup, inp)
    p1 = get_final_string(inp)
    print()

