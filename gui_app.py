import sys
import os
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QSystemTrayIcon,
    QMenu,
    QAction,
    QDialog,
    QLineEdit,
    QFormLayout,
    QDialogButtonBox,
)
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSettings
from pynput import keyboard

from ocr_screen import MultiScreenSelection, configure_tesseract


class SettingsDialog(QDialog):
    def __init__(self, settings: QSettings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Settings")

        self.lang_edit = QLineEdit(settings.value("lang", "rus+eng"))
        self.tesseract_edit = QLineEdit(settings.value("tesseract", ""))

        layout = QFormLayout()
        layout.addRow("OCR languages", self.lang_edit)
        layout.addRow("Tesseract path", self.tesseract_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        self.settings.setValue("lang", self.lang_edit.text())
        self.settings.setValue("tesseract", self.tesseract_edit.text())
        super().accept()


class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Win OCR Screen")
        self.resize(500, 300)

        self.settings = QSettings("WinOCR", "WinOCR")
        os.environ.setdefault("OCR_LANGS", self.settings.value("lang", "rus+eng"))
        tess_path = self.settings.value("tesseract", "")
        if tess_path:
            os.environ["TESSERACT_PATH"] = tess_path
        configure_tesseract()

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
            '<ctrl>+<alt>+p': self.exit_app,
        })
        self.listener.start()

        # System tray
        self.tray = QSystemTrayIcon(QIcon("screenshot.png"), self)
        menu = QMenu()
        menu.addAction(QAction("Capture", self, triggered=self.start_capture))
        menu.addAction(QAction("Settings", self, triggered=self.open_settings))
        menu.addSeparator()
        menu.addAction(QAction("Exit", self, triggered=self.exit_app))
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(self.on_tray_activated)
        self.tray.show()

    def show_text(self, text: str):
        self.text_edit.setPlainText(text)

    def start_capture(self):
        # Use a thread to avoid blocking the UI
        threading.Thread(target=self.multi_select.show, daemon=True).start()

    def on_tray_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            if self.isVisible():
                self.hide()
            else:
                self.showNormal()

    def open_settings(self):
        dlg = SettingsDialog(self.settings, self)
        if dlg.exec_():
            os.environ["OCR_LANGS"] = self.settings.value("lang", "rus+eng")
            tess = self.settings.value("tesseract", "")
            if tess:
                os.environ["TESSERACT_PATH"] = tess
            configure_tesseract()

    def exit_app(self):
        self.listener.stop()
        self.tray.hide()
        self.close()

    def closeEvent(self, event):
        self.hide()
        event.ignore()


def main():
    app = QApplication(sys.argv)
    window = OCRApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
