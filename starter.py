import subprocess
import psutil
import os
import sys
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
        python_executable = os.getenv("PYTHON_EXECUTABLE", sys.executable)
        script_path = os.getenv(
            "OCR_SCREEN_SCRIPT",
            os.path.join(os.path.dirname(__file__), "ocr_screen.py"),
        )
        process = subprocess.Popen([python_executable, script_path])
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
