# -*- coding: utf-8 -*-
import traceback

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QPushButton, QFileDialog, QCommandLinkButton, QLabel, QTextEdit, QSizePolicy, \
    QButtonGroup, QSplitter, QVBoxLayout, QSpacerItem, QStyle, QMessageBox

from deploy.mysql.backup import  backup_restore
from deploy.mysql.mysql_exec import execute_createDB, isInstanceActive

from public_module import config

import log
from public_module.config import MysqlBackupConfig, MysqlConfig, MYSQL_CONFIG, updateMysqlConfig, initMysqlConfig
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
    BUTTON_SQLFILE_DIR:lambda text:setattr(config.CREATE_MYSQL_CONFIG,'sqlfiledir',text)
}



class Ui_MainWindow(object):
    def __init__(self):
        self.logCommandTabs = {}
        self._taskState={}
        self._translate = QtCore.QCoreApplication.translate
        self._radio_state = {}

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
            MYSQL_RESTORE:self._checkMysqlBackupButton,
            MYSQL_CMD:self._checkMysqlBackupButton
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
        if  self._isTaskBusy(MYSQL_RESTORE) or self._isTaskBusy(MYSQL_BACKUP):
            self.launchBackupMysqlButton.setEnabled(False)
        else:
            self.launchBackupMysqlButton.setEnabled(True)



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
        pubConfigGridLayout = QtWidgets.QGridLayout()
        pubConfigGridLayout.setContentsMargins(0,0,0,0)
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
        self.passwordLineEdit = self._addEditLine('password',QtWidgets.QLineEdit.Password,enabled=True)
        # self.logdDirectoryLabel = self._addLabel("日志保存目录:")
        # self.findLogDirButton = self._createButton('浏览',None,fixwidth=80)
        # self.logDirLineText = self._addEditLine(enabled=True)
        self.commitPubConfigButton = self._createButton('done',self._pubconfigButtonClick,True)
        pubConfigGridLayout.addWidget(self.pubConfigLabel,0,0,2,4)
        pubConfigGridLayout.addWidget(self.hostLabel,2,0)
        pubConfigGridLayout.addWidget(self.hostLineEdit,2,1,1,3)
        pubConfigGridLayout.addWidget(self.portLabel,3,0)
        pubConfigGridLayout.addWidget(self.portLineEdit,3,1,1,3)
        pubConfigGridLayout.addWidget(self.userLabel,4,0)
        pubConfigGridLayout.addWidget(self.userLineEdit,4,1,1,3)
        pubConfigGridLayout.addWidget(self.databaseLabel,5,0)
        pubConfigGridLayout.addWidget(self.databaseLineEdit,5,1,1,3)
        pubConfigGridLayout.addWidget(self.passwordLabel,6,0)
        pubConfigGridLayout.addWidget(self.passwordLineEdit,6,1,1,3)
        # self.pubConfigGridLayout.addWidget(self.logdDirectoryLabel,6,0)
        # self.pubConfigGridLayout.addWidget(self.logDirLineText,6,1,1,2)
        # self.pubConfigGridLayout.addWidget(self.findLogDirButton,6,3)
        pubConfigGridLayout.addWidget(self.commitPubConfigButton,7,0,1,4)
        vspacer = QSpacerItem(10,10,QSizePolicy.Minimum,QSizePolicy.Expanding)
        pubConfigGridLayout.addItem(vspacer)
        pubConfigGridLayout.setVerticalSpacing(13)
        self.pubConfigWidget.setLayout(pubConfigGridLayout)
        self._initMysqlPubConfig()


    def _initMysqlPubConfig(self):
        self.userLineEdit.setText(MYSQL_CONFIG.user)
        self.portLineEdit.setText(str(MYSQL_CONFIG.port))
        self.hostLineEdit.setText(MYSQL_CONFIG.host)
        self.databaseLineEdit.setText(MYSQL_CONFIG.database)
        self.passwordLineEdit.setText(MYSQL_CONFIG.password)

    def _dealRadioToggled(self,id,checked):
        self._radio_state[id]=checked
        if id == RADIO_MYSQL_BACKUP_INCREMENT:
            self._mysqlBackupIncrementalBaseDirEditLine.setEnabled(checked)
        elif id == RADIO_MYSQL_BACKUP_FULL:
            pass
        elif id == RADIO_MYSQL_BACKUP_LOGIC:
            pass
        elif id == RADIO_MYSQL_RESTORE:
            self._mysqlRestoreTargetDirEditLine.setEnabled(checked)
            self._mysqlSoftwarePathEditLine.setEnabled(checked)
        elif id == RADIO_MYSQL_BACKUP:
            self._mysqlBackupToLocalCheckBox.setEnabled(checked)
            if not checked:
                self._mysqlBackupToLocalCheckBox.setChecked(checked)
        if not (self._radio_state.get(RADIO_MYSQL_BACKUP_LOGIC,False) or self._radio_state.get(RADIO_MYSQL_RESTORE,False)):
            self._mysqlBackupCompressCheckBox.setEnabled(True)
        else:
            self._mysqlBackupCompressCheckBox.setEnabled(False)


    def _dealCheckboxCheckState(self,id,state):
        if id == CHECKBOX_MYSQL_BACKUPCOMPRESS:
            pass
        if id == CHECKBOX_MYSQL_SAVE_LOCAL:
            self._mysqlBackupLocalPathButton.setEnabled(True if state > 0 else False)
            self._mysqlBackupLocalPathEditLine.setEnabled(True if state > 0 else False)

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

    def _createButton(self, text, member,enabled=True,fixwidth=None,visible=True):
        button = QPushButton(text)
        button.setEnabled(enabled)
        if member:
            button.clicked.connect(member)
        if fixwidth:
            button.setFixedWidth(fixwidth)
        else:
            button.setMinimumWidth(80)
            button.setSizePolicy(QSizePolicy.Minimum,QSizePolicy.Minimum)
        button.setVisible(visible)
        return button

    def _createQCommandLinkButton(self,text,member,enabled=True):
        button = QCommandLinkButton(text)
        if member:
            button.clicked.connect(member)
        button.setEnabled(enabled)
        button.setFixedSize(120,40)
        return button

    def _addCheckBox(self,title,checked=False,member=None,enabled=False):
        checkBox = QtWidgets.QCheckBox(title)
        checkBox.setObjectName(title)
        checkBox.setChecked(checked)
        if member:
            checkBox.stateChanged.connect(member)
        checkBox.setEnabled(enabled)
        return checkBox

    def _addEditLine(self,title=None,echomode=None,text=None,editable=True,textChanged=None,enabled=False):
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
        lineEdit.setEnabled(enabled)
        return lineEdit

    def _addLabel(self,title=None,maxwidth=100):
        label = QLabel()
        if title:
            label.setText(title)
        label.setMaximumWidth(maxwidth)
        label.setSizePolicy(QSizePolicy.Preferred,QSizePolicy.Preferred)
        label.setWordWrap(True)
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
        config.CREATE_MYSQL_CONFIG.log_statement = self.logStatementCheckBox.isChecked()
        config.CREATE_MYSQL_CONFIG.ignore_error = self.ignoreErrorCheckBox.isChecked()
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
        if self._mysqlBackupToLocalCheckBox.isChecked() and not none_null_stringNone(self._mysqlBackupLocalPathEditLine.text()):
            _config.is_save_to_local = True
            _config.local_path = self._mysqlBackupLocalPathEditLine.text().strip()
        log.debug('updateBackConfig')
        if not updateMysqlConfig(_config):
            log.error('updateBackConfig failed , stop {}'.format(BACKUP_OPER_MAP[self._mysqlBackupOperButtonGroup.checkedId()]))
            return
        _result,_msg = _config.checkConfig()
        if not _result:
            log.error(_msg)
            QMessageBox.warning(self,'输入配置错误',_msg,QMessageBox.Yes,QMessageBox.Yes)
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
        self._mysqlBackupRadio = self._createRadioButton('备份',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP,checked),self._mysqlBackupOperButtonGroup,RADIO_MYSQL_BACKUP)
        self._mysqlRestoreRadio = self._createRadioButton('恢复',lambda checked:self._dealRadioToggled(RADIO_MYSQL_RESTORE,checked),self._mysqlBackupOperButtonGroup,RADIO_MYSQL_RESTORE)
        self._mysqlBackupModeButtonGroup = QButtonGroup(self.backupMysqlQWidget)
        self._myqslBackupLogicRadio = self._createRadioButton('逻辑备份',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_LOGIC,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_LOGIC)
        self._myqslBackupFullRadio = self._createRadioButton('全量备份',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_FULL,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_FULL)
        self._myqslBackupIncrementRadio = self._createRadioButton('增量备份',lambda checked:self._dealRadioToggled(RADIO_MYSQL_BACKUP_INCREMENT,checked),self._mysqlBackupModeButtonGroup,RADIO_MYSQL_BACKUP_INCREMENT)
        self._mysqlBackupCompressCheckBox = self._addCheckBox('压缩',True)
        self._mysqlBackupToLocalCheckBox = self._addCheckBox('保存到本地',False,lambda state:self._dealCheckboxCheckState(CHECKBOX_MYSQL_SAVE_LOCAL,state))
        self._mysqlSSHUserLabel = self._addLabel("ssh用户:")
        self._mysqlSSHPasswordLabel = self._addLabel("ssh密码:")
        self._mysqlSSHPortLabel = self._addLabel("ssh端口:")
        self._mysqlSSHUserEditline = self._addEditLine("mysqlsshuser",enabled=True)
        self._mysqlSSHPasswordEditline = self._addEditLine("mysqlsshpassword",QtWidgets.QLineEdit.Password,enabled=True)
        self._mysqlSSHPortEditline = self._addEditLine("mysqlsshport",enabled=True)
        self._mysqlBackupPathLabel = self._addLabel("备份路径")
        self._mysqlbackupPathEditLine = self._addEditLine('mysqlBackupPath',enabled=True)
        self._mysqlBackupPathButton = self._createButton('浏览',None,enabled=False,visible=False)
        self._mysqlBackupLocalPathLabel = self._addLabel("本地保存路径")
        self._mysqlBackupLocalPathEditLine = self._addEditLine('mysqlBackupLocalPath')
        self._mysqlBackupLocalPathButton = self._createButton('browse',lambda :self._getFileDir(self._mysqlBackupLocalPathEditLine,BUTTON_SAVE_TO_LOCAL),enabled=False)
        self._mysqlBackupIncrementalBaseDirLabel = self._addLabel("增量备份基目录")
        self._mysqlBackupIncrementalBaseDirEditLine = self._addEditLine('mysqlBackupIncrementalBaseDir')
        self._mysqlBackupIncrementalBaseDirButton = self._createButton('browse',None,enabled=False,visible=False)
        self._mysqlRestoreTargetDirLabel = self._addLabel("恢复目标路径")
        self._mysqlRestoreTargetDirEditLine = self._addEditLine('mysqlRestoreTargetDirEditLine')
        self._mysqlRestoreTargetDirButton = self._createButton('浏览',None,enabled=False,visible=False)
        self._mysqlSoftwarePathLabel = self._addLabel("Mysql软件路径")
        self._mysqlSoftwarePathEditLine = self._addEditLine('mysqlSoftwarePathEditLine')
        self._mysqlSoftwarePathButton = self._createButton('browse',None,enabled=False,visible=False)
        self.launchBackupMysqlButton = self._createQCommandLinkButton('backup',self._mysqlCheckAndSetConfig,True)
        self._mysqlBackupRadio.setChecked(True)
        self._dealRadioToggled(RADIO_MYSQL_BACKUP,True)
        self._myqslBackupLogicRadio.setChecked(True)
        self._dealRadioToggled(RADIO_MYSQL_BACKUP_LOGIC,True)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupRadio,0,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreRadio,0,1)
        self.backupMysqlGridLayout.addWidget(self._myqslBackupLogicRadio,1,0,1,3)
        self.backupMysqlGridLayout.addWidget(self._myqslBackupFullRadio,1,1)
        self.backupMysqlGridLayout.addWidget(self._myqslBackupIncrementRadio,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHUserLabel,2,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHUserEditline,2,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPortLabel,3,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPortEditline,3,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPasswordLabel,4,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSSHPasswordEditline,4,1,1,2)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupCompressCheckBox,5,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupToLocalCheckBox,5,1)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupPathLabel,6,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlbackupPathEditLine,6,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupPathButton,6,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathLabel,7,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathEditLine,7,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupLocalPathButton,7,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirLabel,8,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirEditLine,8,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlBackupIncrementalBaseDirButton,8,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirLabel,9,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirEditLine,9,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlRestoreTargetDirButton,9,4)
        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathLabel,10,0)
        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathEditLine,10,1,1,3)
        self.backupMysqlGridLayout.addWidget(self._mysqlSoftwarePathButton,10,4)
        self.backupMysqlGridLayout.addWidget(self.launchBackupMysqlButton,11,0)
        self.backupMysqlQWidget.setLayout(self.backupMysqlGridLayout)
        self.occupyTestData()

    def occupyTestData(self):
        # self._mysqlRestoreTargetDirEditLine.setText('/database/my3579')
        # self._mysqlSoftwarePathEditLine.setText('/usr/local/mysql-5.7.23-el7-x86_64')
        # self._mysqlbackupPathEditLine.setText('/data/backup/my3578/2020-03-18')
        # self._mysqlBackupIncrementalBaseDirEditLine.setText('/data/backup/my3578/bak')
        # self._mysqlSSHUserEditline.setText('mysql')
        # self._mysqlSSHPasswordEditline.setText('8845')
        # self._mysqlSSHPortEditline.setText('22')
        pass


    def _setupRestoreMysqlWidget(self):
        self.restoreMysqlQWidget = QtWidgets.QWidget()
        self.restoreMysqlGridLayout = QtWidgets.QGridLayout()
        self.launchRestoreMysqlButton = self._createQCommandLinkButton('恢复',self._mysqlCheckAndSetConfig,True)
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
        self.directoryLabel = self._addLabel("sql脚本目录:")
        self.sqlFileDirLineText = self._addEditLine(textChanged=lambda text: setattr(config.CREATE_MYSQL_CONFIG,'sqlfiledir',text))
        self.findSQLFileDirButton = self._createButton('浏览',lambda :self._getFileDir(self.sqlFileDirLineText,MYSQL_CREATE_DB),fixwidth=80)
        self.launchCRDBButton = self._createQCommandLinkButton('创建',self._launchCreateDB,False)
        self.ignoreErrorCheckBox = self._addCheckBox('忽略错误',True,enabled=True)
        self.logStatementCheckBox = self._addCheckBox('记录语句到日志',True,enabled=True)
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

    def _setupMysqlCheckAliveWidget(self):
        self.checkAliveQWidget = QtWidgets.QWidget()
        self.checkAliveQWidget.setGeometry(QtCore.QRect(0, 0, 400, 421))
        self.checkAliveQWidget.setObjectName("checkAliveQWidget")

        self.checkMysqlDBAliveGridLayout = QtWidgets.QGridLayout()
        self.checkMysqlAliveButton = self._createQCommandLinkButton('测试连接',self._launchCheckMysqlAlive,False)
        self.checkMysqlAliveButton.setGeometry(QtCore.QRect(261, 0, 131, 41))
        self.checkMysqlDBAliveGridLayout.addWidget(self.checkMysqlAliveButton,0,2)
        self.checkAliveQWidget.setLayout(self.checkMysqlDBAliveGridLayout)

    def _setupMysqlActionBox(self):
        self.mysqlActionBox = QtWidgets.QToolBox()
        self._setupCreateDatabaseWidget()
        self._setupMysqlCheckAliveWidget()
        self._setupBackupMysqlWidget()
        # self._setupRestoreMysqlWidget()
        self.mysqlActionBox.addItem(self.createDatabaseQWidget, "")
        self.mysqlActionBox.addItem(self.checkAliveQWidget, "")
        self.mysqlActionBox.addItem(self.backupMysqlQWidget, "")
        # self.mysqlActionBox.addItem(self.restoreMysqlQWidget, "")
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

        MainWindow.setWindowTitle(self._translate("MainWindow", "Python运维工具"))
        self.mainPannelTabWidget.setToolTip(self._translate("MainWindow", "<html><head/><body><p>mysql</p></body></html>"))
        self.mainPannelTabWidget.setWhatsThis(self._translate("MainWindow", "<html><head/><body><p>MySQL</p></body></html>"))
        self.launchCRDBButton.setText(self._translate("MainWindow", "开始部署"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.createDatabaseQWidget), self._translate("MainWindow", "部署脚本"))
        self.checkMysqlAliveButton.setText(self._translate("MainWindow", "测试连接"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.checkAliveQWidget), self._translate("MainWindow", "Mysql服务检查"))
        self.launchBackupMysqlButton.setText(self._translate("MainWindow", "开始"))
        self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.backupMysqlQWidget), self._translate("MainWindow", "备份 / 恢复"))
        # self.launchRestoreMysqlButton.setText(self._translate("MainWindow", "do restore"))
        # self.mysqlActionBox.setItemText(self.mysqlActionBox.indexOf(self.restoreMysqlQWidget), self._translate("MainWindow", "恢复"))
        self.hostLabel.setText(self._translate("MainWindow", "主机"))
        self.portLabel.setText(self._translate("MainWindow", "端口"))
        self.userLabel.setText(self._translate("MainWindow", "用户"))
        self.databaseLabel.setText(self._translate("MainWindow", "数据库名称"))
        self.passwordLabel.setText(self._translate("MainWindow", "密码"))
        self.commitPubConfigButton.setText(self._translate("MainWindow", "保存"))
        self.pubConfigLabel.setText(self._translate("MainWindow", "公共配置"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.mysqlQWidget), self._translate("MainWindow", "MySQL"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.esQWidget), self._translate("MainWindow", "ElasticSearch"))
        self.mainPannelTabWidget.setTabText(self.mainPannelTabWidget.indexOf(self.oracleQWidget), self._translate("MainWindow", "Oracle"))
        self.menuFile.setTitle(self._translate("MainWindow", "文件"))
        self.menuhelp.setTitle(self._translate("MainWindow", "帮助"))
        self.actionExit.setText(self._translate("MainWindow", "退出"))
        self.actionabout_version.setText(self._translate("MainWindow", "关于"))
        self.actionmanual.setText(self._translate("MainWindow", "手册"))
        self.createMysqlDBDeployModecomboBox.setItemText(0, self._translate("MainWindow", "简单部署"))
        self.createMysqlDBDeployModecomboBox.setItemText(1, self._translate("MainWindow", "并行部署"))
        self.createMysqlDBLogLevelcomboBox.setItemText(0, self._translate("MainWindow", "DEBUG"))
        self.createMysqlDBLogLevelcomboBox.setItemText(1, self._translate("MainWindow", "VERBOSE"))
        self.createMysqlDBLogLevelcomboBox.setItemText(2, self._translate("MainWindow", "INFO"))
        self.createMysqlDBLogLevelcomboBox.setItemText(3, self._translate("MainWindow", "WARNING"))
        self.createMysqlDBLogLevelcomboBox.setItemText(4, self._translate("MainWindow", "ERROR"))
        self.createMysqlDBDeployModeLabel.setText(self._translate("MainWindow", "部署模式"))
        self.createMysqlDBLogLevelLabel.setText(self._translate("MainWindow", "日志级别"))


