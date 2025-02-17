# src/main.py

import tkinter as tk
from gui import BattlegroundsGUI


def main():
    root = tk.Tk()
    app = BattlegroundsGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
