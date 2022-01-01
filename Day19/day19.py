from functools import lru_cache
from typing import Dict
import re


def parse(filename):
    with open(filename, "r") as f:
        lines = f.read().rstrip().split("\n")
    RULES = {}
    INPUTS = []

    flag = False
    for line in lines:
        if line == "":
            flag = True
            continue

        if not flag:
            rule, val = line.split(": ")
            val = val.strip()
            if val == '"a"':
                val = "a"
            elif val == '"b"':
                val = "b"
            RULES[rule] = val
        else:
            INPUTS.append(line)

    return RULES, INPUTS


def get_regex(rule: str, rules: Dict, regexes: Dict, p2=False):
    if rule in regexes:
        return regexes[rule]
    if rule == "8" and p2:
        regex = get_looped_regex(20, "8", rules, regexes)
        regexes[rule] = regex
        return regex
    elif rule == "11" and p2:
        regex = get_looped_regex(20, "11", rules, regexes)
        regexes[rule] = regex
        return regex

    curr: str = rules[rule]
    if "|" in curr:
        rule_1, rule_2 = curr.split(" | ")

        # try:
        split = rule_1.split(" ")
        if len(split) <= 1:
            regex_1 = "(" + get_regex(split[0], rules, regexes, p2) + ")"
        else:
            regex_1 = (
                "("
                + ")(".join(
                    [get_regex(elem, rules, regexes, p2) for elem in split]
                )
                + ")"
            )
        split = rule_2.split()
        if len(split) == 1:
            regex_2 = "(" + get_regex(split[0], rules, regexes, p2) + ")"
        else:
            regex_2 = (
                "("
                + ")(".join(
                    [get_regex(elem, rules, regexes, p2) for elem in split]
                )
                + ")"
            )
        # except:
        #     pass
        regex = f"({regex_1}|{regex_2})"
    elif curr == "a":
        regex = r"a"
    elif curr == "b":
        regex = r"b"
    else:
        split = curr.split(" ")
        if len(split) == 1:
            regex = "(" + get_regex(split[0], rules, regexes, p2) + ")"
        else:
            regex = (
                "("
                + ")(".join(
                    [get_regex(elem, rules, regexes, p2) for elem in split]
                )
                + ")"
            )

    regexes[rule] = regex
    return regex


def get_looped_regex(n, val, rules, regexes):
    r42 = get_regex("42", rules, regexes)
    r31 = get_regex("31", rules, regexes)

    if val == "8":
        return f"(({r42})+)"
    if val != "11":
        raise "Looped regex generation should be done only for rule 8 or 11"

    r11s = []
    for n in range(1, 10):
        r11s.append(f"({r42}){{{n}}}({r31}){{{n}}}")
    r11 = "(" + ")|(".join([i for i in r11s]) + ")"
    return r11


def match(string, rule):
    if re.fullmatch(regexes[rule], string):
        return True
    else:
        return False


if __name__ == "__main__":

    sample = "sample1.txt"
    sample2 = "sample2.txt"
    input = "input.txt"

    inp = input

    rules, strings = parse(inp)
    regexes = {}
    get_regex("0", rules, regexes)
    matches_1 = sum([match(s, "0") for s in strings])
    regexes.clear()
    rules, strings = parse(inp)
    get_regex("42", rules, regexes, p2=True)
    get_regex("31", rules, regexes, p2=True)
    get_regex("0", rules, regexes, p2=True)
    matches_2 = sum([match(s, "0") for s in strings])
    print(f"p1: {matches_1}\npart2:{matches_2}")
