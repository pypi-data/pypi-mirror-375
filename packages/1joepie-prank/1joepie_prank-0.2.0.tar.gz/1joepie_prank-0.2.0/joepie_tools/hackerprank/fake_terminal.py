"""Fake terminal with typing effect and random 'commands' + fake outputs."""
import tkinter as tk
import random, time, threading

COMMANDS = [
    "nmap -sS 192.168.1.0/24",
    "ssh root@192.168.0.1",
    "cat /etc/passwd",
    "sudo echo 'simulate' > /dev/null",
    "grep -R 'password' /home",
    "python3 exploit.py --target 10.0.0.5"
]

OUTPUTS = [
    "ESTABLISHING CONNECTION...",
    "AUTH SUCCESS: root",
    "FILE: /etc/passwd\nroot:x:0:0:root:/root:/bin/bash",
    "SCAN REPORT: 34 hosts up",
    "ERROR: permission denied",
    "EXPLOIT RUNNING... DONE"
]

def _type_text(text_widget, text, delay=25, stop_event=None):
    def run(i=0):
        if stop_event and stop_event.is_set():
            return
        if i < len(text):
            try:
                text_widget.insert("end", text[i])
                text_widget.see("end")
            except Exception:
                pass
            text_widget.after(delay, run, i+1)
    run()

def fake_terminal(duration: float = 10.0):
    stop_event = threading.Event()
    root = tk.Tk()
    root.title("Terminal — joepie_tools")
    txt = tk.Text(root, bg="black", fg="lime", font=("Courier", 11))
    txt.pack(expand=True, fill="both")
    start = time.time()

    def close():
        stop_event.set()
        try:
            root.destroy()
        except Exception:
            pass

    root.protocol("WM_DELETE_WINDOW", close)

    def chat_loop():
        if stop_event.is_set():
            close(); return
        if time.time() - start < duration:
            cmd = random.choice(COMMANDS)
            _type_text(txt, f"$ {cmd}\n", delay=20, stop_event=stop_event)
            txt.after(600 + random.randint(0,500), lambda: _type_text(txt, random.choice(OUTPUTS) + "\n\n", delay=8, stop_event=stop_event))
            txt.after(1200 + random.randint(0,1200), chat_loop)
        else:
            close()
    chat_loop()
    try:
        root.mainloop()
    finally:
        stop_event.set()
