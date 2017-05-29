import os
import sys

from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QImage,
    QPainter,
    QPalette,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMdiArea,
    QScrollArea,
    QWidget,
)


APPLICATION_TITLE = 'Wiggle'
APPLICATION_VERSION = '0.1'


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

    def width(self):
        return self.WIDTH

    def height(self):
        return self.HEIGHT

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


class Wiggle(QMainWindow):
    def __init__(self):
        super().__init__()

        self.brush = Brush(QColor(255, 0, 0))

        self.document_area = QMdiArea()
        self.setCentralWidget(self.document_area)

        self.documents = []
        self.current_document = 0
        self.add_empty_canvas()

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

        self.swatches = Swatches(self)
        swatches_menu = QDockWidget(self)
        swatches_menu.setFeatures(QDockWidget.DockWidgetVerticalTitleBar)
        swatches_menu.setWidget(self.swatches)
        self.addDockWidget(Qt.TopDockWidgetArea, swatches_menu)

        self.setWindowTitle(
            '{} v{}'.format(APPLICATION_TITLE, APPLICATION_VERSION))

        self.showMaximized()

    def add_empty_canvas(self):
        CANVAS_PADDING = 60
        canvas = Canvas.scrollable(self)

        self.document_area \
            .addSubWindow(canvas) \
            .resize(
                canvas.widget().width() + CANVAS_PADDING,
                canvas.widget().height() + CANVAS_PADDING
            )

        self.documents.append(canvas.widget())
        self.current_document = len(self.documents) - 1

    def get_current_document(self):
        if self.documents:
            return self.documents[self.current_document]
        return None

    def save(self):
        self.statusbar.clearMessage()

        document = self.get_current_document()
        if document:
            saved_filename = document.save()
        if saved_filename:
            self.statusbar.showMessage('Saved to {}'.format(saved_filename))

    def switch_brush_color(self, color):
        self.brush = Brush(color)


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


class Canvas(QMainWindow):
    ZOOM = 4

    @classmethod
    def scrollable(cls, app):
        window = QScrollArea()

        window.setBackgroundRole(QPalette.Midlight)
        window.setWidget(cls(app))
        window.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        window.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        return window

    def __init__(self, app):
        super().__init__()
        self.app = app
        self.image = Image()
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wiggle = Wiggle()
    sys.exit(app.exec_())
