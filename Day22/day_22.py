from typing import List, Dict

from collections import Counter


class Player:
    def __init__(self, id, cards):
        self.id = id
        self.cards = cards

    def draw(self):
        card = self.cards.pop(0)
        return card


def load_data(filename: str):
    with open(filename, "r") as f:

        player_a, player_b = f.read().strip().split("\n\n")

        player_a_cards = list(map(int, player_a.split("\n")[1:]))
        player_b_cards = list(map(int, player_b.split("\n")[1:]))

    return Player("a", player_a_cards), Player("b", player_b_cards)


def play_round(player_a: Player, player_b: Player):
    card_a = player_a.draw()
    card_b = player_b.draw()

    if card_a > card_b:
        player_a.cards.extend([card_a, card_b])
    elif card_b > card_a:
        player_b.cards.extend([card_b, card_a])


def play_game(player_a: Player, player_b: Player):

    while player_a.cards and player_b.cards:
        play_round(player_a, player_b)

    if player_a.cards:
        return player_a
    else:
        return player_b


def calc_score(player: Player):
    cards = player.cards
    pairs = list(enumerate((reversed(cards)), 1))
    return sum([p[0] * p[1] for p in pairs])


if __name__ == "__main__":
    player_a, player_b = load_data("input.txt")
    winner = play_game(player_a, player_b)
    score = calc_score(winner)

    print()
