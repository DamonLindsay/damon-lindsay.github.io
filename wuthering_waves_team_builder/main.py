import tkinter as tk
from tkinter import ttk
from characters import character_data


def show_teammates(event):
    selected = character_select.get()
    info = character_data.get(selected)
    if info:
        role_label.config(text=f"Role: {info['role']}")
        teammates = ", ".join(info['meta_teammates'])
        teammates_label.config(text=f"Meta Teammates: {teammates}")
    else:
        role_label.config(text="")
        teammates_label.config(text="")


app = tk.Tk()
app.title("Wuthering Waves Team Builder")

tk.Label(app, text="Select a Character:").pack(pady=5)
character_select = ttk.Combobox(app, values=list(character_data.keys()))
character_select.pack()
character_select.bind("<<ComboboxSelected>>", show_teammates)

role_label = tk.Label(app, text="", font=("Helvetica", 12))
role_label.pack(pady=10)

teammates_label = tk.Label(app, text="", font=("Helvetica", 12))
teammates_label.pack(pady=10)

app.mainloop()
