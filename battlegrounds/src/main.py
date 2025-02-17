import random


class Hero:
    def __init__(self, name, health=30):
        self.name = name
        self.health = health

    def take_damage(self, damage):
        self.health -= damage
        print(f"{self.name} takes {damage} damage! (Health: {self.health})")


class Minion:
    def __init__(self, name, attack, health):
        self.name = name
        self.attack = attack
        self.health = health


class Player:
    def __init__(self, name):
        self.name = name
        self.hero = Hero(f"{name}'s Hero")
        self.minions = []
        self.gold = 10

    def buy_minion(self, minion):
        cost = 3
        if self.gold >= cost:
            self.minions.append(minion)
            self.gold -= cost
            print(
                f"{self.name} bought {minion.name} (Attack: {minion.attack}, Health: {minion.health}). Gold left: {self.gold}")
        else:
            print(f"{self.name} doesn't have enough gold to buy {minion.name}.")

    def sell_minion(self, index):
        if 0 <= index < len(self.minions):
            sold = self.minions.pop(index)
            self.gold += 1  # Simplified: refund 1 gold
            print(f"{self.name} sold {sold.name}. Gold is now: {self.gold}")
        else:
            print("Invalid minion index.")


class Game:
    def __init__(self):
        self.players = []

    def add_player(self, name):
        player = Player(name)
        self.players.append(player)
        print(f"Player '{name}' joined the lobby.")

    def start_game(self):
        print("\n--- Starting Battlegrounds ---")
        round_num = 1
        while len(self.players) > 1:
            print(f"\n=== Round {round_num} ===")
            self.tavern_phase()
            self.battle_phase()
            round_num += 1
        print("\nGame Over!")
        if self.players:
            print(f"Winner: {self.players[0].name}")
        else:
            print("No winner.")

    def tavern_phase(self):
        print("\nTavern Phase: Each player attempts to buy a minion.")
        for player in self.players:
            # For MVP, automatically buy a random minion if affordable.
            if player.gold >= 3:
                minion = Minion("Goblin", random.randint(1, 3), random.randint(1, 3))
                player.buy_minion(minion)
            else:
                print(f"{player.name} cannot afford a minion this round.")

    def battle_phase(self):
        print("\nBattle Phase: Auto-resolving battles.")
        if len(self.players) < 2:
            return

        # Shuffle players and pair them up.
        random.shuffle(self.players)
        next_round_players = []
        for i in range(0, len(self.players), 2):
            if i + 1 < len(self.players):
                p1 = self.players[i]
                p2 = self.players[i + 1]
                winner, loser = self.resolve_battle(p1, p2)
                next_round_players.append(winner)
                # Loser takes fixed damage.
                loser.hero.take_damage(3)
                if loser.hero.health > 0:
                    next_round_players.append(loser)
            else:
                # Odd player gets a bye.
                print(f"{self.players[i].name} gets a bye to the next round.")
                next_round_players.append(self.players[i])
        # Only keep players whose heroes are still alive.
        self.players = [p for p in next_round_players if p.hero.health > 0]

    def resolve_battle(self, p1, p2):
        # Simplified scoring: sum of minion attacks plus a small random factor.
        score1 = sum(m.attack for m in p1.minions) + random.randint(0, 2)
        score2 = sum(m.attack for m in p2.minions) + random.randint(0, 2)
        print(f"\nBattle: {p1.name} (Score: {score1}) vs {p2.name} (Score: {score2})")
        if score1 >= score2:
            print(f"{p1.name} wins the battle.")
            return p1, p2
        else:
            print(f"{p2.name} wins the battle.")
            return p2, p1


if __name__ == "__main__":
    game = Game()
    # For testing, add some players to the lobby.
    game.add_player("Alice")
    game.add_player("Bob")
    game.add_player("Charlie")
    game.start_game()
