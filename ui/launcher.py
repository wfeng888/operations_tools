import sys
from PyQt5 import QtWidgets, uic

from ui.mainwindow  import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedSize(self.width(), self.height())

def start(params):
    app = QtWidgets.QApplication(params)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())