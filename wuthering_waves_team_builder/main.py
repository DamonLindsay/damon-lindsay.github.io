import tkinter as tk
from PIL import Image, ImageTk
from characters import characters


class TeamBuilderApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Wuthering Waves Team Builder")
        self.configure(bg="#1e1e1e")
        self.geometry("1000x800")

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
        self.team_frame.pack()

        tk.Button(self.team_frame, text="Back", command=self.show_character_grid).pack(anchor="w", padx=10, pady=10)

        for team in characters[character_name]["teams"]:
            self.create_team_section(self.team_frame, team["title"], team["slots"])

    def create_team_section(self, parent, title, slots):
        frame = tk.Frame(parent, bg="#2e2e2e", pady=10)
        tk.Label(frame, text=title, bg="#ff7043", fg="white", font=("Helvetica", 14, "bold")).pack(fill="x")

        row = tk.Frame(frame, bg="#2e2e2e")
        row.pack(pady=10)

        for idx, group in enumerate(slots):
            col = tk.Frame(row, bg="#2e2e2e")
            col.grid(row=0, column=idx, padx=20)
            for name, img_path in group:
                img = Image.open(img_path).resize((100, 100))
                photo = ImageTk.PhotoImage(img)
                label = tk.Label(col, image=photo, bg="#2e2e2e")
                label.image = photo
                label.pack()
                tk.Label(col, text=name, fg="white", bg="#2e2e2e").pack()

        frame.pack(pady=10, fill="x")

    def clear_frames(self):
        for frame in (self.main_frame, self.team_frame):
            frame.pack_forget()
            for widget in frame.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    app = TeamBuilderApp()
    app.mainloop()
