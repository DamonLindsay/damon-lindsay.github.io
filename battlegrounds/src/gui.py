# src/gui.py

import os
import random
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from game_logic.engine import Game
from game_logic.models import Minion


class BattlegroundsGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Battlegrounds - Basic GUI with Images")
        self.game = Game()

        # Dictionary to hold loaded images so they aren't garbage-collected.
        self.images = {}

        # Load all needed assets at startup
        self.load_assets()

        # Set up the GUI layout
        self.setup_ui()

    def load_assets(self):
        hero_path = os.path.join(os.path.dirname(__file__), "..", "assets", "hero_portrait.png")
        goblin_path = os.path.join(os.path.dirname(__file__), "..", "assets", "goblin.png")

        print(f"Loading Hero Image: {hero_path}")  # Debugging output
        print(f"Loading Minion Image: {goblin_path}")

        if os.path.exists(hero_path):
            hero_img = Image.open(hero_path).resize((100, 100))
            self.images["hero_portrait"] = ImageTk.PhotoImage(hero_img)
        else:
            print("❌ Hero Image Not Found!")

        if os.path.exists(goblin_path):
            goblin_img = Image.open(goblin_path).resize((80, 80))
            self.images["minion_goblin"] = ImageTk.PhotoImage(goblin_img)
        else:
            print("❌ Minion Image Not Found!")

    def setup_ui(self):
        # Top Frame: Player Entry & Add Button
        self.top_frame = ttk.Frame(self.root, padding="10")
        self.top_frame.pack(side=tk.TOP, fill=tk.X)

        self.player_label = ttk.Label(self.top_frame, text="Add Player:")
        self.player_label.pack(side=tk.LEFT)

        self.player_name_var = tk.StringVar()
        self.player_entry = ttk.Entry(self.top_frame, textvariable=self.player_name_var)
        self.player_entry.pack(side=tk.LEFT, padx=5)

        self.add_player_button = ttk.Button(self.top_frame, text="Add", command=self.add_player)
        self.add_player_button.pack(side=tk.LEFT)

        # Middle Frame: Display area (Hero + Minion placeholders)
        self.middle_frame = ttk.Frame(self.root, padding="10")
        self.middle_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Hero Portrait (placeholder)
        self.hero_label = ttk.Label(self.middle_frame, text="Hero Portrait")
        self.hero_label.pack(side=tk.LEFT, padx=10)

        if self.images["hero_portrait"]:
            self.hero_img_label = ttk.Label(self.middle_frame, image=self.images["hero_portrait"])
            self.hero_img_label.pack(side=tk.LEFT)

        # Example Minion Display
        self.minion_label = ttk.Label(self.middle_frame, text="Minion Preview")
        self.minion_label.pack(side=tk.LEFT, padx=10)

        if self.images["minion_goblin"]:
            self.minion_img_label = ttk.Label(self.middle_frame, image=self.images["minion_goblin"])
            self.minion_img_label.pack(side=tk.LEFT)

        # Bottom Frame: Controls
        self.bottom_frame = ttk.Frame(self.root, padding="10")
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.start_button = ttk.Button(self.bottom_frame, text="Start Game", command=self.start_game)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.next_phase_button = ttk.Button(self.bottom_frame, text="Next Phase", command=self.next_phase)
        self.next_phase_button.pack(side=tk.LEFT, padx=5)

        # Info Label
        self.info_label = ttk.Label(self.bottom_frame, text="Welcome to Battlegrounds!")
        self.info_label.pack(side=tk.LEFT, padx=5)

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
        summary_lines = [f"Round {self.game.round_number} complete."]
        for player in self.game.players:
            summary_lines.append(
                f"{player.player_name}: {len(player.minions)} minions, "
                f"Hero Health={player.hero.health}, Gold={player.gold}"
            )
        self.game.round_number += 1
        return "\n".join(summary_lines)

    def update_info(self, message):
        self.info_label.config(text=message)
