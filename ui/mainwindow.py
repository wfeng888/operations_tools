# -*- coding: utf-8 -*-
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QFileDialog, QCommandLinkButton, QLabel, QTextEdit, QSizePolicy, \
    QButtonGroup, QSplitter, QVBoxLayout, QSpacerItem, QStyle

from deploy.mysql.backup import  backup_restore
from deploy.mysql.mysql_exec import execute_createDB, isInstanceActive

from public_module import config

import log
from public_module.config import MysqlBackupConfig, MysqlConfig, MYSQL_CONFIG, updateMysqlConfig, initMysqlConfig, \
    CREATE_MYSQL_CONFIG
from public_module.utils import none_null_stringNone

from ui.myThread import MyThread


MYSQL_CREATE_DB,MYSQL_CHECK_ALIVE,MYSQL_BACKUP,MYSQL_RESTORE,MYSQL_CMD = range(5)
TASK_IDLE,TASK_BUSY = range(2)
TABPAGE,LOG,COMMAND,PROGRESS = range(4)
RADIO_MYSQL_BACKUP,RADIO_MYSQL_RESTORE,RADIO_MYSQL_BACKUP_LOGIC,RADIO_MYSQL_BACKUP_FULL,RADIO_MYSQL_BACKUP_INCREMENT = range(5)
BUTTON_SAVE_TO_LOCAL,BUTTON_SQLFILE_DIR = range(2)
CHECKBOX_MYSQL_BACKUPCOMPRESS,CHECKBOX_MYSQL_SAVE_LOCAL = range(2)
BACKUP_MODE_MAP = {
    RADIO_MYSQL_BACKUP_LOGIC:MysqlBackupConfig._CONS_BACKUP_MODE_LOGIC,
    RADIO_MYSQL_BACKUP_FULL:MysqlBackupConfig._CONS_BACKUP_MODE_FULL,
    RADIO_MYSQL_BACKUP_INCREMENT:MysqlBackupConfig._CONS_BACKUP_MODE_INCREMENT
}
BACKUP_OPER_MAP = {
    RADIO_MYSQL_BACKUP:MysqlBackupConfig._CONS_OPERATE_BACKUP,
    RADIO_MYSQL_RESTORE:MysqlBackupConfig._CONS_OPERATE_RESTORE
}

BUTTON_DEAL_MAP = {
    BUTTON_SAVE_TO_LOCAL:lambda obj,text:obj._mysqlBackupLocalPathEditLine.setText(text),
    BUTTON_SQLFILE_DIR:lambda text:setattr(CREATE_MYSQL_CONFIG,'sqlfiledir',text)
}



