# -*- coding: utf-8 -*-
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSpacerItem, QSizePolicy

from ui.base_window import BaseWindow


class ESWindow(BaseWindow):
    def setupUi(self):
        self.init_framework(200)
        self._setupPubPannel()

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
        self.commitPubConfigButton = self._createButton('done',None,True)
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
        pubConfigGridLayout.addWidget(self.commitPubConfigButton,6,0,1,4)
        vspacer = QSpacerItem(10,10,QSizePolicy.Minimum,QSizePolicy.Expanding)
        pubConfigGridLayout.addItem(vspacer)
        pubConfigGridLayout.setVerticalSpacing(13)
        self.pubConfigWidget.setLayout(pubConfigGridLayout)

    def retranslateUi(self):
        self.pubConfigLabel.setText(self._translate("MainWindow", "开始部署"))