import dataclasses
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Set, Generator
import re


def parse(filename: str):

    with open(filename, "r") as f:
        lines = f.read().strip().split("\n")
    return lines


# class Door:
#     loop_size = None
#     subj_num = 7
#
#     def __init__(self, public_key: str):
#         self.public_key = public_key

class Device:
    loop_size = None
    subj_num = 7
    default_val = 1
    val = 1
    other_loop_size = None
    other_val = None

    def __init__(self, public_key: str):
        self.public_key = int(public_key)


    def transform(self, val, subj_number, loop_size):

        for _ in range(loop_size):
            val *= subj_number
            val %= 20201227
        return val

    def find_loop_size(self):
        i = 1
        while True:
            self.val *= self.subj_num
            self.val %= 20201227
            if self.val == self.public_key:
                self.loop_size = i
                break
            else:
                i += 1













if __name__ == "__main__":

    sample = "sample.txt"
    input = "input.txt"

    inp = parse(input)
    card = Device(inp[0])
    door = Device(inp[1])

    # card.find_loop_size()
    door.find_loop_size()
    x = card.public_key
    y = door.loop_size
    encryption = card.transform(1, card.public_key, door.loop_size)
    print()