class Ui_MainWindow(object):
    def __init__(self):
        self.logCommandTabs = {}
        self._taskState={}
        self._translate = QtCore.QCoreApplication.translate

    def updateProgress(self,id,progress):
        log.debug('id:{},msg:{}'.format(str(id),str(progress)))
        if self.logCommandTabs[id].get(PROGRESS):
            self.logCommandTabs[id].get(PROGRESS).setProperty("value", progress)

    def writeLog(self,id,msg):
        self.logCommandTabs[id].get(LOG).append(msg)
        self.logCommandTabs[id].get(LOG).verticalScrollBar().minimum()

    def _initButtonEnable(self):
        self.setEnable = {
            MYSQL_CREATE_DB:self._checkMysqlCreateDBButton,
            MYSQL_CHECK_ALIVE:self._checkMysqlServiceAliveButton,
            MYSQL_BACKUP:self._checkMysqlBackupButton,
            MYSQL_RESTORE:self._checkMysqlRestoreButton,
            MYSQL_CMD:self._checkMysqlCommandButton
        }

    def _isTaskBusy(self,id):
        return True if self._taskState.get(id) and self._taskState.get(id) == TASK_BUSY else False

    def _checkMysqlCreateDBButton(self):
        if config.checkConfigForMysqlCreateDB() and not self._isTaskBusy(MYSQL_CREATE_DB):
            self.launchCRDBButton.setEnabled(True)
        else:
            self.launchCRDBButton.setEnabled(False)

    def _checkMysqlServiceAliveButton(self):
        if config.checkConfigForMysqlAlive() and not self._isTaskBusy(MYSQL_CHECK_ALIVE):
            self.checkMysqlAliveButton.setEnabled(True)
        else:
            self.checkMysqlAliveButton.setEnabled(False)

    def _checkMysqlBackupButton(self):
        pass

    def _checkMysqlRestoreButton(self):
        pass

    def _checkMysqlCommandButton(self):
        pass

    def _checkButtonEnable(self,id=None):
        if id != None:
            if not isinstance(id,(list,tuple)):
                id = (id,)
            keys = id
        else:
            keys = self.setEnable.keys()
        for key in keys:
            self.setEnable[key]()

    def _pubconfigButtonClick(self):
        pubMysqlConfig = MysqlConfig()
        pubMysqlConfig.port = self.portLineEdit.text().strip()
        pubMysqlConfig.host = self.hostLineEdit.text().strip()
        pubMysqlConfig.database = self.databaseLineEdit.text().strip()
        pubMysqlConfig.password = self.passwordLineEdit.text().strip()
        pubMysqlConfig.user = self.userLineEdit.text().strip()
        initMysqlConfig(pubMysqlConfig)
        log.debug(pubMysqlConfig)
        self._checkButtonEnable()

    def copyMyslqConfig(self,target):
        target.port = self.pubMysqlConfig.port
        target.host = self.pubMysqlConfig.host
        target.database = self.pubMysqlConfig.database
        target.password = self.pubMysqlConfig.password
        target.user = self.pubMysqlConfig.user

    def _setupMysqlPubPannel(self):
        self.pubConfigWidget = QtWidgets.QWidget()
        self.pubConfigWidget.setFixedHeight(220)
        self.pubConfigWidget.setContentsMargins(0,0,0,0)
        self.pubConfigGridLayout = QtWidgets.QGridLayout()
        self.pubConfigGridLayout.setContentsMargins(0,0,0,0)
        self.pubConfigLabel = QLabel()
        self.pubConfigLabel.setAlignment(Qt.AlignCenter)
        self.hostLabel = self._addLabel()
        self.hostLineEdit = QtWidgets.QLineEdit()
        self.portLabel = self._addLabel()
        self.portLineEdit = QtWidgets.QLineEdit()
        self.userLabel = self._addLabel()
        self.userLineEdit = QtWidgets.QLineEdit()
        self.databaseLabel = self._addLabel()
        self.databaseLineEdit = QtWidgets.QLineEdit()
        self.passwordLabel = self._addLabel()
        self.passwordLineEdit = self._addEditLine('password',QtWidgets.QLineEdit.Password)
        self.logdDirectoryLabel = self._addLabel("logDir:")
        self.findLogDirButton = self._createButton('Browers',None,fixwidth=80)
        self.logDirLineText = self._addEditLine()
        self.commitPubConfigButton = self._createButton('done',self._pubconfigButtonClick,True)
        self.pubConfigGridLayout.addWidget(self.pubConfigLabel,0,0,1,4)
        self.pubConfigGridLayout.addWidget(self.hostLabel,1,0)
        self.pubConfigGridLayout.addWidget(self.hostLineEdit,1,1,1,3)
        self.pubConfigGridLayout.addWidget(self.portLabel,2,0)
        self.pubConfigGridLayout.addWidget(self.portLineEdit,2,1,1,3)
        self.pubConfigGridLayout.addWidget(self.userLabel,3,0)
        self.pubConfigGridLayout.addWidget(self.userLineEdit,3,1,1,3)
        self.pubConfigGridLayout.addWidget(self.databaseLabel,4,0)
        self.pubConfigGridLayout.addWidget(self.databaseLineEdit,4,1,1,3)
        self.pubConfigGridLayout.addWidget(self.passwordLabel,5,0)
        self.pubConfigGridLayout.addWidget(self.passwordLineEdit,5,1,1,3)
        self.pubConfigGridLayout.addWidget(self.logdDirectoryLabel,6,0)
        self.pubConfigGridLayout.addWidget(self.logDirLineText,6,1,1,2)
        self.pubConfigGridLayout.addWidget(self.findLogDirButton,6,3)
        self.pubConfigGridLayout.addWidget(self.commitPubConfigButton,7,0,1,4)
        self.pubConfigWidget.setLayout(self.pubConfigGridLayout)
        self._initMysqlPubConfig()


    def _initMysqlPubConfig(self):
        self.userLineEdit.setText(MYSQL_CONFIG.user)
        self.portLineEdit.setText(str(MYSQL_CONFIG.port))
        self.hostLineEdit.setText(MYSQL_CONFIG.host)
        self.databaseLineEdit.setText(MYSQL_CONFIG.database)
        self.passwordLineEdit.setText(MYSQL_CONFIG.password)

    def _createRadioButton(self,title,member,buttongroup=None,id=None,checked=False):
        radioButton = QtWidgets.QRadioButton()
        radioButton.setObjectName(title)
        radioButton.setText(self._translate("MainWindow", title))
        radioButton.setChecked(checked)
        if member:
            radioButton.toggled.connect(member)
        if buttongroup:
            if id != None:
                buttongroup.addButton(radioButton,id)
            else:
                buttongroup.addButton(radioButton)
        return radioButton

    def _dealRadioToggled(self,id,checked):
        if id == RADIO_MYSQL_BACKUP_INCREMENT:
            self._mysqlBackupIncrementalBaseDirEditLine.setEnabled(checked)
        elif id == RADIO_MYSQL_BACKUP_FULL:
            pass
        elif id == RADIO_MYSQL_BACKUP_LOGIC:
            self._mysqlBackupCompressCheckBox.setEnabled(not checked)
        elif id == RADIO_MYSQL_RESTORE:
            self._mysqlRestoreTargetDirEditLine.setEnabled(checked)
        elif id == RADIO_MYSQL_BACKUP:
            pass

    def _dealCheckboxCheckState(self,id,state):
        if id == CHECKBOX_MYSQL_BACKUPCOMPRESS:
            pass
        if id == CHECKBOX_MYSQL_SAVE_LOCAL:
            self._mysqlBackupLocalPathButton.setEnabled(True if state > 0 else False)
            self._mysqlBackupLocalPathEditLine.setEnabled(True if state > 0 else False)


    def _createButton(self, text, member,enabled=True,fixwidth=None):
        button = QPushButton(text)
        button.setEnabled(enabled)
        if member:
            button.clicked.connect(member)
        if fixwidth:
            button.setFixedWidth(fixwidth)
        else:
            button.setMinimumWidth(80)
            button.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        return button

    def _createQCommandLinkButton(self,text,member,enabled=True):
        button = QCommandLinkButton(text)
        if member:
            button.clicked.connect(member)
        button.setEnabled(enabled)
        button.setFixedSize(120,40)
        return button

    def _addCheckBox(self,title,checked=False,member=None):
        checkBox = QtWidgets.QCheckBox(title)
        checkBox.setObjectName(title)
        checkBox.setEnabled(True)
        checkBox.setChecked(checked)
        if member:
            checkBox.stateChanged.connect(member)
        return checkBox

    def _addEditLine(self,title=None,echomode=None,text=None,editable=True,textChanged=None):
        lineEdit = QtWidgets.QLineEdit()
        lineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        lineEdit.setClearButtonEnabled(False)
        lineEdit.setEnabled(editable)
        lineEdit.setMinimumWidth(50)
        lineEdit.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        if title:
            lineEdit.setObjectName(title)
        if echomode:
            lineEdit.setEchoMode(echomode)
        if text:
            lineEdit.setText(text)
        if textChanged:
            lineEdit.textChanged.connect(textChanged)
        return lineEdit

    def _addLabel(self,title=None,maxwidth=100):
        label = QLabel()
        if title:
            label.setText(title)
        label.setMaximumWidth(maxwidth)
        label.setSizePolicy(QSizePolicy.Maximum,QSizePolicy.Preferred)
        return label

    def _createProgressBar(self,objname=None):
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMouseTracking(False)
        progressBar.setTabletTracking(False)
        progressBar.setMinimumWidth(200)
        progressBar.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Fixed)
        progressBar.setProperty("value", 0.0)
        if objname:
            progressBar.setObjectName(objname)
        return progressBar



    def _getFileDir(self,obj,id,fallback=None,args=()):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())
        obj.setText(directory)
        if id == MYSQL_CREATE_DB:
            config.CREATE_MYSQL_CONFIG.sqlfiledir = directory
        self._checkButtonEnable(id)
        if fallback:
            fallback(*args)

    def _taskStartCallback(self,id):
        self._taskState[id]=TASK_BUSY
        self._checkButtonEnable(id)

    def _taskFinishCallback(self,id,runningResult,taskResult):
        self._taskState[id]=TASK_IDLE
        self._checkButtonEnable(id)
        if id == MYSQL_CHECK_ALIVE:
            msg = 'THANK GOD!Mysql service is alive.' if taskResult == MyThread.SUCCESS else 'TOO BAD! Mysql service is down!'
            self.writeLog(id,msg)

    def _launchTask(self,func,id,tabtitle=None,pargs=()):
        try:
            if not self.logCommandTabs.get(id):
                self.logCommandTabs[id] = self._addTabPage(tabtitle,self.logCommandTabWidget)
            self.logCommandTabWidget.setCurrentWidget(self.logCommandTabs[id].get(TABPAGE))
            _taskThread = MyThread(func,id,args=pargs)
            _taskThread.progressUpdate.connect(self.updateProgress)
            _taskThread.msgUpdate.connect(self.writeLog)
            _taskThread.beginTask.connect(self._taskStartCallback)
            _taskThread.finishTask.connect(self._taskFinishCallback)
            _taskThread.start(MyThread.LowPriority)
        except BaseException as e:
            log.error(traceback.format_exc())

    def _launchCreateDB(self):
        log.debug('begin create database')
        _config = config.CREATE_MYSQL_CONFIG.copy()
        self._launchTask(execute_createDB,MYSQL_CREATE_DB,pargs=(_config,))

    def _mysqlCheckAndSetConfig(self):
        _config = MysqlBackupConfig()
        _config.backup_base_dir = self._mysqlbackupPathEditLine.text().strip()
        _config.operate = BACKUP_OPER_MAP[self._mysqlBackupOperButtonGroup.checkedId()]
        _config.backup_mode = BACKUP_MODE_MAP[self._mysqlBackupModeButtonGroup.checkedId()]

        if _config.backup_mode == MysqlBackupConfig._CONS_BACKUP_MODE_INCREMENT:
            _config.incremental_basedir = self._mysqlBackupIncrementalBaseDirEditLine.text().strip()
        _config.backup_software = MysqlBackupConfig._CONS_BACKUP_SOFTWARE_XTRABACKUP
        if _config.backup_mode == MysqlBackupConfig._CONS_BACKUP_MODE_LOGIC:
            if _config.operate == MysqlBackupConfig._CONS_OPERATE_RESTORE:
                _config.backup_software = MysqlBackupConfig._CONS_BACKUP_SOFTWARE_MYSQL
            else:
                _config.backup_software = MysqlBackupConfig._CONS_BACKUP_SOFTWARE_MYSQLDUMP
        if _config.operate == MysqlBackupConfig._CONS_OPERATE_RESTORE:
            _config.restore_target_dir = self._mysqlRestoreTargetDirEditLine.text().strip()
        _config.ssh_user = self._mysqlSSHUserEditline.text().strip()
        _config.ssh_port = self._mysqlSSHPortEditline.text().strip()
        _config.ssh_password = self._mysqlSSHPasswordEditline.text().strip()
        _config.mysql_software_path = self._mysqlSoftwarePathEditLine.text().strip()
        if self._mysqlBackupCompressCheckBox.isChecked():
            _config.compress = True
        if self._mysqlBackupToLocalCheckBox.isChecked() and none_null_stringNone(self._mysqlBackupLocalPathEditLine.text()):
            _config.is_save_to_local = True
            _config.local_path = self._mysqlBackupLocalPathEditLine.text().strip()
        log.debug('updateBackConfig')
        if not updateMysqlConfig(_config):
            log.error('updateBackConfig failed , stop {}'.format(BACKUP_OPER_MAP[self._mysqlBackupOperButtonGroup.checkedId()]))
            return
        if _config.operate == MysqlBackupConfig._CONS_OPERATE_BACKUP:
            self._launchBackupMysql(_config)
        else:
            self._launchRestoreMysql(_config)

    def _launchBackupMysql(self,config:MysqlBackupConfig):
        log.debug('Begin to backup mysql !')
        self._launchTask(backup_restore,MYSQL_BACKUP,'backMysql',pargs=(config,))

    def _launchRestoreMysql(self,config:MysqlBackupConfig):
        log.debug('Begin to restore mysql!')
        self._launchTask(backup_restore,MYSQL_RESTORE,'restoreMysql',pargs=(config,))

    def _launchCheckMysqlAlive(self):
        log.debug('Begin to check mysql !')
        _config = MYSQL_CONFIG.copy()
        self._launchTask(isInstanceActive,MYSQL_CHECK_ALIVE,'checkMysqlAlive',pargs=(_config,))

    def _setupBackupMysqlWidget(self):
        self.backupMysqlQWidget = QtWidgets.QWidget()
        self.backupMysqlQWidget.setObjectName("backupMysqlQWidget")
        self.backupMysqlGridLayout = QtWidgets.QGridLayout()

        self._mysqlBackupOperButtonGroup = QButtonGroup(self.backupMysqlQWidget)
        self._mysqlBackupRadio = self._createRadioButton('backup',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP,checked),self._mysqlBackupOperButtonGroup,RADIO_MYSQL_BACKUP,True)
        self._mysqlRestoreRadio = self._createRadioButton('restore',lambda checked:self._dealRadioToggled(RADIO_MYSQL_RESTORE,checked),self._mysqlBackupOperButtonGroup,RADIO_MYSQL_RESTORE)

        self._mysqlBackupModeButtonGroup = QButtonGroup(self.backupMysqlQWidget)
        self._myqslBackupLogicRadio = self._createRadioButton('logic',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_LOGIC,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_LOGIC)
        self._myqslBackupFullRadio = self._createRadioButton('full',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_FULL,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_FULL,True)
        self._myqslBackupIncrementRadio = self._createRadioButton('increment',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_INCREMENT,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_INCREMENT)

        self._mysqlBackupCompressCheckBox = self._addCheckBox('compress',True)
        self._mysqlBackupToLocalCheckBox = self._addCheckBox('save local',True,lambda state:self._dealCheckboxCheckState(CHECKBOX_MYSQL_SAVE_LOCAL,state))
        self._mysqlSSHUserLabel = self._addLabel("ssh user:")
        self._mysqlSSHPasswordLabel = self._addLabel("ssh password:")
        self._mysqlSSHPortLabel = self._addLabel("ssh port:")
        self._mysqlSSHUserEditline = self._addEditLine("mysqlsshuser")
        self._mysqlSSHUserEditline.setText('mysql')
        self._mysqlSSHPasswordEditline = self._addEditLine("mysqlsshpassword",QtWidgets.QLineEdit.Password)
        self._mysqlSSHPasswordEditline.setText('8845')
        self._mysqlSSHPortEditline = self._addEditLine("mysqlsshport")
        self._mysqlSSHPortEditline.setText('22')

        self._mysqlBackupPathLabel = self._addLabel("backup path")
        self._mysqlbackupPathEditLine = self._addEditLine('mysqlBackupPath')

        self._mysqlBackupPathButton = self._createButton('browse',None,enabled=False)

        self._mysqlBackupLocalPathLabel = self._addLabel("local save path")
        self._mysqlBackupLocalPathEditLine = self._addEditLine('mysqlBackupLocalPath')
        self._mysqlBackupLocalPathButton = self._createButton('browse',lambda :self._getFileDir(BUTTON_SAVE_TO_LOCAL,self._mysqlBackupLocalPathEditLine))

        self._mysqlBackupIncrementalBaseDirLabel = self._addLabel("incremental base path")
        self._mysqlBackupIncrementalBaseDirEditLine = self._addEditLine('mysqlBackupIncrementalBaseDir')
        self._mysqlBackupIncrementalBaseDirButton = self._createButton('browse',None,enabled=False)

        self._mysqlRestoreTargetDirLabel = self._addLabel("restore target path")
        self._mysqlRestoreTargetDirEditLine = self._addEditLine('mysqlRestoreTargetDirEditLine')
        self._mysqlRestoreTargetDirButton = self._createButton('browse',None,enabled=False)

        self._mysqlSoftwarePathLabel = self._addLabel("mysql software path")
        self._mysqlSoftwarePathEditLine = self._addEditLine('mysqlSoftwarePathEditLine')
        self._mysqlSoftwarePathButton = self._createButton('browse',None,enabled=False)

        self.launchBackupMysqlButton = self._createQCommandLinkButton('backup',self._mysqlCheckAndSetConfig,True)


        self.backupMysqlGridLayout.addWidget(self._myqslBackupLogicRadio,0,0,1,3)
        self.backupMysqlGridLayout.addWidget(self._myqslBackupFullRadio,0,1)
        self.backupMysqlGridLayout.addWidget(self._myqslBackupIncrementRadio,0,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHUserLabel,1,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHUserEditline,1,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPortLabel,2,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPortEditline,2,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPasswordLabel,3,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPasswordEditline,3,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupCompressCheckBox,4,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupToLocalCheckBox,4,1)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupPathLabel,5,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlbackupPathEditLine,5,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupPathButton,5,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathLabel,6,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathEditLine,6,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathButton,6,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirLabel,7,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirEditLine,7,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirButton,7,4)
        self.backupMysqlGridLayout.addWidget(self.launchBackupMysqlButton,8,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupRadio,9,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreRadio,9,1)
        self.backupMysqlQWidget.setLayout(self.backupMysqlGridLayout)

        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirLabel,10,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirEditLine,10,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirButton,10,4)

        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathLabel,11,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathEditLine,11,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathButton,11,4)

        self.occupyTestData()

    def occupyTestData(self):
        self._mysqlRestoreTargetDirEditLine.setText('/database/my3579')
        self._mysqlSoftwarePathEditLine.setText('/usr/local/mysql-5.7.23-el7-x86_64')
        self._mysqlbackupPathEditLine.setText('/data/backup/my3578/2020-03-18')
        self._mysqlBackupIncrementalBaseDirEditLine.setText('/data/backup/my3578/bak')


    def _setupRestoreMysqlWidget(self):
        self.restoreMysqlQWidget = QtWidgets.QWidget()
        self.restoreMysqlGridLayout = QtWidgets.QGridLayout()
        self.launchRestoreMysqlButton = self._createQCommandLinkButton('restore',self._mysqlCheckAndSetConfig,True)
        self.restoreMysqlGridLayout.addWidget(self.launchRestoreMysqlButton,1,1)
        self.restoreMysqlQWidget.setLayout(self.restoreMysqlGridLayout)

    def _addTabPage(self,title,tabWidget):
        logTextEdit = QTextEdit()
        logTextEdit.setReadOnly(True)
        font = QFont()
        font.setPointSize(20)
        logTextEdit.setFont(font)
        commandTextEdit = QTextEdit()
        commandTextEdit.setMinimumHeight(100)
        commandTextEdit.cursor()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        splitter.addWidget(logTextEdit)
        splitter.addWidget(commandTextEdit)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        splitter.setStretchFactor(0,80)
        boxlayout = QVBoxLayout()
        boxlayout.addWidget(splitter)
        boxlayout.setSpacing(0)
        boxlayout.setStretch(0,0)
        boxlayout.setStretch(0,0)
        tab = QtWidgets.QWidget()
        tab.setLayout(boxlayout)
        tab.layout().setContentsMargins(0,0,0,0)
        tabWidget.addTab(tab, "")
        tabWidget.setTabText(tabWidget.indexOf(tab), self._translate("MainWindow", title))
        tabWidget.setCurrentWidget(tabWidget)
        return  {TABPAGE:tab,LOG:logTextEdit,COMMAND:commandTextEdit}

    def _setupCreateDatabaseWidget(self):
        self.createDatabaseQWidget = QtWidgets.QWidget()
        self.createDBGridLayout = QtWidgets.QGridLayout()
        self.directoryLabel = self._addLabel("sqlDir:")
        self.sqlFileDirLineText = self._addEditLine(textChanged=lambda text: setattr(CREATE_MYSQL_CONFIG,'sqlfiledir',text))
        self.findSQLFileDirButton = self._createButton('Browers',lambda :self._getFileDir(self.sqlFileDirLineText,MYSQL_CREATE_DB),fixwidth=80)
        self.launchCRDBButton = self._createQCommandLinkButton('create',self._launchCreateDB,False)
        self.ignoreErrorCheckBox = self._addCheckBox('IgnoreError',True)
        self.logStatementCheckBox = self._addCheckBox('LogStatement',True)
        self.createMysqlDBDeployModeLabel = self._addLabel()
        self.createMysqlDBDeployModecomboBox = QtWidgets.QComboBox()
        self.createMysqlDBDeployModecomboBox.addItem("")
        self.createMysqlDBDeployModecomboBox.addItem("")
        self.createMysqlDBLogLevelLabel = self._addLabel()
        self.createMysqlDBLogLevelcomboBox = QtWidgets.QComboBox()
        self.createMysqlDBLogLevelcomboBox.addItem("DEBUG")
        self.createMysqlDBLogLevelcomboBox.addItem("VERBOSE")
        self.createMysqlDBLogLevelcomboBox.addItem("INFO")
        self.createMysqlDBLogLevelcomboBox.addItem("WARNING")
        self.createMysqlDBLogLevelcomboBox.addItem("ERROR")
        self.createMysqlDBProgressBar = self._createProgressBar('createMysqlDBProgressBar')
        self.logCommandTabs[MYSQL_CREATE_DB][PROGRESS] = self.createMysqlDBProgressBar
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        self.createDBGridLayout.addWidget(self.directoryLabel,0,0)
        self.createDBGridLayout.addWidget(self.sqlFileDirLineText,0,1,1,2)
        self.createDBGridLayout.addWidget(self.findSQLFileDirButton,0,3)
        self.createDBGridLayout.addWidget(self.ignoreErrorCheckBox,2,0,1,2)
        self.createDBGridLayout.addWidget(self.logStatementCheckBox,2,2,1,2)
        self.createDBGridLayout.addWidget(self.createMysqlDBDeployModeLabel,3,0)
        self.createDBGridLayout.addWidget(self.createMysqlDBDeployModecomboBox,3,1,1,2)
        self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelLabel,4,0)
        self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelcomboBox,4,1,1,2)
        self.createDBGridLayout.addWidget(self.createMysqlDBProgressBar,5,0,1,4)
        self.createDBGridLayout.addWidget(self.launchCRDBButton,6,2,1,2)
        self.createDBGridLayout.addItem(vspacer)
        self.createDBGridLayout.setVerticalSpacing(20)
        self.createDatabaseQWidget.setLayout(self.createDBGridLayout)
        return self.createDatabaseQWidget
    #
    #
    #
    # def _setupCreateDatabaseWidget(self):
    #     self.createDatabaseQWidget = QtWidgets.QWidget()
    #     self.createDatabaseQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
    #     self.createDatabaseQWidget.setObjectName("createDatabaseQWidget")
    #
    #     self.createDBGridLayout = QtWidgets.QGridLayout()
    #     self.directoryLabel = QLabel("sql directory:")
    #     self.findSQLFileDirButton = self._createButton('Browers',self._getSQLFileDir)
    #     self.sqlFileDirLineText = self._createTextEdit(True)
    #
    #     self.logdDirectoryLabel = QLabel("log directory:")
    #     self.findLogDirButton = self._createButton('Browers',self._getSQLFileDir)
    #     self.logDirLineText = self._createTextEdit(True)
    #
    #     self.launchCRDBButton = self._createQCommandLinkButton('create',self._launchCreateDB,False)
    #
    #     self.ignoreErrorCheckBox = self._addCheckBox('IgnoreError',True)
    #     self.logStatementCheckBox = self._addCheckBox('LogStatement',True)
    #
    #     self.createMysqlDBDeployModeLabel = QLabel()
    #     self.createMysqlDBDeployModecomboBox = QtWidgets.QComboBox()
    #     self.createMysqlDBDeployModecomboBox.setObjectName("createMysqlDBDeployModecomboBox")
    #     self.createMysqlDBDeployModecomboBox.addItem("")
    #     self.createMysqlDBDeployModecomboBox.addItem("")
    #
    #     self.createMysqlDBLogLevelLabel = QLabel()
    #     self.createMysqlDBLogLevelcomboBox = QtWidgets.QComboBox()
    #     self.createMysqlDBLogLevelcomboBox.setObjectName("createMysqlDBLogLevelcomboBox")
    #     self.createMysqlDBLogLevelcomboBox.addItem("DEBUG")
    #     self.createMysqlDBLogLevelcomboBox.addItem("VERBOSE")
    #     self.createMysqlDBLogLevelcomboBox.addItem("INFO")
    #     self.createMysqlDBLogLevelcomboBox.addItem("WARNING")
    #     self.createMysqlDBLogLevelcomboBox.addItem("ERROR")
    #
    #     self.createMysqlDBProgressBar = self._createProgressBar('createMysqlDBProgressBar')
    #
    #     self.createDBGridLayout.addWidget(self.directoryLabel,0,0)
    #     self.createDBGridLayout.addWidget(self.sqlFileDirLineText,0,1,1,3)
    #     self.createDBGridLayout.addWidget(self.findSQLFileDirButton,0,4)
    #     self.createDBGridLayout.addWidget(self.logdDirectoryLabel,1,0)
    #
    #     self.createDBGridLayout.addWidget(self.logDirLineText,1,1,1,3)
    #     self.createDBGridLayout.addWidget(self.findLogDirButton,1,4)
    #     self.createDBGridLayout.addWidget(self.ignoreErrorCheckBox,2,0,1,2)
    #     self.createDBGridLayout.addWidget(self.logStatementCheckBox,2,1,1,2)
    #     self.createDBGridLayout.addWidget(self.createMysqlDBDeployModeLabel,3,0)
    #     self.createDBGridLayout.addWidget(self.createMysqlDBDeployModecomboBox,3,1,1,3)
    #     self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelLabel,4,0)
    #     self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelcomboBox,4,1,1,2)
    #     self.createDBGridLayout.addWidget(self.createMysqlDBProgressBar,5,0,1,5)
    #     self.createDBGridLayout.addWidget(self.launchCRDBButton,6,3)
    #     self.createDatabaseQWidget.setLayout(self.createDBGridLayout)
    #
    #     self.logCommandTabs[MYSQL_CREATE_DB][PROGRESS] = self.createMysqlDBProgressBar
    #     return self.createDatabaseQWidge

    def _setupMysqlCheckAliveWidget(self):
        self.checkAliveQWidget = QtWidgets.QWidget()
        self.checkAliveQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
        self.checkAliveQWidget.setObjectName("checkAliveQWidget")

        self.checkMysqlDBAliveGridLayout = QtWidgets.QGridLayout()
        self.checkMysqlAliveButton = self._createQCommandLinkButton('do check',self._launchCheckMysqlAlive,False)
        self.checkMysqlAliveButton.setGeometry(QtCore.QRect(261, 0, 131, 41))
        self.checkMysqlDBAliveGridLayout.addWidget(self.checkMysqlAliveButton,0,2)
        self.checkAliveQWidget.setLayout(self.checkMysqlDBAliveGridLayout)

    def _setupMysqlActionBox(self):
        self.mysqlActionBox = QtWidgets.QToolBox()
        self._setupCreateDatabaseWidget()
        self._setupMysqlCheckAliveWidget()
        self._setupBackupMysqlWidget()
        self._setupRestoreMysqlWidget()
        self.mysqlActionBox.addItem(self.createDatabaseQWidget, "")
        self.mysqlActionBox.addItem(self.checkAliveQWidget, "")
        self.mysqlActionBox.addItem(self.backupMysqlQWidget, "")
        self.mysqlActionBox.addItem(self.restoreMysqlQWidget, "")
        self.mysqlActionBox.layout().setContentsMargins(0,0,0,0)
        self._initButtonEnable()


    def setupESActionBox(self):
        pass

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
        self.logCommandTabs[MYSQL_CREATE_DB] = self._addTabPage('createDB',self.logCommandTabWidget)
        # 主功能面板功能细分 mysql、es、oracle
        self.mysqlQWidget = QtWidgets.QWidget()
        self.esQWidget = QtWidgets.QWidget()
        self.oracleQWidget = QtWidgets.QWidget()
        self.mainPannelTabWidget.addTab(self.mysqlQWidget, "")
        self.mainPannelTabWidget.addTab(self.esQWidget, "")
        self.mainPannelTabWidget.addTab(self.oracleQWidget, "")
        self.mainPannelTabWidget.setCurrentIndex(0)
        # mysql公共配置面板
        self._setupMysqlPubPannel()
        # mysql动作面板tab
        self._setupMysqlActionBox()
        self.mysqlActionBox.setCurrentIndex(4)
        # mysql tabwidget 布局
        qvblayout = QVBoxLayout()
        qvblayout.addWidget(self.pubConfigWidget)
        qvblayout.addWidget(self.mysqlActionBox)
        qvblayout.setStretchFactor(self.mysqlActionBox,100)
        self.mysqlQWidget.setLayout(qvblayout)
        self.mysqlQWidget.layout().setContentsMargins(0,0,0,0)
        self._checkButtonEnable()
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

    def retranslateUi(self, MainWindow):

        MainWindow.setWindowTitle(self._translate("MainWindow", "MainWindow"))
        self.mainPannelTabWidget.setToolTip(self._translate("MainWindow", "<html><head/><body><p>mysql</p></body></html>"))
        self.mainPannelTabWidget.setWhatsThis(self._translate("MainWindow", "<html><head/><body><p>MySQL</p></body></html>"))
        self.launchCRDBButton.setText(self._translate("MainWindow", "create"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.createDatabaseQWidget), self._translate("MainWindow", "createdb"))
        self.checkMysqlAliveButton.setText(self._translate("MainWindow", "do check"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.checkAliveQWidget), self._translate("MainWindow", "checkAlive"))
        self.launchBackupMysqlButton.setText(self._translate("MainWindow", "do action"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.backupMysqlQWidget), self._translate("MainWindow", "backup"))
        self.launchRestoreMysqlButton.setText(self._translate("MainWindow", "do restore"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.restoreMysqlQWidget), self._translate("MainWindow", "restore"))
        # self.mysqlCommandButton.setText(self._translate("MainWindow", "enter"))
        # self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.mysqlCommandQWidget), self._translate("MainWindow", "command"))
        self.hostLabel.setText(self._translate("MainWindow", "host"))
        self.portLabel.setText(self._translate("MainWindow", "port"))
        self.userLabel.setText(self._translate("MainWindow", "user"))
        self.databaseLabel.setText(self._translate("MainWindow", "database"))
        self.passwordLabel.setText(self._translate("MainWindow", "password"))
        self.commitPubConfigButton.setText(self._translate("MainWindow", "done"))
        self.pubConfigLabel.setText(self._translate("MainWindow", "公共配置"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.mysqlQWidget), self._translate("MainWindow", "MySQL"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.esQWidget), self._translate("MainWindow", "ElasticSearch"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.oracleQWidget), self._translate("MainWindow", "Oracle"))
        self.menuFile.setTitle(self._translate("MainWindow", "File"))
        self.menuhelp.setTitle(self._translate("MainWindow", "help"))
        self.actionExit.setText(self._translate("MainWindow", "Exit"))
        self.actionabout_version.setText(self._translate("MainWindow", "about version"))
        self.actionmanual.setText(self._translate("MainWindow", "manual"))
        self.createMysqlDBDeployModecomboBox.setItemText(0, self._translate("MainWindow", "Simple deploy"))
        self.createMysqlDBDeployModecomboBox.setItemText(1, self._translate("MainWindow", "Parallel deploy"))
        self.createMysqlDBLogLevelcomboBox.setItemText(0, self._translate("MainWindow", "DEBUG"))
        self.createMysqlDBLogLevelcomboBox.setItemText(1, self._translate("MainWindow", "VERBOSE"))
        self.createMysqlDBLogLevelcomboBox.setItemText(2, self._translate("MainWindow", "INFO"))
        self.createMysqlDBLogLevelcomboBox.setItemText(3, self._translate("MainWindow", "WARNING"))
        self.createMysqlDBLogLevelcomboBox.setItemText(4, self._translate("MainWindow", "ERROR"))
        self.createMysqlDBDeployModeLabel.setText(self._translate("MainWindow", "deploy mode"))
        self.createMysqlDBLogLevelLabel.setText(self._translate("MainWindow", "log level"))


