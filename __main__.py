import os
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
    QFileDialog,
    QWidget,
)


APPLICATION_TITLE = 'Wiggle'
APPLICATION_VERSION = '0.1'


class Brush(QImage):
    def __init__(self):
        super().__init__(3, 3, QImage.Format_ARGB32)

        red = QColor(255, 0, 0)
        transparent = QColor(0, 0, 0, 0)

        self.setPixelColor(0, 0, transparent)
        self.setPixelColor(0, 1, red)
        self.setPixelColor(0, 2, transparent)
        self.setPixelColor(1, 0, red)
        self.setPixelColor(1, 1, red)
        self.setPixelColor(1, 2, red)
        self.setPixelColor(2, 0, transparent)
        self.setPixelColor(2, 1, red)
        self.setPixelColor(2, 2, transparent)


class Image(object):
    WIDTH = 256
    HEIGHT = 256

    def __init__(self):
        self.filename = None

        layer = QImage(
            self.WIDTH,
            self.HEIGHT,
            QImage.Format_ARGB32
        )

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

        self.brush = Brush()

    def width(self):
        return self.WIDTH

    def height(self):
        return self.HEIGHT

    def draw_with_brush(self, pos):
        painter = QPainter()
        painter.begin(self.layers[self.current_layer])
        painter.drawImage(
            pos,
            self.brush,
            QRect(0, 0, self.brush.width(), self.brush.height())
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


class Canvas(QWidget):
    ZOOM = 4

    def __init__(self):
        super().__init__()
        self.image = Image()

        # Resize and center on the screen
        self.resize(
            self.image.width() * self.ZOOM,
            self.image.height() * self.ZOOM
        )

        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())

        self.setWindowTitle(
            '{} v{}'.format(APPLICATION_TITLE, APPLICATION_VERSION))

        self.show()

    def mousePressEvent(self, event):
        self.image.draw_with_brush(event.pos() / self.ZOOM)
        self.update()

    def mouseMoveEvent(self, event):
        is_left_button_pressed = \
            event.buttons() & Qt.LeftButton == Qt.LeftButton
        if not is_left_button_pressed:
            return

        self.image.draw_with_brush(event.pos() / self.ZOOM)
        self.update()

    def paintEvent(self, event):
        composited = \
            self.image.composited().scaled(
                self.image.width() * self.ZOOM,
                self.image.height() * self.ZOOM,
                Qt.IgnoreAspectRatio,
                Qt.FastTransformation
            )

        painter = QPainter()
        painter.begin(self)
        painter.drawImage(
            QPoint(0, 0),
            composited,
            QRect(0, 0, composited.width(), composited.height())
        )
        painter.end()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_S and \
                bool(event.modifiers() and Qt.ControlModifier) and \
                self.capture_filename_if_necessary():
            self.image.save()
            print('saved to {}'.format(self.image.filename))

    def capture_filename_if_necessary(self):
        if self.image.filename:
            return True

        filename = QFileDialog.getSaveFileName(
            self,
            'Save image',
            os.getcwd(),
            'PNG images (*.png)'
        )[0]

        if filename:
            self.image.filename = filename
            return True

        return False


if __name__ == '__main__':
    app = QApplication(sys.argv)
    canvas = Canvas()
    sys.exit(app.exec_())
