import time

from PyQt5.QtCore import QThread

getCurrentThreadID = QThread.currentThread

def formatDate(format='%Y-%m-%d'):
    return time.strftime(format,time.localtime())

def formatDateTime():
    return formatDate('%Y%m%d%H%M%S')

