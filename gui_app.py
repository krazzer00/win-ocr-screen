import sys
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QTextEdit, QVBoxLayout
from PyQt5.QtCore import Qt
from pynput import keyboard

from ocr_screen import MultiScreenSelection


class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Win OCR Screen")
        self.resize(500, 300)

        self.text_edit = QTextEdit()
        self.capture_button = QPushButton("Capture Screen")

        layout = QVBoxLayout()
        layout.addWidget(self.capture_button)
        layout.addWidget(self.text_edit)
        self.setLayout(layout)

        self.capture_button.clicked.connect(self.start_capture)

        # Callback from screenshot windows
        self.multi_select = MultiScreenSelection(self.show_text)

        # Register global hotkeys
        self.listener = keyboard.GlobalHotKeys({
            '<ctrl>+<alt>+o': self.start_capture,
            '<ctrl>+<alt>+p': self.close_app
        })
        self.listener.start()

    def show_text(self, text: str):
        self.text_edit.setPlainText(text)

    def start_capture(self):
        # Use a thread to avoid blocking the UI
        threading.Thread(target=self.multi_select.show, daemon=True).start()

    def close_app(self):
        self.listener.stop()
        self.close()


def main():
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
