# -*- coding: utf-8 -*-
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir
from PyQt5.QtWidgets import QPushButton, QFileDialog, QLineEdit, QCommandLinkButton, QLabel, QTextEdit, QSizePolicy, \
    QButtonGroup

from deploy.mysql.backup import backup, restore, backup_new
from deploy.mysql.mysql_exec import execute_createDB
from deploy.mysql import DBUtils
from public_module import config

import log
from public_module.config import init_mysqlconfig, checkConfigForMysqlCreateDB, setSQLFileDirectory, \
    checkGeneralConfigForMysql, BACKUP_CONFIG, BackupConfig, updateBackConfig

from ui.myThread import MyThread


MYSQL_CREATE_DB,MYSQL_CHECK_ALIVE,MYSQL_BACKUP,MYSQL_RESTORE,MYSQL_CMD = range(5)
TASK_IDLE,TASK_BUSY = range(2)
TABPAGE,LOG,COMMAND,PROGRESS = range(4)
RADIO_MYSQL_BACKUP,RADIO_MYSQL_RESTORE,RADIO_MYSQL_BACKUP_LOGIC,RADIO_MYSQL_BACKUP_FULL,RADIO_MYSQL_BACKUP_INCREMENT = range(5)
CHECKBOX_MYSQL_BACKUPCOMPRESS,CHECKBOX_MYSQL_SAVE_LOCAL = range(2)
BACKUP_MODE_MAP = {
    RADIO_MYSQL_BACKUP_LOGIC:BackupConfig._CONS_BACKUP_MODE_LOGIC,
    RADIO_MYSQL_BACKUP_FULL:BackupConfig._CONS_BACKUP_MODE_FULL,
    RADIO_MYSQL_BACKUP_INCREMENT:BackupConfig._CONS_BACKUP_MODE_INCREMENT
}
BACKUP_OPER_MAP = {
    RADIO_MYSQL_BACKUP:BackupConfig._CONS_OPERATE_BACKUP,
    RADIO_MYSQL_RESTORE:BackupConfig._CONS_OPERATE_RESTORE
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
        if checkGeneralConfigForMysql() and not self._isTaskBusy(MYSQL_CHECK_ALIVE):
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
        keys = self.setEnable.keys()
        if id:
            if not isinstance(id,(list,tuple)):
                id = (id,)
            keys = id
        for key in keys:
            self.setEnable[key]()

    def _pubconfigButtonClick(self):
        param = {'host':self.hostLineEdit.text().strip(),'port':self.portLineEdit.text().strip(),'user':self.userLineEdit.text().strip() \
            ,'password':self.passwordLineEdit.text().strip(),'database':self.databaseLineEdit.text().strip()}
        log.debug(param)
        init_mysqlconfig(**param)
        self._checkButtonEnable()

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

        self.commitPubConfigButton.clicked.connect(self._pubconfigButtonClick)
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
        self._initMysqlPubConfig()


    def _initMysqlPubConfig(self):
        self.userLineEdit.setText(config.getMysqlUser())
        self.portLineEdit.setText(config.getMysqlPort())
        self.hostLineEdit.setText(config.getMysqlHost())
        self.databaseLineEdit.setText(config.getMysqlDatabase())
        self.passwordLineEdit.setText(config.getMysqlPassword())
        self._checkButtonEnable()

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


    def _createButton(self, text, member,enabled=True):
        button = QPushButton(text)
        if member:
            button.clicked.connect(member)
        button.setEnabled(enabled)
        return button
    
    def _createQCommandLinkButton(self,text,member,enabled=True):
        button = QCommandLinkButton(text)
        button.clicked.connect(member)
        button.setEnabled(enabled)
        button.setFixedSize(120,40)
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
        self._checkButtonEnable(MYSQL_CREATE_DB)

    def _getFileDir(self,displayobj=None,callback=None):
        directory = QFileDialog.getExistingDirectory(self, "Find Files", QDir.currentPath())
        if displayobj:
            displayobj.setText(directory)
        if callback:
            callback(directory)

    # def _setButtonEnable(self,id,enabled):
    #     self.setEnable[id](enabled)

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
        self._launchTask(execute_createDB,MYSQL_CREATE_DB)

    def _launchBackupMysql(self):
        log.debug('Begin to backup mysql !')
        # self._launchTask(backup,MYSQL_BACKUP,'backMysql',pargs=(1,))
        self._launchTask(backup_new,MYSQL_BACKUP,'backMysql')

    def _mysqlCheckAndSetConfig(self):
        BACKUP_CONFIG.resetFields()
        BACKUP_CONFIG.backup_base_dir = self._mysqlbackupPathEditLine.text().strip()

        BACKUP_CONFIG.operate = BACKUP_OPER_MAP[self._mysqlBackupOperButtonGroup.checkedId()]
        BACKUP_CONFIG.backup_mode = BACKUP_MODE_MAP[self._mysqlBackupModeButtonGroup.checkedId()]

        if BACKUP_CONFIG.backup_mode == BackupConfig._CONS_BACKUP_MODE_INCREMENT:
            BACKUP_CONFIG.incremental_basedir = self._mysqlBackupIncrementalBaseDirEditLine.text().strip()
        BACKUP_CONFIG.backup_software = BackupConfig._CONS_BACKUP_SOFTWARE_XTRABACKUP
        if BACKUP_CONFIG.backup_mode == BackupConfig._CONS_BACKUP_MODE_LOGIC:
            if BACKUP_CONFIG.operate == BackupConfig._CONS_OPERATE_RESTORE:
                BACKUP_CONFIG.backup_software = BackupConfig._CONS_BACKUP_SOFTWARE_MYSQL
            else:
                BACKUP_CONFIG.backup_software = BackupConfig._CONS_BACKUP_SOFTWARE_MYSQLDUMP

        if BACKUP_CONFIG.operate == BackupConfig._CONS_OPERATE_RESTORE:
            BACKUP_CONFIG.restore_target_dir = self._mysqlRestoreTargetDirEditLine.text().strip()



        BACKUP_CONFIG.ssh_user = self._mysqlSSHUserEditline.text().strip()
        BACKUP_CONFIG.ssh_port = self._mysqlSSHPortEditline.text().strip()
        BACKUP_CONFIG.ssh_password = self._mysqlSSHPasswordEditline.text().strip()
        if self._mysqlBackupCompressCheckBox.isChecked():
            BACKUP_CONFIG.compress = True
        if self._mysqlBackupToLocalCheckBox.isChecked():
            BACKUP_CONFIG.is_save_to_local = True
            BACKUP_CONFIG.local_path = self._mysqlBackupLocalPathEditLine.text().strip()
        log.debug('updateBackConfig')
        if not updateBackConfig():
            log.error('updateBackConfig failed , stop {}'.format(BACKUP_OPER_MAP[self._mysqlBackupOperButtonGroup.checkedId()]))
            return
        self._launchBackupMysql()

    def _launchRestoreMysql(self):
        log.debug('Begin to restore mysql!')
        self._launchTask(restore,MYSQL_RESTORE,'restoreMysql',pargs=(1,))

    def _launchCheckMysqlAlive(self):
        log.debug('Begin to check mysql !')
        self._launchTask(DBUtils.isInstanceActive,MYSQL_CHECK_ALIVE,'checkMysqlAlive')


    def _addCheckBox(self,title,checked=False,member=None):
        checkBox = QtWidgets.QCheckBox(title)
        checkBox.setObjectName(title)
        checkBox.setEnabled(True)
        checkBox.setChecked(checked)
        if member:
            checkBox.stateChanged.connect(member)
        return checkBox

    def _addEditLine(self,title,echomode=None):
        lineEdit = QtWidgets.QLineEdit()
        lineEdit.setFocusPolicy(QtCore.Qt.StrongFocus)
        lineEdit.setClearButtonEnabled(False)
        lineEdit.setObjectName(title)
        if echomode:
            lineEdit.setEchoMode(echomode)
        return lineEdit

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
        self._mysqlSSHUserLabel = QLabel("ssh user:")
        self._mysqlSSHPasswordLabel = QLabel("ssh password:")
        self._mysqlSSHPortLabel = QLabel("ssh port:")
        self._mysqlSSHUserEditline = self._addEditLine("mysqlsshuser")
        self._mysqlSSHPasswordEditline = self._addEditLine("mysqlsshpassword",QtWidgets.QLineEdit.Password)
        self._mysqlSSHPortEditline = self._addEditLine("mysqlsshport")

        self._mysqlBackupPathLabel = QLabel("backup path")
        self._mysqlbackupPathEditLine = self._addEditLine('mysqlBackupPath')
        self._mysqlBackupPathButton = self._createButton('browse',None,enabled=False)

        self._mysqlBackupLocalPathLabel = QLabel("local save path")
        self._mysqlBackupLocalPathEditLine = self._addEditLine('mysqlBackupLocalPath')
        self._mysqlBackupLocalPathButton = self._createButton('browse',None)

        self._mysqlBackupIncrementalBaseDirLabel = QLabel("incremental base path")
        self._mysqlBackupIncrementalBaseDirEditLine = self._addEditLine('mysqlBackupIncrementalBaseDir')
        self._mysqlBackupIncrementalBaseDirButton = self._createButton('browse',None,enabled=False)

        self._mysqlRestoreTargetDirLabel = QLabel("restore target path")
        self._mysqlRestoreTargetDirEditLine = self._addEditLine('mysqlRestoreTargetDirEditLine')
        self._mysqlRestoreTargetDirButton = self._createButton('browse',None,enabled=False)


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

    def _setupRestoreMysqlWidget(self):
        self.restoreMysqlQWidget = QtWidgets.QWidget()
        self.restoreMysqlQWidget.setObjectName("restoreMysqlQWidget")
        self.restoreMysqlGridLayout = QtWidgets.QGridLayout()
        self.launchRestoreMysqlButton = self._createQCommandLinkButton('restore',self._launchRestoreMysql,True)
        self.restoreMysqlGridLayout.addWidget(self.launchRestoreMysqlButton,1,1)
        self.restoreMysqlQWidget.setLayout(self.restoreMysqlGridLayout)

    def _setupCreateDatabaseWidget(self):
        self.createDatabaseQWidget = QtWidgets.QWidget()
        self.createDatabaseQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
        self.createDatabaseQWidget.setObjectName("createDatabaseQWidget")

        self.createDBGridLayout = QtWidgets.QGridLayout()
        self.directoryLabel = QLabel("sql directory:")
        self.findSQLFileDirButton = self._createButton('Browers',self._getSQLFileDir)
        self.sqlFileDirLineText = self._createTextEdit(True)

        self.logdDirectoryLabel = QLabel("log directory:")
        self.findLogDirButton = self._createButton('Browers',self._getSQLFileDir)
        self.logDirLineText = self._createTextEdit(True)

        self.launchCRDBButton = self._createQCommandLinkButton('create',self._launchCreateDB,False)

        self.ignoreErrorCheckBox = self._addCheckBox('IgnoreError',True)
        self.logStatementCheckBox = self._addCheckBox('LogStatement',True)

        self.createMysqlDBDeployModeLabel = QLabel()
        self.createMysqlDBDeployModecomboBox = QtWidgets.QComboBox()
        self.createMysqlDBDeployModecomboBox.setObjectName("createMysqlDBDeployModecomboBox")
        self.createMysqlDBDeployModecomboBox.addItem("")
        self.createMysqlDBDeployModecomboBox.addItem("")

        self.createMysqlDBLogLevelLabel = QLabel()
        self.createMysqlDBLogLevelcomboBox = QtWidgets.QComboBox()
        self.createMysqlDBLogLevelcomboBox.setObjectName("createMysqlDBLogLevelcomboBox")
        self.createMysqlDBLogLevelcomboBox.addItem("DEBUG")
        self.createMysqlDBLogLevelcomboBox.addItem("VERBOSE")
        self.createMysqlDBLogLevelcomboBox.addItem("INFO")
        self.createMysqlDBLogLevelcomboBox.addItem("WARNING")
        self.createMysqlDBLogLevelcomboBox.addItem("ERROR")

        self.createMysqlDBProgressBar = self._createProgressBar('createMysqlDBProgressBar')

        self.createDBGridLayout.addWidget(self.directoryLabel,0,0)
        self.createDBGridLayout.addWidget(self.sqlFileDirLineText,0,1,1,3)
        self.createDBGridLayout.addWidget(self.findSQLFileDirButton,0,4)
        self.createDBGridLayout.addWidget(self.logdDirectoryLabel,1,0)

        self.createDBGridLayout.addWidget(self.logDirLineText,1,1,1,3)
        self.createDBGridLayout.addWidget(self.findLogDirButton,1,4)
        self.createDBGridLayout.addWidget(self.ignoreErrorCheckBox,2,0,1,2)
        self.createDBGridLayout.addWidget(self.logStatementCheckBox,2,1,1,2)
        self.createDBGridLayout.addWidget(self.createMysqlDBDeployModeLabel,3,0)
        self.createDBGridLayout.addWidget(self.createMysqlDBDeployModecomboBox,3,1,1,3)
        self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelLabel,4,0)
        self.createDBGridLayout.addWidget(self.createMysqlDBLogLevelcomboBox,4,1,1,2)
        self.createDBGridLayout.addWidget(self.createMysqlDBProgressBar,5,0,1,5)
        self.createDBGridLayout.addWidget(self.launchCRDBButton,6,3)
        self.createDatabaseQWidget.setLayout(self.createDBGridLayout)

        self.logCommandTabs[MYSQL_CREATE_DB][PROGRESS] = self.createMysqlDBProgressBar
        return self.createDatabaseQWidget

    def _createProgressBar(self,objname=None):
        progressBar = QtWidgets.QProgressBar()
        progressBar.setMouseTracking(False)
        progressBar.setTabletTracking(False)
        progressBar.setProperty("value", 0.0)
        if objname:
            progressBar.setObjectName(objname)
        return progressBar

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

        self.mysqlActionBox = QtWidgets.QToolBox(self.mysqlQWidget)
        self.mysqlActionBox.setGeometry(QtCore.QRect(0, 180, 400, 551))
        self.mysqlActionBox.setObjectName("detailConfigToolBox")

        self._setupCreateDatabaseWidget()
        self._setupMysqlCheckAliveWidget()
        self._setupBackupMysqlWidget()
        self._setupRestoreMysqlWidget()
        self.mysqlActionBox.addItem(self.createDatabaseQWidget, "")
        self.mysqlActionBox.addItem(self.checkAliveQWidget, "")
        self.mysqlActionBox.addItem(self.backupMysqlQWidget, "")
        self.mysqlActionBox.addItem(self.restoreMysqlQWidget, "")
        self.mysqlCommandQWidget = QtWidgets.QWidget()
        self.mysqlCommandQWidget.setObjectName("mysqlCommandQWidget")
        self.mysqlCommandButton = QtWidgets.QCommandLinkButton(self.mysqlCommandQWidget)
        self.mysqlCommandButton.setGeometry(QtCore.QRect(260, 0, 131, 41))
        self.mysqlCommandButton.setObjectName("mysqlCommandButton")
        self.mysqlActionBox.addItem(self.mysqlCommandQWidget, "")

        self._initButtonEnable()


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

        self.logCommandTabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.logCommandTabWidget.setGeometry(QtCore.QRect(400, 0, 1001, 751))
        self.logCommandTabWidget.setTabPosition(QtWidgets.QTabWidget.South)
        self.logCommandTabWidget.setObjectName("logCommandTabWidget")
        self.logCommandTabs[MYSQL_CREATE_DB] = self._addTabPage('createDB',self.logCommandTabWidget)

        MainWindow.setCentralWidget(self.centralwidget)

        self._setupMysqlActionBox()
        self._setupMysqlPubPannel()
        self._setupMenu(MainWindow)

        self.retranslateUi(MainWindow)
        self.mainPannelTabWidget.setCurrentIndex(0)
        self.mysqlActionBox.setCurrentIndex(4)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def _addTabPage(self,title,tabWidget):
        tab = QtWidgets.QWidget()
        tab.setObjectName("tab")
        logTextEdit = QTextEdit()
        logTextEdit.setReadOnly(True)
        commandTextEdit = QTextEdit()
        commandTextEdit.setMinimumHeight(100)
        commandTextEdit.cursor()
        splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical,tab)
        splitter.setGeometry(QtCore.QRect(0, 0, 1000, 750))
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(logTextEdit)
        splitter.addWidget(commandTextEdit)
        tabWidget.addTab(tab, "")
        tabWidget.setTabText(tabWidget.indexOf(tab), self._translate("MainWindow", title))
        tabWidget.setCurrentWidget(tabWidget)

        return  {TABPAGE:tab,LOG:logTextEdit,COMMAND:commandTextEdit}

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
        self.mysqlCommandButton.setText(self._translate("MainWindow", "enter"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.mysqlCommandQWidget), self._translate("MainWindow", "command"))
        self.hostLabel.setText(self._translate("MainWindow", "host"))
        self.portLabel.setText(self._translate("MainWindow", "port"))
        self.userLabel.setText(self._translate("MainWindow", "user"))
        self.databaseLabel.setText(self._translate("MainWindow", "database"))
        self.passwordLabel.setText(self._translate("MainWindow", "password"))
        self.commitPubConfigButton.setText(self._translate("MainWindow", "done"))
        self.label.setText(self._translate("MainWindow", "公共配置"))
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


