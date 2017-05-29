import os
import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import (
    QColor,
    QIcon,
    QPainter,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QDockWidget,
    QFileDialog,
    QMainWindow,
    QMdiArea,
    QWidget,
)

from brush import Brush
from canvas import Canvas


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


class OpenedImage(object):
    def __init__(self, mdi_window):
        self.window = mdi_window

    def canvas(self):
        # The MDI window's widget is a scroll area, and the scroll area's
        # widget is the actual canvas.
        return self.window.widget().widget()

    def filename(self):
        return self.canvas().image.filename


class Wiggle(QMainWindow):
    def __init__(self):
        super().__init__()

        self.brush = Brush(QColor(255, 0, 0))

        self.document_area = QMdiArea()
        self.setCentralWidget(self.document_area)

        self.documents = []
        self.current_document = 0
        self.add_empty_canvas()

        open_action = QAction(QIcon.fromTheme('document-open'), 'Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.setStatusTip('Open image')
        open_action.triggered.connect(self.open)

        save_action = QAction(QIcon.fromTheme('document-save'), 'Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.setStatusTip('Save image')
        save_action.triggered.connect(self.save)

        self.statusbar = self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(open_action)
        fileMenu.addAction(save_action)

        toolbar = self.addToolBar('Main')
        toolbar.addAction(open_action)
        toolbar.addAction(save_action)

        self.swatches = Swatches(self)
        swatches_menu = QDockWidget(self)
        swatches_menu.setFeatures(QDockWidget.DockWidgetVerticalTitleBar)
        swatches_menu.setWidget(self.swatches)
        self.addDockWidget(Qt.TopDockWidgetArea, swatches_menu)

        self.setWindowTitle(
            '{} v{}'.format(APPLICATION_TITLE, APPLICATION_VERSION))

        self.showMaximized()

    def add_empty_canvas(self):
        self.add_canvas_for_filename(None)

    def add_canvas_for_filename(self, filename):
        CANVAS_PADDING = 60
        canvas = Canvas.scrollable(self, filename)

        subwindow = self.document_area.addSubWindow(canvas)
        subwindow.resize(
            canvas.widget().width() + CANVAS_PADDING,
            canvas.widget().height() + CANVAS_PADDING
        )
        subwindow.setWindowTitle(filename if filename else 'New image')
        subwindow.show()

        self.documents.append(OpenedImage(subwindow))
        self.current_document = len(self.documents) - 1

    def get_current_document(self):
        if self.documents:
            return self.documents[self.current_document]
        return None

    def open(self):
        filename = QFileDialog.getOpenFileName(
            self,
            'Open image',
            os.getcwd(),
            'PNG images (*.png)'
        )[0]

        if filename:
            existing = self.find_existing_document_for_filename(filename)
            if existing:
                self.document_area.setActiveSubWindow(existing.window)
            else:
                self.add_canvas_for_filename(filename)

    def find_existing_document_for_filename(self, filename):
        for document in self.documents:
            if document.filename() == filename:
                return document
        return None

    def save(self):
        self.statusbar.clearMessage()

        document = self.get_current_document()
        if document:
            saved_filename = document.canvas().save()
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    wiggle = Wiggle()
    sys.exit(app.exec_())
