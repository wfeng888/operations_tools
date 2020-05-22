# -*- coding: utf-8 -*-
import threading
import time
from functools import partial

import tornado
import yaml
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtWidgets import QLabel, QSpacerItem, QSizePolicy, QButtonGroup

import deploy
import log
from deploy.es import es_execute, es_install, CONSTANTS_CONFIG
from deploy.es.es_config import ESConfig, ESDeployConfig, ESSnapshotRestoreConfig, ESInstallConfig
from deploy.es.es_execute import getClusterState, exec_warp
from public_module.utils import none_null_stringNone
from public_module.web import tornado_server, browser_tabbed
from ui.base_window import BaseWindow

CHECK_CLUSTER_STATE,ES_DEPLOY,ES_BACKUP,ES_RESTORE,ES_INSTALL = range(5)
RADIO_SNAPSHOT,RADIO_RESTORE,RADIO_REPOSITORY_FROM_EXISTS,RADIO_NEW_REPOSITORY = range(4)
class ESWindow(BaseWindow):
    def setupUi(self):
        self._radio_state = {}
        self.init_framework(200)
        self._setupPubPannel()
        self.initAction()
        self._setupActionBox()
        self.retranslateUi()
        self._initButtonEnable()
        self._repositorys = []
        self._snapshots = {}

    def _setupPubPannel(self):
        self.pubConfigLabel = QLabel()
        self.pubConfigLabel.setAlignment(Qt.AlignCenter)
        self.httpConnLabel = self._addLabel()
        self.httpConnLineEdit = QtWidgets.QLineEdit()
        self.transportConnLabel = self._addLabel()
        self.transportConnLineEdit = QtWidgets.QLineEdit()
        self.userLabel = self._addLabel()
        self.userLineEdit = QtWidgets.QLineEdit()
        self.passwordLabel = self._addLabel()
        self.passwordLineEdit = self._addEditLine('password',QtWidgets.QLineEdit.Password,enabled=True)
        pubConfigGridLayout = self.pubConfigWidget.layout()
        pubConfigGridLayout.addWidget(self.pubConfigLabel,0,0,2,4)
        pubConfigGridLayout.addWidget(self.httpConnLabel,2,0)
        pubConfigGridLayout.addWidget(self.httpConnLineEdit,2,1,1,3)
        pubConfigGridLayout.addWidget(self.transportConnLabel,3,0)
        pubConfigGridLayout.addWidget(self.transportConnLineEdit,3,1,1,3)
        pubConfigGridLayout.addWidget(self.userLabel,4,0)
        pubConfigGridLayout.addWidget(self.userLineEdit,4,1,1,3)
        pubConfigGridLayout.addWidget(self.passwordLabel,5,0)
        pubConfigGridLayout.addWidget(self.passwordLineEdit,5,1,1,3)
        vspacer = QSpacerItem(10,10,QSizePolicy.Minimum,QSizePolicy.Expanding)
        pubConfigGridLayout.addItem(vspacer)
        pubConfigGridLayout.setVerticalSpacing(13)
        self.pubConfigWidget.setLayout(pubConfigGridLayout)

    def _setupActionBox(self):
        self._setupTestConnect()
        self._setupDeployScript()
        self._setupSnapshot()
        self._setupRestore()
        self._setupInstall()

    def _setupTestConnect(self):
        self.clusterStateWidget = self.addWidget()
        self.checkClusterStateButton = self._createQCommandLinkButton('cluster_state',self.do_action[CHECK_CLUSTER_STATE],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.clusterStateWidget.layout()
        layout.addWidget(self.checkClusterStateButton,6,2,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.clusterStateWidget

    def _setupDeployScript(self):
        self.deployScriptWidget = self.addWidget()
        self.deployDirectoryLabel = self._addLabel("sql脚本目录:")
        self.deployDirLineText = self._addEditLine(editable=True)
        self.findSQLFileDirButton = self._createButton('浏览',lambda :self._getFileDir(self.deployDirLineText),fixwidth=80)
        self.ignoreErrorCheckBox = self._addCheckBox('忽略错误',True,enabled=True)
        self.logStatementCheckBox = self._addCheckBox('记录语句到日志',True,enabled=True)
        self.deployScriptButton = self._createQCommandLinkButton('deploy_script',self.do_action[ES_DEPLOY],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.deployScriptWidget.layout()
        layout.addWidget(self.deployDirectoryLabel,0,0)
        layout.addWidget(self.deployDirLineText,0,1,1,2)
        layout.addWidget(self.findSQLFileDirButton,0,3)
        layout.addWidget(self.ignoreErrorCheckBox,2,0,1,2)
        layout.addWidget(self.logStatementCheckBox,2,2,1,2)
        layout.addWidget(self.deployScriptButton,3,2,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.deployScriptWidget

    def resetComboBox(self,combo:QtWidgets.QComboBox,items):
        combo.clear()
        for item in items:
            combo.addItem(item)

    def resetRespository(self,combo:QtWidgets.QComboBox):
        config = ESConfig()
        config.http_connect = self.httpConnLineEdit.text().rstrip()
        if config.http_connect:
            self._repositorys = es_execute.get_repository(config)
        # self._window.update_ui.emit(self.resetComboBox,(combo,self._repositorys))
        self.resetComboBox(combo,self._repositorys)

    def resetSnapshots(self,combo:QtWidgets.QComboBox):
        config = ESConfig()
        config.http_connect = self.httpConnLineEdit.text().rstrip()
        if config.http_connect:
            self._snapshots = es_execute.list_snapshots(config)
        self.resetComboBox(combo,self._snapshots.keys())

    def resetSnapshot(self,combo:QtWidgets.QComboBox,text):
        items = self._snapshots.get(text,None)
        if items:
            items = items.keys()
        self.resetComboBox(combo,items)

    def _fillRestoreIndex(self,editText:QtWidgets.QLineEdit,combo:QtWidgets.QComboBox,snapshot):
        repository = combo.currentText()
        indices = self._snapshots[repository][snapshot]
        editText.setText(','.join(indices))

    def _setupSnapshot(self):
        self.snapshotWidget = self.addWidget()
        self.repositoryLabel = self._addLabel('目录/资源')
        self.repositoryLineText = self._addEditLine(enabled=True)
        self.snapshotRepositorycomboBox = QtWidgets.QComboBox()
        self.snapshotRepositorycomboBox.currentTextChanged.connect(lambda text:self.repositoryLineText.setText(text))
        self.getRespositoryButton = self._createButton('获取现有资源',lambda : self.resetRespository(self.snapshotRepositorycomboBox))
        self.indexLabel = self._addLabel("指定索引")
        self.indexLineText = self._addEditLine(editable=True,enabled=True)
        self.snapshotButton = self._createQCommandLinkButton('执行',self.do_action[ES_BACKUP],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.snapshotWidget.layout()
        layout.addWidget(self.snapshotRepositorycomboBox,0,0,1,2)
        layout.addWidget(self.getRespositoryButton,0,2,1,2)
        layout.addWidget(self.repositoryLabel,1,0)
        layout.addWidget(self.repositoryLineText,1,1,1,3)
        layout.addWidget(self.indexLabel,2,0)
        layout.addWidget(self.indexLineText,2,1,1,3)
        layout.addWidget(self.snapshotButton,3,0,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.snapshotWidget

    def _setupRestore(self):
        self.restoreWidget = self.addWidget()
        self.restoreIndexLabel = self._addLabel("指定索引")
        self.restoreIndexLineText = self._addEditLine(enabled=True)
        self.restoreSnapshotLabel = self._addLabel('备份ID')
        self.restoreSnapshotcomboBox = QtWidgets.QComboBox()
        self.restoreRepositoryLabel = self._addLabel('备份资源')
        self.restoreRepositorycomboBox = QtWidgets.QComboBox()
        self.restoreSnapshotcomboBox.currentTextChanged.connect(lambda text:self._fillRestoreIndex(self.restoreIndexLineText,self.restoreRepositorycomboBox,text))
        self.restoreRepositorycomboBox.currentTextChanged.connect(lambda text:self.resetSnapshot(self.restoreSnapshotcomboBox,text))
        self.getRestoreRespositoryButton = self._createButton('获取现有资源',lambda :self.resetSnapshots(self.restoreRepositorycomboBox))
        self.restoreRenameLabel = self._addLabel("rename_pattern")
        self.restoreRenameLineText = self._addEditLine(enabled=True)
        self.restoreRenameReplaceLabel = self._addLabel('rename_replacement')
        self.restoreRenameReplaceLineText = self._addEditLine(enabled=True)
        self.restoreIgnoreUnvlbleChckBx = self._addCheckBox('ignore_unavailable',True,enabled=True)
        self.restoreIncldGlblSttChckBx = self._addCheckBox('include_global_state',False,enabled=True)
        self.restorePrtlChckBx = self._addCheckBox('partial',True,enabled=True)
        self.restoreIndxSttingsLabel = self._addLabel('index_settings')
        self.restoreIndxSttingsLineText = self._addEditLine(enabled=True)
        self.restoreIncldAlssChckBx = self._addCheckBox('include_aliases',False,enabled=True)
        self.restoreIgnrIndxSttingsLabel = self._addLabel('ignore_index_settings')
        self.restoreIgnrIndxSttingsLineText = self._addEditLine(enabled=True)
        self.restoreButton = self._createQCommandLinkButton('执行',self.do_action[ES_RESTORE],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.restoreWidget.layout()
        layout.addWidget(self.restoreRepositoryLabel,0,0,1,1)
        layout.addWidget(self.restoreRepositorycomboBox,0,1,1,2)
        layout.addWidget(self.getRestoreRespositoryButton,0,3,1,1)
        layout.addWidget(self.restoreSnapshotLabel,1,0)
        layout.addWidget(self.restoreSnapshotcomboBox,1,1,1,3)
        layout.addWidget(self.restoreIndexLabel,2,0,)
        layout.addWidget(self.restoreIndexLineText,2,1,1,3)
        layout.addWidget(self.restoreRenameLabel,3,0)
        layout.addWidget(self.restoreRenameLineText,3,1,1,3)
        layout.addWidget(self.restoreRenameReplaceLabel,4,0)
        layout.addWidget(self.restoreRenameReplaceLineText,4,1,1,3)
        layout.addWidget(self.restoreIgnoreUnvlbleChckBx,5,0,1,2)
        layout.addWidget(self.restoreIncldGlblSttChckBx,5,2,1,2)
        layout.addWidget(self.restoreIncldAlssChckBx,6,0,1,2)
        layout.addWidget(self.restorePrtlChckBx,6,2,1,2)
        layout.addWidget(self.restoreIndxSttingsLabel,7,0)
        layout.addWidget(self.restoreIndxSttingsLineText,7,1,1,3)
        layout.addWidget(self.restoreIgnrIndxSttingsLabel,8,0)
        layout.addWidget(self.restoreIgnrIndxSttingsLineText,8,1,1,3)
        layout.addWidget(self.restoreButton,9,0,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.restoreWidget

    def _setupInstall(self):
        self.installWidget = self.addWidget()
        self.installButton = self._createQCommandLinkButton('执行',self.do_action[ES_INSTALL],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.installWidget.layout()
        layout.addWidget(self.installButton,0,0,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.installWidget

    def initAction(self):
        def _launchCheckClusterState():
            config = ESConfig()
            config.http_connect = self.httpConnLineEdit.text().rstrip()
            self._launchTask(getClusterState,CHECK_CLUSTER_STATE,'check es healthy',(config,))

        def _launchDeployScript():
            config = ESDeployConfig()
            config.http_connect = self.httpConnLineEdit.text().rstrip()
            config.file_path = self.deployDirLineText.text().rstrip()
            config.log_statement = self.logStatementCheckBox.isChecked()
            config.ignore_error = self.ignoreErrorCheckBox.isChecked()
            self._launchTask(exec_warp,ES_DEPLOY,'deploy script',(config,))

        def getTaskStatus(func,args=()):
            while(True):
                log.info('checking snapshot status')
                finish = func(*args)
                if finish:
                    break
                time.sleep(60)

        def _launchSnapshot(config:ESSnapshotRestoreConfig):
            if config.repository:
                # 这里判断一下给定的repository是否存在，如果不存在则退出
                res,stat = es_execute.get_repository(config)
                if -1 == stat or not res or not (config.repository in res):
                    log.error('repository %s does not exists!' % config.repository)
                    return False
            elif config.directory:
                res,stat = es_execute.exec_request(config,'GET',('_snapshot','_all'))
            #     这里要判断一下，给定的目录是不是已经注册过了资源，如果没有注册，这里要注册一下
                res,stats = es_execute.get_repository_location(config)
                if stats == 0:
                    find_flag = False
                    for i in res:
                        if 'fs' == i[1] and config.directory == i[3]:
                            config.repository = i[0]
                            find_flag = True
                if not find_flag:
                    res,stats = es_execute.register_snapshot(config,None,settings={'location':config.directory})
                    if 0 != stats:
                        log.error('failed to create repository, stop snapshot! ')
                        return False
                    config.repository = res['repository']
            log.debug('start snapshot ')
            res,stats = es_execute.exec_snapshot(config,config.repository,(config.index_name,),ignore_unavailable=False,include_global_state=False,metadata={})
            if stats == 0:
                config.snapshotid = res['snapshot']
                def getSnapShotStatus(config:ESSnapshotRestoreConfig,target_stats=()):
                    res,stats = es_execute.exec_request(config,'GET',('_snapshot',config.repository,config.snapshotid,'_status'))
                    # log.debug(res)
                    if stats == 0:
                        log.info('snapshot:%s, status:%s '%(res['snapshots'][0]['snapshot'],res['snapshots'][0]['state']))
                    if stats == -1 or res['snapshots'][0]['state'] in target_stats:
                        return True
                    else:
                        return False
                getTaskStatus(getSnapShotStatus,(config,(config._CONS_STATUS.SUCCESS.value,config._CONS_STATUS.FAILED.value, \
                                                                     config._CONS_STATUS.INCOMPATIBLE.value,config._CONS_STATUS.PARTIAL.value)))

        def _launchRestore(config:ESSnapshotRestoreConfig):
            res,stat = es_execute.exec_restore(config,config.repository,config.snapshotid)
            log.info(res)
            return stat

        def _launchSnapshotWrap():
            config =  ESSnapshotRestoreConfig()
            if not none_null_stringNone(self.indexLineText.text().rstrip()):
                config.index_name = self.indexLineText.text().rstrip()
            config.http_connect = self.httpConnLineEdit.text().rstrip()
            _content = self.repositoryLineText.text().rstrip()
            if none_null_stringNone(_content):
                log.error('repository is null.')
                return False
            if _content.startswith('/'):
                config.directory = _content
            else:
                config.repository = _content
            self._launchTask(_launchSnapshot,ES_BACKUP,'snapshot',(config,))

        def _launchRestoreWrap():
            config = ESSnapshotRestoreConfig()
            config.index_name = self.restoreIndexLineText.text().rstrip()
            config.http_connect = self.httpConnLineEdit.text().rstrip()
            config.repository = self.restoreRepositorycomboBox.currentText().rstrip()
            config.snapshotid = self.restoreSnapshotcomboBox.currentText().rstrip()
            config.partial = self.restorePrtlChckBx.isChecked()
            config.include_aliases = self.restoreIncldAlssChckBx.isChecked()
            config.ignore_index_settings = self.restoreIndxSttingsLineText.text().rstrip()
            config.ignore_unavailable = self.restoreIgnoreUnvlbleChckBx.isChecked()
            config.include_global_state = self.restoreIncldGlblSttChckBx.isChecked()
            config.rename_pattern = self.restoreRenameLineText.text().rstrip()
            config.rename_replacement = self.restoreRenameReplaceLineText.text().rstrip()
            config.index_settings = self.restoreIndxSttingsLineText.text().rstrip()
            self._launchTask(_launchRestore,ES_RESTORE,'restore',(config,))

        # def _launchInstall(configs):
        #     es_install.install(configs)

        def _launchInstallWrap():
            config = CONSTANTS_CONFIG
            threading.Thread(target=tornado_server.start).start()
            time.sleep(2)
            # tornado_server.start()
            tornado_server.setConfig(deploy.es.CONSTANTS_CONFIG)
            webtabs = browser_tabbed.MainWindow()
            _tab = webtabs.make_tabs()
            self._log_pannel.addTab(_tab, "")
            self._log_pannel.setTabText(self._log_pannel.indexOf(_tab), self._translate("MainWindow", 'CLUSTER INSTALL'))
            self._log_pannel.setCurrentWidget(_tab)
            webtabs.add_new_tab(QUrl('http://localhost:8888/g/config'), 'Cluster Config')

            # for file in ('201','202','210'):
            #     config = ESInstallConfig()
            #     config.es_base_path = '/bigdata/cluster_t'
            #     config.ssh_user = 'root'
            #     config.ssh_port = 22
            #     config.ssh_host = '10.45.156.%s'%file
            #     config.ssh_passwd = '8845'
            #     with open('C:/Users/ZNV/Desktop/test/es/%s_elasticsearch.yml'%file,'r',encoding='utf-8') as f:
            #         config.yml_config = yaml.load(f)
            #     config.es_tgz_path = '/home/elasticsearch/elasticsearch-5.4.3.tar.gz'
            #     config.jvm_heap = '1G'
            #     configs.append(config)
            # self._launchTask(_launchInstall,ES_INSTALL,'INSTALL',pargs=(configs,))


        self.do_action = {
            CHECK_CLUSTER_STATE: _launchCheckClusterState,
            ES_DEPLOY: _launchDeployScript,
            ES_BACKUP:_launchSnapshotWrap,
            ES_RESTORE:_launchRestoreWrap,
            ES_INSTALL:_launchInstallWrap
        }

    def retranslateUi(self):
        self.pubConfigLabel.setText(self._translate("MainWindow", "公共配置"))
        self.httpConnLabel.setText(self._translate("MainWindow", "http配置"))
        self.transportConnLabel.setText(self._translate("MainWindow", "transport配置"))
        self.userLabel.setText(self._translate("MainWindow", "用户"))
        self.passwordLabel.setText(self._translate("MainWindow", "密码"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.clusterStateWidget), self._translate("MainWindow", "集群服务检查"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.deployScriptWidget), self._translate("MainWindow", "脚本执行"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.snapshotWidget), self._translate("MainWindow", "备份"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.restoreWidget), self._translate("MainWindow", "恢复"))
        self.actionBox.setItemText(self.actionBox.indexOf(self.installWidget), self._translate("MainWindow", "集群安装"))



    def _dealRadioToggled(self,id,checked):
        self._radio_state[id]=checked
        if id == RADIO_RESTORE:
            pass
        elif id == RADIO_SNAPSHOT:
            pass

    def _initButtonEnable(self):
        self.setEnable = {
            CHECK_CLUSTER_STATE:lambda :self.checkClusterStateButton.setEnabled(False if  self._isTaskBusy(CHECK_CLUSTER_STATE) else True),
            ES_DEPLOY:self._checkESDeployButton,
            ES_BACKUP:self._checkESBackupButton,
            ES_RESTORE:self._checkESRestoreBackupButton,
            ES_INSTALL:self._checkESInstallButton
        }

    def _checkESDeployButton(self):
        pass

    def _checkESBackupButton(self):
        pass

    def _checkESRestoreBackupButton(self):
        pass

    def _checkESInstallButton(self):
        self.installButton.setEnabled(not self._isTaskBusy(ES_INSTALL))