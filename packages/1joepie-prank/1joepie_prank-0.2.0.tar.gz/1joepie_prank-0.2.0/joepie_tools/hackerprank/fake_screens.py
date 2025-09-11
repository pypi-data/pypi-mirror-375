"""Multiple fake terminal windows with progress bars and messages."""
import tkinter as tk
from tkinter import ttk
import random, time, threading, logging

logger = logging.getLogger(__name__)

MESSAGES = [
    "Access Granted", "Decrypting files...", "Bypassing firewall...",
    "Scanning ports...", "Injecting payload...", "Root access obtained",
    "Downloading secrets...", "Establishing backdoor...", "Dumping memory..."
]

def _create_toplevel(root, title, duration, stop_event):
    win = tk.Toplevel(root)
    win.title(title)
    win.geometry("520x150")
    try:
        win.attributes("-topmost", True)
    except Exception:
        pass
    lbl = tk.Label(win, text=random.choice(MESSAGES), font=("Courier", 12))
    lbl.pack(pady=8)
    progress = ttk.Progressbar(win, orient="horizontal", mode="determinate", length=420, maximum=100)
    progress.pack(pady=6)

    start = time.time()
    def update():
        if stop_event.is_set():
            try:
                win.destroy()
            except Exception:
                pass
            return
        elapsed = time.time() - start
        pct = min(100, (elapsed / max(0.1, duration)) * 100)
        try:
            progress['value'] = pct
        except Exception:
            pass
        if int(elapsed * 2) % 2 == 0:
            try:
                lbl.config(text=random.choice(MESSAGES))
            except Exception:
                pass
        if elapsed < duration:
            win.after(150, update)
        else:
            try:
                win.destroy()
            except Exception:
                pass
    win.after(100, update)
    return win

def fake_hack_screen(num_windows: int = 3, duration: float = 8.0):
    try:
        num_windows = max(1, min(8, int(num_windows)))
        duration = max(1.0, float(duration))
    except Exception:
        num_windows = 3
        duration = 8.0

    stop_event = threading.Event()

    root = tk.Tk()
    root.withdraw()
    wins = []
    for i in range(num_windows):
        d = duration + random.uniform(-2.0, 2.0)
        wins.append(_create_toplevel(root, f"Terminal-{i+1}", abs(d), stop_event))

    root.deiconify()
    root.title("joepie_tools — prank running")
    root.geometry("360x110")
    lbl = tk.Label(root, text="Fake hack running — press STOP to close everything", font=("Helvetica", 10))
    lbl.pack(pady=6)
    def _stop():
        stop_event.set()
        try:
            root.quit()
        except Exception:
            pass
    stop_btn = tk.Button(root, text="STOP", command=_stop)
    stop_btn.pack()
    root.protocol("WM_DELETE_WINDOW", _stop)
    try:
        root.mainloop()
    finally:
        stop_event.set()
        for w in root.winfo_children():
            try:
                w.destroy()
            except Exception:
                pass
        try:
            root.destroy()
        except Exception:
            pass
