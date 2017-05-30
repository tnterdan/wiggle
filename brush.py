from PyQt5.QtGui import (
    QColor,
    QImage,
)


class Brush(object):
    def __init__(self, color):
        self.image = QImage(3, 3, QImage.Format_ARGB32)

        transparent = QColor(0, 0, 0, 0)

        self.image.setPixelColor(0, 0, transparent)
        self.image.setPixelColor(0, 1, color)
        self.image.setPixelColor(0, 2, transparent)
        self.image.setPixelColor(1, 0, color)
        self.image.setPixelColor(1, 1, color)
        self.image.setPixelColor(1, 2, color)
        self.image.setPixelColor(2, 0, transparent)
        self.image.setPixelColor(2, 1, color)
        self.image.setPixelColor(2, 2, transparent)

    def width(self):
        return self.image.width()

    def height(self):
        return self.image.height()
