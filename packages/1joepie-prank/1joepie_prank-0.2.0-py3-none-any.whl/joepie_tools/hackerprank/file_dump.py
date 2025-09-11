"""Fake file-dump window: shows fake filenames and hex-like lines."""
import tkinter as tk
import random, time

FILENAMES = ["passwords.txt","secrets.db","tokens.json","wallet.dump","notes.txt","credentials.csv","db_backup.sql"]

def _random_filename():
    return random.choice(FILENAMES)

def _random_hex_line():
    return " ".join(f"{random.randint(0,255):02x}" for _ in range(12))

def fake_file_dump(duration: float = 6.0):
    root = tk.Tk()
    root.title("FileDump — joepie_tools")
    text = tk.Text(root, font=("Courier", 10))
    text.pack(expand=True, fill="both")
    start = time.time()

    def update():
        if time.time() - start < duration:
            text.insert("end", f"--- Opening {_random_filename()} ---\n")
            for _ in range(random.randint(6,12)):
                text.insert("end", _random_hex_line() + "\n")
            text.insert("end", "\n")
            text.see("end")
            root.after(500, update)
        else:
            try:
                root.destroy()
            except Exception:
                pass
    update()
    root.mainloop()
