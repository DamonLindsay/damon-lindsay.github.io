# src/game_logic/models.py

class Hero:
    def __init__(self, name, health=30):
        self.name = name
        self.health = health

    def take_damage(self, damage):
        self.health -= damage


class Minion:
    def __init__(self, name, attack, health):
        self.name = name
        self.attack = attack
        self.health = health


class Player:
    def __init__(self, player_name):
        self.player_name = player_name
        self.hero = Hero(f"{player_name}'s Hero")
        self.minions = []
        self.gold = 10

    def buy_minion(self, minion_cost, minion):
        if self.gold >= minion_cost:
            self.minions.append(minion)
            self.gold -= minion_cost

    def sell_minion(self, index):
        if 0 <= index < len(self.minions):
            sold = self.minions.pop(index)
            # Simplified: refund 1 gold
            self.gold += 1
            return sold
        return None
