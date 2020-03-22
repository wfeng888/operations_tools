import sys
from PyQt5 import QtWidgets, uic

from deploy.mysql.DataSource import destroyDS
from ui.mainwindow  import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.initSize(0.8)

    def initSize(self, rate):
        desktop = QtWidgets.QApplication.desktop()
        self.screenWidth = desktop.width() * rate
        self.screenHeight = desktop.height() * rate
        self.resize(self.screenWidth, self.screenHeight)

def start(params):
    app = QtWidgets.QApplication(params)
    window = MainWindow()
    window.show()
    extstat = app.exec()
    destroyDS()
    sys.exit(extstat)

if __name__ == '__main__':
    start(sys.argv)