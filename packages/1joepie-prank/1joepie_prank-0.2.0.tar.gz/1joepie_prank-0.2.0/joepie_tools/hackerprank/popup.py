"""A harmless fake warning popup that auto-closes."""
import tkinter as tk
import threading, time

def fake_warning_popup(message: str = "Warning: Unauthorized access", duration: float = 4.0):
    def _show():
        root = tk.Tk()
        root.title("System Alert")
        root.geometry("420x120")
        lbl = tk.Label(root, text=message, font=("Helvetica", 12), fg="red")
        lbl.pack(pady=12)
        btn = tk.Button(root, text="OK (just kidding)", command=root.destroy)
        btn.pack()
        def auto_close():
            time.sleep(max(0.5, duration))
            try:
                root.destroy()
            except Exception:
                pass
        t = threading.Thread(target=auto_close, daemon=True)
        t.start()
        try:
            root.mainloop()
        except Exception:
            pass
    threading.Thread(target=_show, daemon=True).start()
