from PyQt5.QtCore import QThread, QMutexLocker, pyqtSignal, QMutex

import log
from public_module.global_vars import addNotifier,removeNotifier


class NotifyCombine(object):

    def __init__(self,logchannel,progresswriter,id):
        self._logchannel = logchannel
        self._progresswriter = progresswriter
        self._id = id


    def getLogChannel(self):
        return self._logchannel

    def notifyProgress(self,progressPercent):
        self._progresswriter.update(progressPercent)

    def getID(self):
        return self._id


class MyThread(QThread):
    NOT_BEGIN,RUNNING,FINISHED = range(3)
    progressUpdate = pyqtSignal(int,float)
    msgUpdate = pyqtSignal(int,str)
    buttonenable = pyqtSignal(int,bool)
    def __init__(self,runfunc,id):
        super(MyThread, self).__init__()
        self._runFunc = runfunc
        self._id = id
        self._state = self.NOT_BEGIN
        self._notifier = NotifyCombine(self,self,self._id)

    def run(self):
        try:
            locker = QMutexLocker(QMutex())
            self.buttonenable.emit(self._id,False)
            addNotifier(self._notifier)
            self._state = self.RUNNING
            self._runFunc()
            self._state = self.FINISHED
            removeNotifier(self._notifier)
        except BaseException as e:
            log.error(e)
            raise e
        finally:
            self.buttonenable.emit(self._id,True)

    def isRunning(self):
        return self._state == self.RUNNING

    def isFinished(self):
        return self._state == self.finished()

    def write(self,msg):
        self.msgUpdate.emit(self._id,msg)

    def update(self,progress):
        self.progressUpdate.emit(self._id,progress)