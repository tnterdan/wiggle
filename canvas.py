import os

from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import (
    QPainter,
    QPalette,
)
from PyQt5.QtWidgets import (
    QFileDialog,
    QMainWindow,
    QScrollArea,
)

from image import Image


class Canvas(QMainWindow):
    ZOOM = 4

    @classmethod
    def scrollable(cls, app, filename=None):
        window = QScrollArea()

        window.setBackgroundRole(QPalette.Midlight)
        window.setWidget(cls(app, filename))
        window.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        window.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return window

    def __init__(self, app, filename=None):
        super().__init__()
        self.app = app
        self.image = Image(filename)
        self.resize(self.width(), self.height())
        self.show()

    def width(self):
        return self.image.width() * self.ZOOM

    def height(self):
        return self.image.height() * self.ZOOM

    def mousePressEvent(self, event):
        self.image.draw_with_brush(self.app.brush, event.pos() / self.ZOOM)
        self.update()

    def mouseMoveEvent(self, event):
        is_left_button_pressed = \
            event.buttons() & Qt.LeftButton == Qt.LeftButton
        if not is_left_button_pressed:
            return

        self.image.draw_with_brush(self.app.brush, event.pos() / self.ZOOM)
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
                bool(event.modifiers() and Qt.ControlModifier):
            self.save()

    def save(self):
        if self.capture_filename_if_necessary():
            self.image.save()
            return self.image.filename
        return None

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
