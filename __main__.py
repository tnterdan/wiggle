import os
import sys

from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QImage,
    QPainter,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDesktopWidget,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QWidget,
)


APPLICATION_TITLE = 'Wiggle'
APPLICATION_VERSION = '0.1'


class ColorSwatch(object):
    WIDTH = 32
    HEIGHT = 32

    def __init__(self, color, index, parent_widget, canvas_widget):
        self.color = color
        self.index = index

        self.switch_action = QAction('Select Color', parent_widget)
        self.switch_action.setStatusTip('Select color')
        self.switch_action.triggered.connect(
            lambda: canvas_widget.switch_brush_color(self.color))

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


class Wiggle(QMainWindow):
    def __init__(self):
        super().__init__()

        self.canvas = Canvas()
        self.setCentralWidget(self.canvas)

        saveAction = QAction(QIcon.fromTheme('document-save'), 'Save', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Save image')
        saveAction.triggered.connect(self.save)

        self.statusbar = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(saveAction)

        toolbar = self.addToolBar('Main')
        toolbar.addAction(saveAction)

        self.swatches = Swatches(self.canvas)
        swatches_menu = QDockWidget(self)
        swatches_menu.setFeatures(QDockWidget.DockWidgetVerticalTitleBar)
        swatches_menu.setWidget(self.swatches)
        self.addDockWidget(Qt.TopDockWidgetArea, swatches_menu)

        # Resize and center on the screen
        self.resize(
            self.canvas.width(),
            self.canvas.height()
        )

        geom = self.frameGeometry()
        geom.moveCenter(QDesktopWidget().availableGeometry().center())
        self.move(geom.topLeft())

        self.setWindowTitle(
            '{} v{}'.format(APPLICATION_TITLE, APPLICATION_VERSION))

        self.show()

    def save(self):
        self.statusbar.clearMessage()
        saved_filename = self.canvas.save()
        if saved_filename:
            self.statusbar.showMessage('Saved to {}'.format(saved_filename))


class Swatches(QWidget):
    def __init__(self, canvas_widget):
        super().__init__()

        # Swatches
        self.swatches = [
            ColorSwatch(QColor(0, 0, 0), 0, self, canvas_widget),
            ColorSwatch(QColor(255, 255, 255), 1, self, canvas_widget),
            ColorSwatch(QColor(212, 64, 16), 2, self, canvas_widget),
            ColorSwatch(QColor(64, 128, 212), 3, self, canvas_widget),
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


class Canvas(QWidget):
    ZOOM = 4

    def __init__(self):
        super().__init__()
        self.image = Image()

    def width(self):
        return self.image.width() * self.ZOOM

    def height(self):
        return self.image.height() * self.ZOOM

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

    def switch_brush_color(self, color):
        print('Switch brush color')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wiggle = Wiggle()
    sys.exit(app.exec_())
