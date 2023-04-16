import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QGraphicsScene, QGraphicsView, QRubberBand, QDesktopWidget
from PyQt5.QtGui import QPixmap, QPainter, QPen, QCursor
from PyQt5.QtCore import Qt, QPoint, QRect, QSize
from PIL import Image

import pyperclip
import pytesseract
from PyQt5 import QtWidgets

# Укажите путь к tesseract.exe
pytesseract.pytesseract.tesseract_cmd = r'D:\tesseract\tesseract.exe'

class MultiScreenSelection:
    def __init__(self):
        self.windows = []

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

        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)

        self.setGeometry(screen_geometry)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)

        self.origin = QPoint()

        self.setMouseTracking(True)
        self.grabMouse(Qt.CrossCursor)

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

            pixmap.save('screenshot.png', 'png')
            img = Image.open('screenshot.png')

            text = pytesseract.image_to_string(img, lang='rus+eng', config='--psm 6')
            pyperclip.copy(text)

            print("Распознанный текст:", text)

            self.rubber_band.hide()
            self.raise_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    multi_screen_selection = MultiScreenSelection()
    multi_screen_selection.show()
    sys.exit(app.exec_())