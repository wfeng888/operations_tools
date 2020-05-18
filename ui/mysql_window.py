# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel,  QSizePolicy, \
    QButtonGroup,  QVBoxLayout, QSpacerItem,  QMessageBox

from deploy.mysql.backup import  backup_restore
from deploy.mysql.mysql_exec import execute_createDB, isInstanceActive

from public_module import config

import log
from deploy.mysql.mysql_config import MysqlBackupConfig, MysqlConfig, MYSQL_CONFIG, updateMysqlConfig, initMysqlConfig, \
    checkConfigForMysqlCreateDB, checkConfigForMysqlAlive, CREATE_MYSQL_CONFIG
from public_module.utils import none_null_stringNone
from ui.base_window import BaseWindow, PROGRESS

from ui.myThread import MyThread


MYSQL_CREATE_DB,MYSQL_CHECK_ALIVE,MYSQL_BACKUP,MYSQL_RESTORE,MYSQL_CMD = range(5)

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




class MysqlWindow(BaseWindow):
    def _initButtonEnable(self):
        self.setEnable = {
            MYSQL_CREATE_DB:self._checkMysqlCreateDBButton,
            MYSQL_CHECK_ALIVE:self._checkMysqlServiceAliveButton,
            MYSQL_BACKUP:self._checkMysqlBackupButton,
            MYSQL_RESTORE:self._checkMysqlBackupButton,
            MYSQL_CMD:self._checkMysqlBackupButton
        }

    def _checkMysqlCreateDBButton(self):
        if checkConfigForMysqlCreateDB() and not self._isTaskBusy(MYSQL_CREATE_DB):
            self.launchCRDBButton.setEnabled(True)
        else:
            self.launchCRDBButton.setEnabled(False)

    def _checkMysqlServiceAliveButton(self):
        if checkConfigForMysqlAlive() and not self._isTaskBusy(MYSQL_CHECK_ALIVE):
            self.checkMysqlAliveButton.setEnabled(True)
        else:
            self.checkMysqlAliveButton.setEnabled(False)

    def _checkMysqlBackupButton(self):
        if  self._isTaskBusy(MYSQL_RESTORE) or self._isTaskBusy(MYSQL_BACKUP):
            self.launchBackupMysqlButton.setEnabled(False)
        else:
            self.launchBackupMysqlButton.setEnabled(True)

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
        # self.pubConfigWidget = QtWidgets.QWidget()
        # self.pubConfigWidget.setFixedHeight(220)
        # self.pubConfigWidget.setContentsMargins(0,0,0,0)
        # pubConfigGridLayout = QtWidgets.QGridLayout()
        # pubConfigGridLayout.setContentsMargins(0,0,0,0)
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
        pubConfigGridLayout = self.pubConfigWidget.layout()
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

    def _getFileDir(self,obj,id,fallback=None,args=()):
        directory = super()._getFileDir(obj)
        if id == MYSQL_CREATE_DB:
            CREATE_MYSQL_CONFIG.sqlfiledir = directory
        self._checkButtonEnable(id)
        if fallback:
            fallback(*args)

    def _taskFinishCallback(self,id,runningResult,taskResult):
        super(MysqlWindow, self)._taskFinishCallback(id,runningResult,taskResult)
        if id == MYSQL_CHECK_ALIVE:
            msg = 'THANK GOD!Mysql service is alive.' if taskResult == MyThread.SUCCESS else 'TOO BAD! Mysql service is down!'
            self.writeLog(id,msg)

    def _launchCreateDB(self):
        log.debug('begin create database')
        CREATE_MYSQL_CONFIG.log_statement = self.logStatementCheckBox.isChecked()
        CREATE_MYSQL_CONFIG.ignore_error = self.ignoreErrorCheckBox.isChecked()
        _config = CREATE_MYSQL_CONFIG.copy()
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


    def _setupCreateDatabaseWidget(self):
        self.createDatabaseQWidget = QtWidgets.QWidget()
        self.createDBGridLayout = QtWidgets.QGridLayout()
        self.directoryLabel = self._addLabel("sql脚本目录:")
        self.sqlFileDirLineText = self._addEditLine(textChanged=lambda text: setattr(CREATE_MYSQL_CONFIG,'sqlfiledir',text))
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
        # self.mysqlActionBox = QtWidgets.QToolBox()
        self._setupCreateDatabaseWidget()
        self._setupMysqlCheckAliveWidget()
        self._setupBackupMysqlWidget()
        # self._setupRestoreMysqlWidget()
        self.actionBox.addItem(self.createDatabaseQWidget, "")
        self.actionBox.addItem(self.checkAliveQWidget, "")
        self.actionBox.addItem(self.backupMysqlQWidget, "")
        # self.mysqlActionBox.addItem(self.restoreMysqlQWidget, "")
        # self.mysqlActionBox.layout().setContentsMargins(0,0,0,0)
        self._initButtonEnable()

    def setupUi(self):
        self.logCommandTabs[MYSQL_CREATE_DB] = self._addTabPage('createDB',self._log_pannel)
        self.init_framework(220)
        # mysql公共配置面板
        self._setupMysqlPubPannel()
        # mysql动作面板tab
        self._setupMysqlActionBox()
        self.actionBox.setCurrentIndex(4)
        # mysql tabwidget 布局
        # qvblayout = QVBoxLayout()
        # qvblayout.addWidget(self.pubConfigWidget)
        # qvblayout.addWidget(self.mysqlActionBox)
        # qvblayout.setStretchFactor(self.mysqlActionBox,100)
        # self._action_pannel.setLayout(qvblayout)
        # self._action_pannel.layout().setContentsMargins(0,0,0,0)
        self._checkButtonEnable()
        #文字显示
        self.retranslateUi()

    def retranslateUi(self):
        self.launchCRDBButton.setText(self._translate("MainWindow", "开始部署"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.createDatabaseQWidget), self._translate("MainWindow", "部署脚本"))
        self.checkMysqlAliveButton.setText(self._translate("MainWindow", "测试连接"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.checkAliveQWidget), self._translate("MainWindow", "Mysql服务检查"))
        self.launchBackupMysqlButton.setText(self._translate("MainWindow", "开始"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.backupMysqlQWidget), self._translate("MainWindow", "备份 / 恢复"))
        self.hostLabel.setText(self._translate("MainWindow", "主机"))
        self.portLabel.setText(self._translate("MainWindow", "端口"))
        self.userLabel.setText(self._translate("MainWindow", "用户"))
        self.databaseLabel.setText(self._translate("MainWindow", "数据库名称"))
        self.passwordLabel.setText(self._translate("MainWindow", "密码"))
        self.commitPubConfigButton.setText(self._translate("MainWindow", "保存"))
        self.pubConfigLabel.setText(self._translate("MainWindow", "公共配置"))
        self.createMysqlDBDeployModecomboBox.setItemText(0, self._translate("MainWindow", "简单部署"))
        self.createMysqlDBDeployModecomboBox.setItemText(1, self._translate("MainWindow", "并行部署"))
        self.createMysqlDBLogLevelcomboBox.setItemText(0, self._translate("MainWindow", "DEBUG"))
        self.createMysqlDBLogLevelcomboBox.setItemText(1, self._translate("MainWindow", "VERBOSE"))
        self.createMysqlDBLogLevelcomboBox.setItemText(2, self._translate("MainWindow", "INFO"))
        self.createMysqlDBLogLevelcomboBox.setItemText(3, self._translate("MainWindow", "WARNING"))
        self.createMysqlDBLogLevelcomboBox.setItemText(4, self._translate("MainWindow", "ERROR"))
        self.createMysqlDBDeployModeLabel.setText(self._translate("MainWindow", "部署模式"))
        self.createMysqlDBLogLevelLabel.setText(self._translate("MainWindow", "日志级别"))


