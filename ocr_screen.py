import sys
import os
import threading
import tempfile
import logging
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QGraphicsScene,
    QGraphicsView,
    QRubberBand,
    QDesktopWidget,
)
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PIL import Image

import pyperclip
import pytesseract
from PyQt5 import QtWidgets
import requests
import zipfile
import io

# Default OCR languages
OCR_LANGS = os.getenv("OCR_LANGS", "rus+eng")

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

# Directory where the application stores additional files
def get_app_dir() -> str:
    """Return path to directory near the executable for storing resources."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.abspath(os.path.dirname(__file__))


APP_DIR = get_app_dir()
WORK_DIR = os.path.join(APP_DIR, "app_data")
TESSERACT_DIR = os.path.join(WORK_DIR, "tesseract")
TESSERACT_EXE = os.path.join(TESSERACT_DIR, "tesseract.exe")


def ensure_tesseract() -> str:
    """Download portable Tesseract if not available and return executable path."""
    if os.path.exists(TESSERACT_EXE):
        return TESSERACT_EXE

    os.makedirs(TESSERACT_DIR, exist_ok=True)
    url = os.getenv(
        "TESSERACT_DOWNLOAD_URL",
        "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.1/tesseract-5.3.1-windows-x64-portable.zip",
    )
    logging.info("Downloading Tesseract from %s", url)
    try:
        resp = requests.get(url, timeout=60)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            zf.extractall(TESSERACT_DIR)
    except Exception as exc:
        logging.error("Failed to download Tesseract: %s", exc)
        return "tesseract"
    return TESSERACT_EXE



def configure_tesseract() -> None:
    """Configure pytesseract command from environment or download."""
    tesseract_from_env = os.getenv("TESSERACT_PATH")
    if tesseract_from_env:
        pytesseract.pytesseract.tesseract_cmd = tesseract_from_env
    else:
        pytesseract.pytesseract.tesseract_cmd = ensure_tesseract()


configure_tesseract()


def translate_text(text: str, target: str) -> str:
    """Translate text using a free online service."""
    params = {"q": text, "langpair": f"auto|{target}"}
    resp = requests.get("https://api.mymemory.translated.net/get", params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    return data.get("responseData", {}).get("translatedText", "")

class MultiScreenSelection:
    def __init__(self, text_callback=None):
        self.windows = []
        self.text_callback = text_callback

    def show(self):
        desktop = QDesktopWidget()
        for screen_number in range(desktop.screenCount()):
            screen_geometry = desktop.screenGeometry(screen_number)
            window = Window(screen_geometry, self)
            window.show()
            self.windows.append(window)

    def hide(self):
        for window in self.windows:
            window.hide()

class Window(QMainWindow):
    def __init__(self, screen_geometry, multi_screen_selection):
        super().__init__()

        self.multi_screen_selection = multi_screen_selection
        self.text_callback = multi_screen_selection.text_callback

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setGeometry(screen_geometry)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        self.origin = QPoint()

        self.setMouseTracking(True)
        self.grabMouse(Qt.CrossCursor)

    def perform_ocr(self, image_path: str):
        """Run OCR on the saved screenshot and copy result to clipboard."""
        try:
            img = Image.open(image_path)
            langs = os.getenv("OCR_LANGS", OCR_LANGS)
            text = pytesseract.image_to_string(img, lang=langs, config='--psm 6')
            target = os.getenv("TRANSLATE_TO")
            if target:
                try:
                    translation = translate_text(text, target)
                    text += f"\n\nTranslated ({target}):\n{translation}"
                except Exception as exc:
                    logging.error("Translation failed: %s", exc)
            pyperclip.copy(text)
            logging.info("Распознанный текст: %s", text)
            if self.text_callback:
                self.text_callback(text)
        except pytesseract.TesseractNotFoundError:
            logging.error("Tesseract not found. Set TESSERACT_PATH environment variable.")
        except Exception as exc:
            logging.exception("OCR processing failed: %s", exc)
        finally:
            try:
                os.remove(image_path)
            except OSError:
                pass

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setOpacity(0.4)
        painter.setBrush(Qt.gray)
        painter.drawRect(self.rect())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.origin = event.pos()
            self.rubber_band.setGeometry(QRect(self.origin, QSize()))
            self.rubber_band.show()

    def mouseMoveEvent(self, event):
        if not self.origin.isNull():
            self.rubber_band.setGeometry(QRect(self.origin, event.pos()).normalized())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.releaseMouse()

            rect = self.rubber_band.geometry()

            screen_number = QApplication.desktop().screenNumber(QCursor().pos())
            screen = QtWidgets.QApplication.screens()[screen_number]
            pixmap = screen.grabWindow(0, rect.x(), rect.y(), rect.width(), rect.height())

            # Save screenshot to a temporary file
            tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png", prefix="screenshot_temp_")
            tmp_file_path = tmp_file.name
            tmp_file.close()
            pixmap.save(tmp_file_path, 'png')

            # Run OCR in a separate thread
            threading.Thread(target=self.perform_ocr, args=(tmp_file_path,), daemon=True).start()

            self.rubber_band.hide()
            self.raise_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    multi_screen_selection = MultiScreenSelection()
    multi_screen_selection.show()
    sys.exit(app.exec_())
