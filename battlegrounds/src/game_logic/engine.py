# src/game_logic/engine.py

import random
from .models import Player, Minion


class Game:
    def __init__(self):
        self.players = []
        self.round_number = 0

    def add_player(self, player_name):
        self.players.append(Player(player_name))

    def start_game(self):
        self.round_number = 1

    def tavern_phase(self):
        """
        Simplified tavern phase:
         - Each player automatically buys a random minion if they can afford it.
        """
        for player in self.players:
            if player.gold >= 3:
                # Random minion with random stats
                minion = Minion("Goblin", random.randint(1, 3), random.randint(1, 3))
                player.buy_minion(3, minion)

    def battle_phase(self):
        """
        Simplified battle resolution:
         - Pair up players, compare sum of minion attacks + random factor.
         - Loser takes fixed damage.
        """
        random.shuffle(self.players)
        next_round_players = []
        for i in range(0, len(self.players), 2):
            if i + 1 < len(self.players):
                p1 = self.players[i]
                p2 = self.players[i + 1]
                winner, loser = self.resolve_battle(p1, p2)
                loser.hero.take_damage(3)
                # Both players continue if still alive
                if p1.hero.health > 0:
                    next_round_players.append(p1)
                if p2.hero.health > 0:
                    next_round_players.append(p2)
            else:
                # Odd player gets a bye
                next_round_players.append(self.players[i])
        self.players = [p for p in next_round_players if p.hero.health > 0]

    def resolve_battle(self, p1, p2):
        score1 = sum(m.attack for m in p1.minions) + random.randint(0, 2)
        score2 = sum(m.attack for m in p2.minions) + random.randint(0, 2)
        if score1 >= score2:
            return p1, p2
        else:
            return p2, p1

    def is_game_over(self):
        return len(self.players) <= 1

    def get_winner(self):
        return self.players[0] if self.players else None
