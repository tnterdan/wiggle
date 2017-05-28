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
    SCALE = 4

    def __init__(self):
        super().__init__()

        # Data
        self.layers = []
        self.layers.append(
            QImage(
                self.WIDTH * self.SCALE,
                self.HEIGHT * self.SCALE,
                QImage.Format_ARGB32
            )
        )
        self.current_layer = 0

        red = QColor(255, 0, 0)
        transparent = QColor(0, 0, 0, 0)
        unscaled_brush = QImage(3, 3, QImage.Format_ARGB32)
        unscaled_brush.setPixelColor(0, 0, transparent)
        unscaled_brush.setPixelColor(0, 1, red)
        unscaled_brush.setPixelColor(0, 2, transparent)
        unscaled_brush.setPixelColor(1, 0, red)
        unscaled_brush.setPixelColor(1, 1, red)
        unscaled_brush.setPixelColor(1, 2, red)
        unscaled_brush.setPixelColor(2, 0, transparent)
        unscaled_brush.setPixelColor(2, 1, red)
        unscaled_brush.setPixelColor(2, 2, transparent)
        self.brush = unscaled_brush.scaled(
            unscaled_brush.width() * self.SCALE,
            unscaled_brush.height() * self.SCALE,
            Qt.IgnoreAspectRatio,
            Qt.FastTransformation
        )

        # Resize and center on the screen
        self.resize(self.WIDTH * self.SCALE, self.HEIGHT * self.SCALE)
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
            event.pos(),
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
            event.pos(),
            self.brush,
            QRect(0, 0, self.brush.width(), self.brush.height())
        )
        painter.end()
        self.update()

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        for layer in self.layers:
            painter.drawImage(
                QPoint(10, 10),
                layer,
                QRect(0, 0, layer.width(), layer.height())
            )

        painter.end()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = Canvas()
    sys.exit(app.exec_())
