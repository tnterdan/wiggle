from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor,
    QPainter,
)
from PyQt5.QtWidgets import (
    QAction,
    QWidget,
)


class Swatches(QWidget):
    def __init__(self, app):
        super().__init__()

        # Swatches
        self.swatches = [
            ColorSwatch(QColor(0, 0, 0), 0, self, app),
            ColorSwatch(QColor(255, 255, 255), 1, self, app),
            ColorSwatch(QColor(212, 64, 16), 2, self, app),
            ColorSwatch(QColor(64, 128, 212), 3, self, app),
        ]

        self.setMinimumWidth(256)
        self.setMinimumHeight(34)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)

        for swatch in self.swatches:
            swatch.draw(painter)

        painter.end()

    def mousePressEvent(self, event):
        if event.button() != Qt.LeftButton:
            return

        swatch_index = event.x() // ColorSwatch.WIDTH

        if swatch_index > len(self.swatches):
            return

        self.swatches[swatch_index].switch_action.trigger()


class ColorSwatch(object):
    WIDTH = 32
    HEIGHT = 32

    def __init__(self, color, index, parent_widget, app):
        self.color = color
        self.index = index

        self.switch_action = QAction('Select Color', parent_widget)
        self.switch_action.setStatusTip('Select color')
        self.switch_action.triggered.connect(
            lambda: app.switch_brush_color(self.color))

    def draw(self, painter):
        painter.fillRect(
            self.index * self.WIDTH,
            0,
            self.WIDTH,
            self.HEIGHT,
            self.color
        )
        painter.drawRect(
            self.index * self.WIDTH,
            0,
            self.WIDTH,
            self.HEIGHT
        )
