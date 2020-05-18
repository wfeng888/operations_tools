from PyQt5.QtCore import *
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtPrintSupport import *

import os
import sys


class MyWebPage(QWebEnginePage):
    def certificateError(self,error):
        return True


class MyWebView(QWebEngineView):
    def __init__(self,tabwidget,parent=None):
        super(MyWebView, self).__init__(parent)
        self._tabwidget = tabwidget


    # 重写createwindow()
    def createWindow(self, QWebEnginePage_WebWindowType):
        return self._tabwidget.add_new_tab()

class MainWindow():
    def make_tabs(self):
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        # self.tabs.currentChanged.connect(self.current_tab_changed)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_current_tab)
        return self.tabs

    def add_new_tab(self, qurl=None, label="Blank"):
        browser = MyWebView(self)
        browser.setPage(MyWebPage())
        if qurl:
            browser.setUrl(qurl)
        i = self.tabs.addTab(browser, label)
        self.tabs.setCurrentIndex(i)
        return browser


    def current_tab_changed(self, i):
        qurl = self.tabs.currentWidget().url()
        self.update_urlbar(qurl, self.tabs.currentWidget())
        self.update_title(self.tabs.currentWidget())

    def close_current_tab(self, i):
        if self.tabs.count() < 2:
            return

        self.tabs.removeTab(i)

    def update_title(self, browser):
        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        title = self.tabs.currentWidget().page().title()
        self.setWindowTitle("%s - Mozarella Ashbadger" % title)

    def update_urlbar(self, q, browser=None):

        if browser != self.tabs.currentWidget():
            # If this signal is not from the current tab, ignore
            return

        if q.scheme() == 'https':
            # Secure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-ssl.png')))

        else:
            # Insecure padlock icon
            self.httpsicon.setPixmap(QPixmap(os.path.join('images', 'lock-nossl.png')))

        self.urlbar.setText(q.toString())
        self.urlbar.setCursorPosition(0)
