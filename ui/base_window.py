import traceback

from PyQt5.QtCore import QDir, Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QFileDialog, QPushButton, QSizePolicy, QCommandLinkButton, QLabel, QTextEdit, QVBoxLayout, \
    QSpacerItem
from PyQt5 import QtCore, QtWidgets
import log
from ui.myThread import MyThread


TABPAGE,LOG,COMMAND,PROGRESS = range(4)
TASK_IDLE,TASK_BUSY = range(2)
class BaseWindow(object):
    def __init__(self,window,actionPannel,logPannel):
        self.logCommandTabs = {}
        self._taskState={}
        self._translate = QtCore.QCoreApplication.translate
        self._radio_state = {}
        self.setEnable = {}
        self._window = window
        self._action_pannel = actionPannel
        self._log_pannel = logPannel
        # self._window.update_ui.connect(self.updateUI)

    def updateUI(self,func,params):
        func(*params)

    def updateProgress(self,id,progress):
        log.debug('id:{},msg:{}'.format(str(id),str(progress)))
        if self.logCommandTabs[id].get(PROGRESS):
            self.logCommandTabs[id].get(PROGRESS).setProperty("value", progress)

    def writeLog(self,id,msg):
        self.logCommandTabs[id].get(LOG).append(msg)
        self.logCommandTabs[id].get(LOG).verticalScrollBar().minimum()

    def _isTaskBusy(self,id):
        return True if self._taskState.get(id) and self._taskState.get(id) == TASK_BUSY else False

    def _checkButtonEnable(self,id=None):
        if id != None:
            if not isinstance(id,(list,tuple)):
                id = (id,)
            keys = id
        else:
            keys = self.setEnable.keys()
        for key in keys:
            self.setEnable[key]()

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
        tabWidget.setCurrentWidget(tab)
        return  {TABPAGE:tab,LOG:logTextEdit,COMMAND:commandTextEdit}

    def _getFileDir(self,obj=None):
        directory = QFileDialog.getExistingDirectory(self._window, "Find Files", QDir.currentPath())
        if obj:
            obj.setText(directory)
        return directory

    def _taskStartCallback(self,id):
        self._taskState[id]=TASK_BUSY
        self._checkButtonEnable(id)

    def _taskFinishCallback(self,id,runningResult,taskResult):
        self._taskState[id]=TASK_IDLE
        self._checkButtonEnable(id)

    def _launchTask(self,func,id,tabtitle=None,pargs=()):
        try:
            if not self.logCommandTabs.get(id):
                self.logCommandTabs[id] = self._addTabPage(tabtitle,self._log_pannel)
            self._log_pannel.setCurrentWidget(self.logCommandTabs[id].get(TABPAGE))
            _taskThread = MyThread(func,id,args=pargs)
            _taskThread.progressUpdate.connect(self.updateProgress)
            _taskThread.msgUpdate.connect(self.writeLog)
            _taskThread.beginTask.connect(self._taskStartCallback)
            _taskThread.finishTask.connect(self._taskFinishCallback)
            _taskThread.start(MyThread.LowPriority)
        except BaseException as e:
            log.error(traceback.format_exc())

    def init_framework(self,pubconig_height):
        self.pubConfigWidget = QtWidgets.QWidget()
        self.pubConfigWidget.setFixedHeight(pubconig_height)
        self.pubConfigWidget.setContentsMargins(0,0,0,0)
        pubConfigGridLayout = QtWidgets.QGridLayout()
        pubConfigGridLayout.setContentsMargins(0,0,0,0)
        pubConfigGridLayout = QtWidgets.QGridLayout()
        pubConfigGridLayout.setContentsMargins(0,0,0,0)
        pubConfigGridLayout.setVerticalSpacing(13)
        self.pubConfigWidget.setLayout(pubConfigGridLayout)
        self.actionBox = QtWidgets.QToolBox()
        self.actionBox.layout().setContentsMargins(0,0,0,0)
        qvblayout = QVBoxLayout()
        qvblayout.addWidget(self.pubConfigWidget)
        qvblayout.addWidget(self.actionBox)
        qvblayout.setStretchFactor(self.actionBox,100)
        self._action_pannel.setLayout(qvblayout)
        self._action_pannel.layout().setContentsMargins(0,0,0,0)

    def addWidget(self,parent=None):
        qwidget = QtWidgets.QWidget()
        gridLayout = QtWidgets.QGridLayout()
        gridLayout.setVerticalSpacing(20)
        qwidget.setLayout(gridLayout)
        if parent:
            parent.addItem(qwidget,"")
        else:
            self.actionBox.addItem(qwidget,"")
        return qwidget