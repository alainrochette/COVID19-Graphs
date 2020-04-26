import numpy as np
import sys
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.backends.qt_compat import QtCore, QtWidgets
import matplotlib.gridspec as gridspec
from matplotlib.figure import Figure


class Textbox_Demo(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        # self._main = QtWidgets.QWidget()
        # self.setCentralWidget(self._main)
        # layout = QtWidgets.QVBoxLayout(self._main)
        # layout.setContentsMargins(0,0,0,0)
        # layout.setSpacing(0)


        # self._textwidget = QtWidgets.QWidget()
        # textlayout = QtWidgets.QHBoxLayout(self._textwidget)
        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.setText("HELLO")
        self.textbox.editingFinished.connect(self.on_submit)
        # or, if wanting to have changed apply directly:
        # self.textbox.textEdited.connect(self.on_submit)
        # textlayout.addWidget(QtWidgets.QLabel("Enter Text: "))
        # textlayout.addWidget(self.textbox)
        # layout.addWidget(self._textwidget)
#


    def on_submit(self):
        text = self.textbox.text()
        print(text)
        pass


if __name__ == "__main__":
    qapp = QtWidgets.QApplication(sys.argv)
    app = Textbox_Demo()
    app.show()
    qapp.exec_()
