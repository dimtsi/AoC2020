from typing import List, Dict

from collections import defaultdict


def load_data(filename: str):
    ingredients = []
    allergens = []
    with open(filename, "r") as f:
        for line in f:
            ingr, all = line.strip().split(" (")
            all = all.replace(")", "").replace("contains ", "")
            ingredients.append(ingr.split())
            allergens.append(all.split(", "))
    return ingredients, allergens


def get_potential_matches(ingredients: List[str], allergens: List[str]):
    candidates = {}
    used_ingr = set()
    for elems, allergens in zip(ingredients, allergens):
        for al in allergens:
            if not al in candidates:
                candidates[al] = set(elems)
            else:
                candidates[al] = candidates[al] & set(elems)
    print()
    for cand in candidates:
        used_ingr.update(candidates[cand])
    return candidates, used_ingr


def get_unique(ingredients: List[str], allergens: List[str]):
    unique_ingr = set()
    unique_allerg = set()

    for ingr in ingredients:
        unique_ingr .update(ingr)
    for al in allergens:
        unique_allerg.update(al)
    return unique_ingr, unique_allerg


def count_appearances(unique, ingred_list):
    count = 0
    for ingr in ingred_list:
        count += len(set(ingr) & unique)
    return count


def solve(candidates):
    ingr_to_al = defaultdict(set)

    for allerg, ingred in candidates.items():
        for ingr in ingred:
            ingr_to_al[ingr].add(allerg)

    stack = []
    for cand in candidates:
        if len(candidates[cand]) == 1:
            stack.append(cand)
            break

    while stack:
        curr_all = stack.pop()
        curr_ing = list(candidates[curr_all])[0]
        potential_matches = ingr_to_al[curr_ing] - set([curr_all])

        for match in potential_matches:
            candidates[match].remove(curr_ing)
            if len(candidates[match]) == 1:
                stack.append(match)


    no_set_cands = {k: list(v)[0] for k, v in candidates.items()}
    sorted_by_all = sorted(list(no_set_cands.items()), key=lambda x: x[0])
    return [x[1] for x in sorted_by_all]


if __name__ == "__main__":
    ingr, allergens = load_data("input.txt")

    candidates, used_ingr = get_potential_matches(ingr, allergens)
    unique_ingr, unique_al = get_unique(ingr, allergens)
    print("part1")
    print(len(unique_ingr - used_ingr))
    non_used = unique_ingr - used_ingr
    print(count_appearances(non_used, ingr))
    final = solve(candidates)
    final = ",".join(final)
    print(final)