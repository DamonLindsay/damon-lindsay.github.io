import tkinter as tk
from PIL import Image, ImageTk
from characters import characters


class TeamBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wuthering Waves Team Builder")
        self.configure(bg="#1e1e1e")
        # totally borderless
        self.overrideredirect(True)
        # let Tk calculate your actual screen size
        self.update_idletasks()
        w = self.winfo_screenwidth()
        h = self.winfo_screenheight()
        # cover the whole screen
        self.geometry(f"{w}x{h}+0+0")
        # allow Escape to quit in case you need to exit during dev
        self.bind("<Escape>", lambda e: self.destroy())

        self.main_frame = tk.Frame(self, bg="#1e1e1e")
        self.team_frame = tk.Frame(self, bg="#1e1e1e")

        self.show_character_grid()

    def show_character_grid(self):
        self.clear_frames()
        self.main_frame.pack()

        row, col = 0, 0
        for name, info in characters.items():
            img = Image.open(info["image"]).resize((100, 100))
            photo = ImageTk.PhotoImage(img)

            frame = tk.Frame(self.main_frame, bg="#1e1e1e", padx=10, pady=10)
            btn = tk.Button(frame, image=photo, command=lambda n=name: self.show_teams(n), bg="#1e1e1e", bd=0)
            btn.image = photo
            btn.pack()
            tk.Label(frame, text=name, bg="#1e1e1e", fg="white").pack()

            frame.grid(row=row, column=col)

            col += 1
            if col > 5:
                col = 0
                row += 1

    def show_teams(self, character_name):
        self.clear_frames()
        # show the team_frame
        self.team_frame.pack(fill="both", expand=True)

        # make a centered content container
        container = tk.Frame(self.team_frame, bg="#1e1e1e")
        container.place(relx=0.5, rely=0.5, anchor="center")  # absolute centering

        # scrollable canvas inside that container
        canvas = tk.Canvas(container, bg="#1e1e1e", highlightthickness=0,
                           width=900, height=700)  # tweak width/height
        vsb = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        # make the canvas cell expand if you resize
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # the interior frame
        scrollable = tk.Frame(canvas, bg="#1e1e1e")
        canvas.create_window((0, 0), window=scrollable, anchor="nw")
        scrollable.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        # back button
        tk.Button(scrollable, text="Back", command=self.show_character_grid) \
            .pack(anchor="w", padx=10, pady=10)

        data = characters[character_name]
        if "note" in data:
            tk.Label(scrollable, text=data["note"].replace("**", ""),
                     wraplength=850, justify="left",
                     bg="#1e1e1e", fg="white", font=("Helvetica", 12),
                     padx=10, pady=10).pack(fill="x", padx=20, pady=20)
            return

        for team in data["teams"]:
            self.create_team_section(scrollable, team["title"], team["slots"])

    def create_team_section(self, parent, title, slots):
        frame = tk.Frame(parent, bg="#2e2e2e", pady=5)
        tk.Label(frame, text=title, bg="#ff7043", fg="white", font=("Helvetica", 14, "bold")).pack(fill="x")

        row = tk.Frame(frame, bg="#2e2e2e")
        row.pack(pady=10)

        for idx, group in enumerate(slots):
            col = tk.Frame(row, bg="#2e2e2e", padx=5)
            col.grid(row=0, column=idx * 2)

            # Character stack
            for name, img_path in group:
                char_frame = tk.Frame(col, bg="#2e2e2e")
                char_frame.pack(pady=2)

                img = Image.open(img_path).resize((80, 80))
                photo = ImageTk.PhotoImage(img)

                img_label = tk.Label(char_frame, image=photo, bg="#2e2e2e")
                img_label.image = photo
                img_label.pack()

                name_label = tk.Label(char_frame, text=name, fg="white", bg="#2e2e2e", font=("Helvetica", 9))
                name_label.pack()

            # Add vertical separator if not last
            if idx < len(slots) - 1:
                separator = tk.Frame(row, bg="#1e1e1e", width=2, height=110)
                separator.grid(row=0, column=idx * 2 + 1, padx=5)

        frame.pack(pady=5, fill="x")

    def clear_frames(self):
        for frame in (self.main_frame, self.team_frame):
            frame.pack_forget()
            for widget in frame.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    app = TeamBuilderApp()
    app.mainloop()
