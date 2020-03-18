import traceback

from PyQt5.QtCore import QThread, QMutexLocker, pyqtSignal, QMutex

import log
from deploy.mysql import BackupException
from public_module.global_vars import addNotifier,removeNotifier
from public_module.config import threadSafeConfig


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
    SUCCESS,FAIL = range(2)
    NOT_BEGIN,RUNNING,FINISHED = range(3)
    progressUpdate = pyqtSignal(int,float)
    msgUpdate = pyqtSignal(int,str)
    beginTask =  pyqtSignal(int)
    finishTask = pyqtSignal(int,int,int)
    def __init__(self,runfunc,id,notifier=None,args=()):
        super(MyThread, self).__init__()
        self._runFunc = runfunc
        self._id = id
        self._state = self.NOT_BEGIN
        self._notifier = notifier
        if not self._notifier:
            self._notifier = NotifyCombine(self,self,self._id)
        self._runningResult = -1
        self._taskresult = 1
        self._args = args
        log.ExceptionHook()
    def run(self):
        try:
            threadSafeConfig.add()
            self.beginTask.emit(self._id)
            # locker = QMutexLocker(QMutex())
            addNotifier(self._notifier)
            self._state = self.RUNNING
            self._taskresult = self.transformResult(self._runFunc(*self._args))
            self._state = self.FINISHED
            self._runningResult = self.SUCCESS
            removeNotifier()
        except BackupException as e:
            log.error(e)
            self._runningResult = self.FAIL
        except BaseException as e:
            log.error(traceback.format_exc())
            self._runningResult = self.FAIL
            raise e
        finally:
            self.finishTask.emit(self._id,self._runningResult,self._taskresult)
            threadSafeConfig.remove()

    def transformResult(self,result):
        if result == None:
            result = self.FAIL
        elif  isinstance(result,bool):
            result = self.SUCCESS if result else self.FAIL
        elif isinstance(result,str):
            if result.upper() == 'TRUE':
                result = self.SUCCESS
            else:
                result = self.FAIL
        if not isinstance(self,int):
            result = self.FAIL
        return result

    def isRunning(self):
        return self._state == self.RUNNING

    def isFinished(self):
        return self._state == self.finished()

    def write(self,msg):
        self.msgUpdate.emit(self._id,msg)

    def update(self,progress):
        self.progressUpdate.emit(self._id,progress)