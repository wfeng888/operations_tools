# -*- coding: utf-8 -*-


from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QPushButton, QFileDialog, QLineEdit, QCommandLinkButton, QLabel
from deploy.mysql.mysql_exec import execute_createDB

import log
from public_module.config import CONFIG, init_mysqlconfig, checkConfigForMysqlCreateDB, setSQLFileDirectory


class Ui_MainWindow(object):



    def _setupMysqlPubPannel(self):
        self.formLayoutWidget = QtWidgets.QWidget(self.mysqlQWidget)
        self.formLayoutWidget.setGeometry(QtCore.QRect(0, 0, 401, 181))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.pubConfigFormLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.pubConfigFormLayout.setContentsMargins(0, 0, 0, 0)
        self.pubConfigFormLayout.setObjectName("pubConfigFormLayout")
        self.hostLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.hostLabel.setObjectName("hostLabel")
        self.pubConfigFormLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.hostLabel)
        self.hostLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.hostLineEdit.setObjectName("hostLineEdit")
        self.pubConfigFormLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.hostLineEdit)
        self.portLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.portLabel.setObjectName("portLabel")
        self.pubConfigFormLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.portLabel)
        self.portLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.portLineEdit.setObjectName("portLineEdit")
        self.pubConfigFormLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.portLineEdit)
        self.userLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.userLabel.setObjectName("userLabel")
        self.pubConfigFormLayout.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.userLabel)
        self.userLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.userLineEdit.setObjectName("userLineEdit")
        self.pubConfigFormLayout.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.userLineEdit)
        self.databaseLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.databaseLabel.setObjectName("databaseLabel")
        self.pubConfigFormLayout.setWidget(4, QtWidgets.QFormLayout.LabelRole, self.databaseLabel)
        self.databaseLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.databaseLineEdit.setObjectName("databaseLineEdit")
        self.pubConfigFormLayout.setWidget(4, QtWidgets.QFormLayout.FieldRole, self.databaseLineEdit)
        self.passwordLabel = QtWidgets.QLabel(self.formLayoutWidget)
        self.passwordLabel.setObjectName("passwordLabel")
        self.pubConfigFormLayout.setWidget(5, QtWidgets.QFormLayout.LabelRole, self.passwordLabel)
        self.passwordLineEdit = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.passwordLineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.passwordLineEdit.setClearButtonEnabled(False)
        self.passwordLineEdit.setObjectName("passwordLineEdit")
        self.passwordLineEdit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.pubConfigFormLayout.setWidget(5, QtWidgets.QFormLayout.FieldRole, self.passwordLineEdit)
        self.commitPubConfigButton = QtWidgets.QPushButton(self.formLayoutWidget)
        self.commitPubConfigButton.setObjectName("commitPubConfigButton")
        def _pubconfigButtonClick(checked:bool):
            param = {'host':self.hostLineEdit.text().strip(),'port':self.portLineEdit.text().strip(),'user':self.userLineEdit.text().strip()\
                     ,'password':self.passwordLineEdit.text().strip(),'database':self.databaseLineEdit.text().strip()}
            print(param)
            init_mysqlconfig(**param)
            if checkConfigForMysqlCreateDB():
                self.launchCRDBButton.setEnabled(True)

        self.commitPubConfigButton.clicked.connect(_pubconfigButtonClick)
        self.pubConfigFormLayout.setWidget(6, QtWidgets.QFormLayout.SpanningRole, self.commitPubConfigButton)
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        self.label.setEnabled(True)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.pubConfigFormLayout.setWidget(0, QtWidgets.QFormLayout.SpanningRole, self.label)
        self.hostLineEdit.raise_()
        self.portLabel.raise_()
        self.portLineEdit.raise_()
        self.userLabel.raise_()
        self.userLineEdit.raise_()
        self.databaseLabel.raise_()
        self.databaseLineEdit.raise_()
        self.passwordLabel.raise_()
        self.passwordLineEdit.raise_()
        self.hostLabel.raise_()
        self.label.raise_()
        self.commitPubConfigButton.raise_()

    def _createButton(self, text, member,enabled=True):
        button = QPushButton(text)
        button.clicked.connect(member)
        button.setEnabled(enabled)
        return button
    
    def _createQCommandLinkButton(self,text,member,enabled=True):
        button = QCommandLinkButton(text)
        button.clicked.connect(member)
        button.setEnabled(enabled)
        return button

    def _createTextEdit(self,editable:bool):
        dirLineEdit = QLineEdit()
        dirLineEdit.setEnabled(True)
        dirLineEdit.setUpdatesEnabled(editable)
        return dirLineEdit


    def _getSQLFileDir(self):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())
        self.sqlFileDirLineText.setText(directory)
        setSQLFileDirectory(directory)
        if checkConfigForMysqlCreateDB():
            self.launchCRDBButton.setEnabled(True)
        
    def _launchCreateDB(self):
        log.debug('begin create database')
        execute_createDB()

    def _setupMysqlActionBox(self):
        self.mysqlActionBox = QtWidgets.QToolBox(self.mysqlQWidget)
        self.mysqlActionBox.setGeometry(QtCore.QRect(0, 180, 400, 551))
        self.mysqlActionBox.setObjectName("detailConfigToolBox")
        self.createDatabaseQWidget = QtWidgets.QWidget()
        self.createDatabaseQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
        self.createDatabaseQWidget.setObjectName("createDatabaseQWidget")       
        
        self.createDBGridLayout = QtWidgets.QGridLayout()
        self.directoryLabel = QLabel("In directory:")
        self.findSQLFileDirButton = self._createButton('Browers',self._getSQLFileDir)
        self.sqlFileDirLineText = self._createTextEdit(True)
        self.launchCRDBButton = self._createQCommandLinkButton('create',self._launchCreateDB,False)
        
        self.createDBGridLayout.addWidget(self.directoryLabel,0,0)
        self.createDBGridLayout.addWidget(self.sqlFileDirLineText,0,1)
        self.createDBGridLayout.addWidget(self.findSQLFileDirButton,0,2)
        self.createDBGridLayout.addWidget(self.launchCRDBButton,1,2)
                
        self.createDatabaseQWidget.setLayout(self.createDBGridLayout)
        
        
        self.mysqlActionBox.addItem(self.createDatabaseQWidget, "")
        self.checkAliveQWidget = QtWidgets.QWidget()
        self.checkAliveQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
        self.checkAliveQWidget.setObjectName("checkAliveQWidget")
        self.commandLinkButton = QtWidgets.QCommandLinkButton(self.checkAliveQWidget)
        self.commandLinkButton.setGeometry(QtCore.QRect(261, 0, 131, 41))
        self.commandLinkButton.setObjectName("commandLinkButton")
        self.mysqlActionBox.addItem(self.checkAliveQWidget, "")
        self.backupQWidget = QtWidgets.QWidget()
        self.backupQWidget.setObjectName("backupQWidget")
        self.commandLinkButton_2 = QtWidgets.QCommandLinkButton(self.backupQWidget)
        self.commandLinkButton_2.setGeometry(QtCore.QRect(260, 0, 131, 41))
        self.commandLinkButton_2.setObjectName("commandLinkButton_2")
        self.mysqlActionBox.addItem(self.backupQWidget, "")
        self.restoreQWidget = QtWidgets.QWidget()
        self.restoreQWidget.setObjectName("restoreQWidget")
        self.commandLinkButton_3 = QtWidgets.QCommandLinkButton(self.restoreQWidget)
        self.commandLinkButton_3.setGeometry(QtCore.QRect(260, 0, 131, 41))
        self.commandLinkButton_3.setObjectName("commandLinkButton_3")
        self.mysqlActionBox.addItem(self.restoreQWidget, "")
        self.commandQWidget = QtWidgets.QWidget()
        self.commandQWidget.setObjectName("commandQWidget")
        self.commandLinkButton_4 = QtWidgets.QCommandLinkButton(self.commandQWidget)
        self.commandLinkButton_4.setGeometry(QtCore.QRect(260, 0, 131, 41))
        self.commandLinkButton_4.setObjectName("commandLinkButton_4")
        self.mysqlActionBox.addItem(self.commandQWidget, "")


    def setupESActionBox(self):
        pass

    def _setupMenu(self,MainWindow):
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 1400, 23))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuhelp = QtWidgets.QMenu(self.menubar)
        self.menuhelp.setObjectName("menuhelp")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(MainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionabout_version = QtWidgets.QAction(MainWindow)
        self.actionabout_version.setObjectName("actionabout_version")
        self.actionmanual = QtWidgets.QAction(MainWindow)
        self.actionmanual.setObjectName("actionmanual")
        self.menuFile.addAction(self.actionExit)
        self.menuhelp.addAction(self.actionabout_version)
        self.menuhelp.addAction(self.actionmanual)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuhelp.menuAction())

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.setEnabled(True)
        MainWindow.resize(1400, 800)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWindow.sizePolicy().hasHeightForWidth())
        MainWindow.setSizePolicy(sizePolicy)
        MainWindow.setDockOptions(QtWidgets.QMainWindow.AllowTabbedDocks|QtWidgets.QMainWindow.AnimatedDocks)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.mainPannelTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.mainPannelTabWidget.setGeometry(QtCore.QRect(0, 0, 400, 771))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(3)
        sizePolicy.setHeightForWidth(self.mainPannelTabWidget.sizePolicy().hasHeightForWidth())
        self.mainPannelTabWidget.setSizePolicy(sizePolicy)
        self.mainPannelTabWidget.setObjectName("mainPannelTabWidget")
        self.mysqlQWidget = QtWidgets.QWidget()
        self.mysqlQWidget.setObjectName("mysqlQWidget")


        self.mainPannelTabWidget.addTab(self.mysqlQWidget, "")
        self.esQWidget = QtWidgets.QWidget()
        self.esQWidget.setObjectName("esQWidget")
        self.mainPannelTabWidget.addTab(self.esQWidget, "")
        self.oracleQWidget = QtWidgets.QWidget()
        self.oracleQWidget.setObjectName("oracleQWidget")
        self.mainPannelTabWidget.addTab(self.oracleQWidget, "")
        self.logcommandMdiArea = QtWidgets.QMdiArea(self.centralwidget)
        self.logcommandMdiArea.setGeometry(QtCore.QRect(400, 0, 1000, 771))
        self.logcommandMdiArea.setObjectName("logcommandMdiArea")
        MainWindow.setCentralWidget(self.centralwidget)

        self._setupMysqlActionBox()
        self._setupMysqlPubPannel()
        self._setupMenu(MainWindow)

        self.retranslateUi(MainWindow)
        self.mainPannelTabWidget.setCurrentIndex(0)
        self.mysqlActionBox.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.mainPannelTabWidget.setToolTip(_translate("MainWindow", "<html><head/><body><p>mysql</p></body></html>"))
        self.mainPannelTabWidget.setWhatsThis(_translate("MainWindow", "<html><head/><body><p>MySQL</p></body></html>"))
        self.launchCRDBButton.setText(_translate("MainWindow", "go"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.createDatabaseQWidget), _translate("MainWindow", "createdb"))
        self.commandLinkButton.setText(_translate("MainWindow", "CommandLinkButton"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.checkAliveQWidget), _translate("MainWindow", "backup"))
        self.commandLinkButton_2.setText(_translate("MainWindow", "CommandLinkButton"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.backupQWidget), _translate("MainWindow", "restore"))
        self.commandLinkButton_3.setText(_translate("MainWindow", "CommandLinkButton"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.restoreQWidget), _translate("MainWindow", "checkAlive"))
        self.commandLinkButton_4.setText(_translate("MainWindow", "CommandLinkButton"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.commandQWidget), _translate("MainWindow", "command"))
        self.hostLabel.setText(_translate("MainWindow", "host"))
        self.portLabel.setText(_translate("MainWindow", "port"))
        self.userLabel.setText(_translate("MainWindow", "user"))
        self.databaseLabel.setText(_translate("MainWindow", "database"))
        self.passwordLabel.setText(_translate("MainWindow", "password"))
        self.commitPubConfigButton.setText(_translate("MainWindow", "done"))
        self.label.setText(_translate("MainWindow", "公共配置"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.mysqlQWidget), _translate("MainWindow", "MySQL"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.esQWidget), _translate("MainWindow", "ElasticSearch"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.oracleQWidget), _translate("MainWindow", "Oracle"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuhelp.setTitle(_translate("MainWindow", "help"))
        self.actionExit.setText(_translate("MainWindow", "Exit"))
        self.actionabout_version.setText(_translate("MainWindow", "about version"))
        self.actionmanual.setText(_translate("MainWindow", "manual"))
