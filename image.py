from PyQt5.QtCore import QPoint, QRect
from PyQt5.QtGui import (
    QColor,
    QImage,
    QPainter,
)


class Image(object):
    WIDTH = 256
    HEIGHT = 256

    def __init__(self, filename=None):
        self.filename = filename

        layer = QImage(
            self.WIDTH,
            self.HEIGHT,
            QImage.Format_ARGB32
        )

        if self.filename:
            layer.load(self.filename)
        else:
            painter = QPainter()
            painter.begin(layer)
            painter.fillRect(
                0,
                0,
                layer.width(),
                layer.height(),
                QColor(255, 255, 255)
            )
            painter.end()

        self.layers = [layer]
        self.current_layer = 0

    def width(self):
        return max(layer.width() for layer in self.layers)

    def height(self):
        return max(layer.height() for layer in self.layers)

    def draw_with_brush(self, brush, pos):
        painter = QPainter()
        painter.begin(self.layers[self.current_layer])
        painter.drawImage(
            pos,
            brush.image,
            QRect(0, 0, brush.width(), brush.height())
        )
        painter.end()

    def composited(self):
        target = QImage(self.width(), self.height(), QImage.Format_ARGB32)

        painter = QPainter()
        painter.begin(target)

        for layer in self.layers:
            painter.drawImage(
                QPoint(0, 0),
                layer,
                QRect(0, 0, layer.width(), layer.height())
            )

        painter.end()
        return target

    def save(self):
        self.composited().save(self.filename, format=None)
