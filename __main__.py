import sys
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import (
    QColor,
    QImage,
    QPainter,
)
from PyQt5.QtWidgets import (
    QApplication,
    QDesktopWidget,
    QWidget,
)


APPLICATION_TITLE = 'Wiggle'
APPLICATION_VERSION = '0.1'


class Canvas(QWidget):
    WIDTH = 256
    HEIGHT = 256
    ZOOM = 4

    def __init__(self):
        super().__init__()

        # Data
        self.layers = []
        self.layers.append(
            QImage(
                self.WIDTH,
                self.HEIGHT,
                QImage.Format_ARGB32
            )
        )
        self.current_layer = 0

        red = QColor(255, 0, 0)
        transparent = QColor(0, 0, 0, 0)
        self.brush = QImage(3, 3, QImage.Format_ARGB32)
        self.brush.setPixelColor(0, 0, transparent)
        self.brush.setPixelColor(0, 1, red)
        self.brush.setPixelColor(0, 2, transparent)
        self.brush.setPixelColor(1, 0, red)
        self.brush.setPixelColor(1, 1, red)
        self.brush.setPixelColor(1, 2, red)
        self.brush.setPixelColor(2, 0, transparent)
        self.brush.setPixelColor(2, 1, red)
        self.brush.setPixelColor(2, 2, transparent)

        # Resize and center on the screen
        self.resize(self.WIDTH * self.ZOOM, self.HEIGHT * self.ZOOM)
        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())

        self.setWindowTitle(
            '{} v{}'.format(APPLICATION_TITLE, APPLICATION_VERSION))

        self.show()

    def mousePressEvent(self, event):
        painter = QPainter()
        painter.begin(self.layers[self.current_layer])
        painter.drawImage(
            event.pos() / self.ZOOM,
            self.brush,
            QRect(0, 0, self.brush.width(), self.brush.height())
        )
        painter.end()
        self.update()

    def mouseMoveEvent(self, event):
        is_left_button_pressed = \
            event.buttons() & Qt.LeftButton == Qt.LeftButton
        if not is_left_button_pressed:
            return

        painter = QPainter()
        painter.begin(self.layers[self.current_layer])
        painter.drawImage(
            event.pos() / self.ZOOM,
            self.brush,
            QRect(0, 0, self.brush.width(), self.brush.height())
        )
        painter.end()
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        for layer in self.layers:
            zoomed_layer = layer.scaled(
                layer.width() * self.ZOOM,
                layer.height() * self.ZOOM,
                Qt.IgnoreAspectRatio,
                Qt.FastTransformation
            )
            painter.drawImage(
                QPoint(0, 0),
                zoomed_layer,
                QRect(0, 0, zoomed_layer.width(), zoomed_layer.height())
            )

        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = Canvas()
    sys.exit(app.exec_())
