# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizePolicy,  QSplitter, QVBoxLayout

from ui.es_window import ESWindow
from ui.mysql_window import MysqlWindow
from ui.oracle_window import OracleWindow


class Ui_MainWindow(object):

    def _setupMenu(self,MainWindow):
        self.menubar = MainWindow.menuBar()
        self.menubar.setSizePolicy(QSizePolicy.Expanding,QSizePolicy.Fixed)
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuhelp = QtWidgets.QMenu(self.menubar)
        self.menuhelp.setObjectName("menuhelp")
        MainWindow.setMenuBar(self.menubar)
        self.actionExit = QtWidgets.QAction()
        self.actionExit.setObjectName("actionExit")
        self.actionabout_version = QtWidgets.QAction()
        self.actionabout_version.setObjectName("actionabout_version")
        self.actionmanual = QtWidgets.QAction()
        self.actionmanual.setObjectName("actionmanual")
        self.menuFile.addAction(self.actionExit)
        self.menuhelp.addAction(self.actionabout_version)
        self.menuhelp.addAction(self.actionmanual)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuhelp.menuAction())

    def setupUi(self, MainWindow):
        #主窗口
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        #菜单设置
        self._setupMenu(MainWindow)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        MainWindow.setCentralWidget(self.centralwidget)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)
        # 左侧功能面板
        self.mainPannelTabWidget = QtWidgets.QTabWidget()
        #右侧日志命令窗口
        self.logCommandTabWidget = QtWidgets.QTabWidget()
        self.logCommandTabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        # 主功能面板功能细分 mysql、es、oracle
        self.mysqlQWidget = QtWidgets.QWidget()
        self.esQWidget = QtWidgets.QWidget()
        self.oracleQWidget = QtWidgets.QWidget()
        self.mainPannelTabWidget.addTab(self.mysqlQWidget, "")
        self.mainPannelTabWidget.addTab(self.esQWidget, "")
        self.mainPannelTabWidget.addTab(self.oracleQWidget, "")
        self.mainPannelTabWidget.setCurrentIndex(0)
        # 主框架
        self.splitter = QSplitter(Qt.Horizontal)
        # 主框架组装
        self.splitter.addWidget(self.mainPannelTabWidget)
        self.splitter.addWidget(self.logCommandTabWidget)
        self.splitter.setHandleWidth(1)
        self.splitter.setStretchFactor(0,25)
        self.splitter.setStretchFactor(1,75)
        self.splitter.setChildrenCollapsible(False)
        self.boxlayout = QVBoxLayout()
        self.boxlayout.setContentsMargins(0,0,0,0)
        self.boxlayout.addWidget(self.splitter)
        self.centralwidget.setLayout(self.boxlayout)
        #文字显示
        self.retranslateUi(MainWindow)
        mysql = MysqlWindow(self,self.mysqlQWidget,self.logCommandTabWidget)
        mysql.setupUi()
        es = ESWindow(self,self.esQWidget,self.logCommandTabWidget)
        es.setupUi()
        oracle = OracleWindow(self,self.oracleQWidget,self.logCommandTabWidget)
        oracle.setupUi()

    def retranslateUi(self, MainWindow):
        self._translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(self._translate("MainWindow", "Python运维工具"))
        self.mainPannelTabWidget.setToolTip(self._translate("MainWindow", "<html><head/><body><p>mysql</p></body></html>"))
        self.mainPannelTabWidget.setWhatsThis(self._translate("MainWindow", "<html><head/><body><p>MySQL</p></body></html>"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.mysqlQWidget), self._translate("MainWindow", "MySQL"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.esQWidget), self._translate("MainWindow", "ElasticSearch"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.oracleQWidget), self._translate("MainWindow", "Oracle"))
        self.menuFile.setTitle(self._translate("MainWindow", "文件"))
        self.menuhelp.setTitle(self._translate("MainWindow", "帮助"))
        self.actionExit.setText(self._translate("MainWindow", "退出"))
        self.actionabout_version.setText(self._translate("MainWindow", "关于"))
        self.actionmanual.setText(self._translate("MainWindow", "手册"))


