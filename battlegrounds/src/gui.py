# src/gui.py

import tkinter as tk
from tkinter import ttk
from game_logic.engine import Game


class BattlegroundsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Battlegrounds - Basic GUI")
        self.game = Game()

        self.setup_ui()

    def setup_ui(self):
        """
        Create a minimal Hearthstone-like layout with:
        - A top frame for 'Lobby/Players'
        - A middle frame for 'Tavern/Battle info'
        - A bottom frame for 'Controls'
        """
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.middle_frame = ttk.Frame(self.root, padding="10")
        self.middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        # Top Frame: Player Entry & Add Button
        self.player_label = ttk.Label(self.top_frame, text="Add Player:")
        self.player_label.pack(side=tk.LEFT)

        self.player_name_var = tk.StringVar()
        self.player_entry = ttk.Entry(self.top_frame, textvariable=self.player_name_var)
        self.player_entry.pack(side=tk.LEFT, padx=5)

        self.add_player_button = ttk.Button(self.top_frame, text="Add", command=self.add_player)
        self.add_player_button.pack(side=tk.LEFT)

        # Middle Frame: Display area
        self.info_label = ttk.Label(self.middle_frame, text="Welcome to Battlegrounds!")
        self.info_label.pack()

        # Bottom Frame: Control buttons
        self.start_button = ttk.Button(self.bottom_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.next_phase_button = ttk.Button(self.bottom_frame, text="Next Phase", command=self.next_phase)
        self.next_phase_button.pack(side=tk.LEFT, padx=5)

    def add_player(self):
        name = self.player_name_var.get().strip()
        if name:
            self.game.add_player(name)
            self.player_name_var.set("")
            self.update_info(f"Player '{name}' added.")
        else:
            self.update_info("Please enter a valid player name.")

    def start_game(self):
        if not self.game.players:
            self.update_info("No players in the lobby. Add players first.")
            return
        self.game.start_game()
        self.update_info("Game started! Round 1 begins.")

    def next_phase(self):
        if not self.game.players:
            self.update_info("No players in the game.")
            return

        if self.game.is_game_over():
            winner = self.game.get_winner()
            if winner:
                self.update_info(f"Game Over! Winner: {winner.player_name}")
            else:
                self.update_info("Game Over! No winner.")
            return

        # Run a single cycle: tavern -> battle
        self.game.tavern_phase()
        self.game.battle_phase()
        self.update_info(self.round_summary())

        if self.game.is_game_over():
            winner = self.game.get_winner()
            if winner:
                self.update_info(f"Game Over! Winner: {winner.player_name}")
            else:
                self.update_info("Game Over! No winner.")

    def round_summary(self):
        summary_lines = []
        summary_lines.append(f"Round {self.game.round_number} Complete.")
        for player in self.game.players:
            summary_lines.append(f"{player.player_name}: {len(player.minions)} minions, "
                                 f"Hero Health = {player.hero.health}, Gold = {player.gold}")
        self.game.round_number += 1
        return "\n".join(summary_lines)

    def update_info(self, message):
        self.info_label.config(text=message)
