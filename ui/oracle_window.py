from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSpacerItem, QSizePolicy
from PyQt5 import QtCore, QtWidgets

from deploy.mysql.mysql_config import MysqlConfig
from deploy.oracle import OracleConfig
from deploy.transform.oracle2mysql.oracle2mysql import start
from ui.base_window import BaseWindow

TRANSFORM_TO_MYSQL,=range(1)
class OracleWindow(BaseWindow):
    def setupUi(self):
        self._radio_state = {}
        self.init_framework(200)
        self._setupPubPannel()
        self.initAction()
        self._setupActionBox()
        self.retranslateUi()
        self._initButtonEnable()
        # self._repositorys = []
        # self._snapshots = {}
        self._occupyTestData()


    def _setupPubPannel(self):
        self.pubConfigLabel = QLabel()
        self.pubConfigLabel.setAlignment(Qt.AlignCenter)
        self.hostLabel = self._addLabel()
        self.hostLineEdit = QtWidgets.QLineEdit()
        self.portLabel = self._addLabel()
        self.portLineEdit = QtWidgets.QLineEdit()
        self.userLabel = self._addLabel()
        self.userLineEdit = QtWidgets.QLineEdit()
        self.passwordLabel = self._addLabel()
        self.passwordLineEdit = self._addEditLine('password',QtWidgets.QLineEdit.Password,enabled=True)
        self.serviceLabel = self._addLabel()
        self.serviceLineEdit = QtWidgets.QLineEdit()
        pubConfigGridLayout = self.pubConfigWidget.layout()
        pubConfigGridLayout.addWidget(self.pubConfigLabel,0,0,2,4)
        pubConfigGridLayout.addWidget(self.hostLabel,2,0)
        pubConfigGridLayout.addWidget(self.hostLineEdit,2,1,1,3)
        pubConfigGridLayout.addWidget(self.portLabel,3,0)
        pubConfigGridLayout.addWidget(self.portLineEdit,3,1,1,3)
        pubConfigGridLayout.addWidget(self.userLabel,4,0)
        pubConfigGridLayout.addWidget(self.userLineEdit,4,1,1,3)
        pubConfigGridLayout.addWidget(self.passwordLabel,5,0)
        pubConfigGridLayout.addWidget(self.passwordLineEdit,5,1,1,3)
        pubConfigGridLayout.addWidget(self.serviceLabel,6,0)
        pubConfigGridLayout.addWidget(self.serviceLineEdit,6,1,1,3)
        vspacer = QSpacerItem(10,10,QSizePolicy.Minimum,QSizePolicy.Expanding)
        pubConfigGridLayout.addItem(vspacer)
        pubConfigGridLayout.setVerticalSpacing(13)
        self.pubConfigWidget.setLayout(pubConfigGridLayout)

    def _initButtonEnable(self):
        self._buttons = {
            TRANSFORM_TO_MYSQL:self.transformButton
        }

        def _buttonEnable(id):
            if self._buttons.get(id,None):
                self._buttons[id].setEnabled(False if  self._isTaskBusy(TRANSFORM_TO_MYSQL) else True)

        self.setEnable = {
            TRANSFORM_TO_MYSQL:lambda :_buttonEnable(TRANSFORM_TO_MYSQL)
        }


    def initAction(self):

        def _transformToMySQL():
            _mysqlConfig = MysqlConfig()
            _mysqlConfig.host = self.toMySQLHostLineText.text().strip()
            _mysqlConfig.port = self.toMySQLPortLineText.text().strip()
            _mysqlConfig.user = self.toMySQLUserLineText.text().strip()
            _mysqlConfig.password = self.toMySQLPasswordLineText.text().strip()
            _mysqlConfig.database = self.toMySQLDataBaseLineText.text().strip()
            _oracleConfig = OracleConfig()
            _oracleConfig.host = self.hostLineEdit.text().strip()
            _oracleConfig.port = self.portLineEdit.text().strip()
            _oracleConfig.user = self.userLineEdit.text().strip()
            _oracleConfig.password = self.passwordLineEdit.text().strip()
            _oracleConfig.service = self.serviceLineEdit.text().strip()
            self._launchTask(start,TRANSFORM_TO_MYSQL,'transform to mysql',(_oracleConfig,_mysqlConfig))

        self.do_action = {
            TRANSFORM_TO_MYSQL: _transformToMySQL
        }

    def _setupActionBox(self):
        self._setupToMysql()


    def _occupyTestData(self):
        self.hostLineEdit.setText('10.72.3.16')
        self.portLineEdit.setText('1521')
        self.userLineEdit.setText('sa')
        self.passwordLineEdit.setText('zxm10')
        self.serviceLineEdit.setText('ORCL')
        self.toMySQLHostLineText.setText('10.72.3.98')
        self.toMySQLPortLineText.setText('3307')
        self.toMySQLUserLineText.setText('root')
        self.toMySQLPasswordLineText.setText('zxm10@@@')
        self.toMySQLDataBaseLineText.setText('usmsc')

    def _setupToMysql(self):
        self.toMySQLWidget = self.addWidget()
        self.toMySQLHostLabel = self._addLabel("Mysql ip")
        self.toMySQLHostLineText = self._addEditLine(enabled=True)
        self.toMySQLPortLabel = self._addLabel('MySQL 端口')
        self.toMySQLPortLineText = self._addEditLine(enabled=True)
        self.toMySQLUserLabel = self._addLabel('MySQL 用户')
        self.toMySQLUserLineText = self._addEditLine(enabled=True)
        self.toMySQLPasswordLabel = self._addLabel('MySQL 密码')
        self.toMySQLPasswordLineText = self._addEditLine('password',QtWidgets.QLineEdit.Password,enabled=True)
        self.toMySQLDataBaseLabel = self._addLabel('MySQL DataBase')
        self.toMySQLDataBaseLineText = self._addEditLine(enabled=True)
        self.transformButton = self._createQCommandLinkButton('开始',self.do_action[TRANSFORM_TO_MYSQL],True)
        vspacer = QSpacerItem(20,40,QSizePolicy.Minimum,QSizePolicy.Expanding)
        layout = self.toMySQLWidget.layout()
        layout.addWidget(self.toMySQLHostLabel,0,0)
        layout.addWidget(self.toMySQLHostLineText,0,1,1,3)
        layout.addWidget(self.toMySQLPortLabel,1,0)
        layout.addWidget(self.toMySQLPortLineText,1,1,1,3)
        layout.addWidget(self.toMySQLUserLabel,2,0)
        layout.addWidget(self.toMySQLUserLineText,2,1,1,3)
        layout.addWidget(self.toMySQLPasswordLabel,3,0)
        layout.addWidget(self.toMySQLPasswordLineText,3,1,1,3)
        layout.addWidget(self.toMySQLDataBaseLabel,4,0)
        layout.addWidget(self.toMySQLDataBaseLineText,4,1,1,3)
        layout.addWidget(self.transformButton,5,0,1,2)
        layout.addItem(vspacer)
        layout.setVerticalSpacing(20)
        return self.toMySQLWidget

    def retranslateUi(self):
        self.pubConfigLabel.setText(self._translate("MainWindow", "公共配置"))
        self.hostLabel.setText(self._translate("MainWindow", "ip"))
        self.portLabel.setText(self._translate("MainWindow", "端口"))
        self.userLabel.setText(self._translate("MainWindow", "用户"))
        self.passwordLabel.setText(self._translate("MainWindow", "密码"))
        self.serviceLabel.setText(self._translate("MainWindow", "服务名"))
        # self.actionBox.setItemText(self.actionBox.indexOf(self.clusterStateWidget), self._translate("MainWindow", "集群服务检查"))
        # self.actionBox.setItemText(self.actionBox.indexOf(self.deployScriptWidget), self._translate("MainWindow", "脚本执行"))
        # self.actionBox.setItemText(self.actionBox.indexOf(self.snapshotWidget), self._translate("MainWindow", "备份"))
        # self.actionBox.setItemText(self.actionBox.indexOf(self.restoreWidget), self._translate("MainWindow", "恢复"))
        # self.actionBox.setItemText(self.actionBox.indexOf(self.installWidget), self._translate("MainWindow", "集群安装"))
