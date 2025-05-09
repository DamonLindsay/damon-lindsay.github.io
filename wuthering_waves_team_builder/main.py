# main.py

import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from characters import characters


class TeamBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wuthering Waves Team Builder")
        self.configure(bg="#1e1e1e")
        self.images = {}
        self.clear_frames()

        # native full‑screen — the OS will handle the taskbar for you
        self.attributes("-fullscreen", True)

        # handy quit key during dev
        self.bind("<Escape>", lambda e: self.destroy())

        # placeholder frames
        self.main_frame = tk.Frame(self, bg="#1e1e1e")
        self.team_frame = tk.Frame(self, bg="#1e1e1e")

        self.show_character_grid()

    # ─── Character Selection Grid ──────────────────────────────────────────────
    def show_character_grid(self):
        # 1) clear the old widgets
        self.clear_frames()

        # 2) pack the container
        self.main_frame.pack(fill="both", expand=True, padx=50, pady=30)

        # 3) header
        header = tk.Label(
            self.main_frame,
            text="Select Your Character",
            bg="#ff7043",
            fg="white",
            font=("Helvetica", 24, "bold"),
            pady=10
        )
        header.pack(fill="x", pady=(0, 20))

        # 4) where cards go
        grid_frame = tk.Frame(self.main_frame, bg="#1e1e1e")
        grid_frame.pack(fill="both", expand=True)

        # 5) calculate how many columns fit
        self.update_idletasks()
        total_width = self.winfo_width() - 100
        card_width = 100 + 2 * 10 + 2 * 15
        cols = max(1, total_width // card_width)

        row = col = 0
        for name in sorted(characters.keys()):
            info = characters[name]
            img = Image.open(info["image"]).resize((100, 100), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.images[name] = photo

            card = tk.Frame(grid_frame, bg="#2e2e2e", bd=2, relief="ridge", padx=10, pady=10)
            card.grid(row=row, column=col, padx=15, pady=15, sticky="nsew")

            btn = tk.Button(card, image=photo, bd=0, command=lambda n=name: self.show_teams(n))
            btn.pack()
            tk.Label(card, text=name, bg="#2e2e2e", fg="white", font=("Helvetica", 10)).pack(pady=(5, 0))

            card.bind("<Enter>", lambda e, c=card: c.config(bg="#383838"))
            card.bind("<Leave>", lambda e, c=card: c.config(bg="#2e2e2e"))

            col += 1
            if col >= cols:
                col = 0
                row += 1

        for c in range(cols):
            grid_frame.grid_columnconfigure(c, weight=1)

    # ─── Team Display (scrollable + back) ───────────────────────────────────────
    def show_teams(self, character_name):
        self.clear_frames()
        self.team_frame.pack(fill="both", expand=True)

        # container centered on screen
        container = tk.Frame(self.team_frame, bg="#1e1e1e")
        container.place(relx=0.5, rely=0.5, anchor="center")

        # scrollable canvas
        canvas = tk.Canvas(
            container,
            bg="#1e1e1e",
            highlightthickness=0,
            width=900, height=700
        )
        vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # inner frame for content
        scrollable = tk.Frame(canvas, bg="#1e1e1e")
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # back button
        tk.Button(
            scrollable,
            text="Back",
            command=self.show_character_grid
        ).pack(anchor="w", padx=10, pady=10)

        data = characters[character_name]
        if "note" in data:
            # show Baizhi‑style note
            tk.Label(
                scrollable,
                text=data["note"].replace("**", ""),
                wraplength=850,
                justify="left",
                bg="#2e2e2e",
                fg="white",
                font=("Helvetica", 12),
                padx=10, pady=10
            ).pack(fill="x", padx=20, pady=20)
            return

        # render each team
        for team in data["teams"]:
            self.create_team_section(scrollable, team["title"], team["slots"])

            # If the team has a specific note, display it right under the section
            if "note" in team:
                tk.Label(
                    scrollable,
                    text=team["note"],
                    bg="#1e1e1e",
                    fg="white",
                    font=("Helvetica", 10, "italic"),
                    justify="left",
                    anchor="w",
                    padx=20,
                    wraplength=850
                ).pack(fill="x", pady=(0, 10))

    # ─── Team Panel (three slots + separators) ─────────────────────────────────
    def create_team_section(self, parent, title, slots):
        frame = tk.Frame(parent, bg="#2e2e2e", pady=5)
        tk.Label(
            frame,
            text=title,
            bg="#ff7043",
            fg="white",
            font=("Helvetica", 14, "bold")
        ).pack(fill="x")

        row = tk.Frame(frame, bg="#2e2e2e")
        row.pack(pady=10)

        for idx, group in enumerate(slots):
            col = tk.Frame(row, bg="#2e2e2e", padx=5)
            col.grid(row=0, column=idx * 2)

            # each portrait + name stacked
            for name, img_path in group:
                cf = tk.Frame(col, bg="#2e2e2e")
                cf.pack(pady=2)

                im = Image.open(img_path).resize((80, 80))
                ph = ImageTk.PhotoImage(im)
                lbl = tk.Label(cf, image=ph, bg="#2e2e2e")
                lbl.image = ph
                lbl.pack()
                tk.Label(cf, text=name, bg="#2e2e2e", fg="white",
                         font=("Helvetica", 9)).pack()

            # add vertical bar between slots
            if idx < len(slots) - 1:
                sep = tk.Frame(row, bg="#1e1e1e", width=2, height=110)
                sep.grid(row=0, column=idx * 2 + 1, padx=5)

        frame.pack(pady=5, fill="x")

    # ─── Utility: clear previous view ──────────────────────────────────────────
    def clear_frames(self):
        for frame in (self.main_frame, self.team_frame):
            frame.pack_forget()
            for w in frame.winfo_children():
                w.destroy()


if __name__ == "__main__":
    app = TeamBuilderApp()
    app.mainloop()
