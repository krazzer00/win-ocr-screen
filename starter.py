import subprocess
import psutil
from pynput import keyboard

process = None

def on_activate():
    global process

    for p in psutil.process_iter():
        if p.name() == "python.exe" and "ocr_screen.py" in " ".join(p.cmdline()):
            print("Program is already running")
            process.terminate()
            process = None
            return

    if process is None:
        process = subprocess.Popen(['C:/Users/krazz/AppData/Local/Programs/Python/Python310/python.exe', 'c:/Users/krazz/Desktop/ocr-screen-main/ocr_screen.py'])
    else:
        process.terminate()
        process = None

def on_exit():
    global process
    if process is not None:
        process.terminate()
    exit()

def register_listener():
    with keyboard.GlobalHotKeys({'<ctrl>+<alt>+o': on_activate, '<ctrl>+<alt>+p': on_exit}) as h:
        h.join()

# Start with a listener for the hotkeys
register_listener()
