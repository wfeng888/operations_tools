import sys
import time
import traceback
from abc import ABCMeta,abstractmethod
from enum import Enum
from public_module.global_vars import getNotifier


class LogLevel(Enum):
    DEBUG = 0
    VERBOSE = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

currentLevel = LogLevel.DEBUG

class LogChannel(object,metaclass=ABCMeta):


    @abstractmethod
    def write(self,msg):
        pass


class DefaultLogChannel(LogChannel):

    def write(self,msg):
        print(msg)

class TargetLogChannel(LogChannel):

    def __init__(self,target):
        self._target = target

    def write(self,msg):
        if self._target:
            self._target.write(msg)

class CombineLogChannel(TargetLogChannel):


    def __init__(self,target):
        self._logChannels = set()
        self._logChannels.add(target)

    def addChannel(self,target):
        self._logChannels.add(target)

    def removeChannel(self,target):
        self._logChannels.remove(target)

    def write(self,msg):
        for channel in self._logChannels:
            channel.write(msg)


_defaultLogChannel = DefaultLogChannel()

def debug(msg,logchannel=None):
    _log_msg(LogLevel.DEBUG,msg,logchannel)

def verbose(msg,logchannel=None):
    _log_msg(LogLevel.VERBOSE,msg,logchannel)

def info(msg,logchannel=None):
    _log_msg(LogLevel.INFO,msg,logchannel)

def warning(msg,logchannel=None):
    _log_msg(LogLevel.WARNING,msg,logchannel)

def error(msg,logchannel=None):
    _log_msg(LogLevel.ERROR,msg,logchannel)


def _log_msg(level:LogLevel,msg:str,logchannel):
    if level.value >= currentLevel.value:
        if not logchannel:
            curnotifier = getNotifier()
            logchannel = curnotifier.getLogChannel() if  curnotifier and  curnotifier.getLogChannel() else _defaultLogChannel
        logchannel.write('{} {}:{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),level.name,msg))



class ExceptionHook(object):
    def __init__(self):
        sys.excepthook = self.__HandleException

    def __HandleException(self, excType, excValue, tb):
        try:
            error(exc_info=(excType, excValue, tb))
            error(traceback.format_exception(excType, excValue, tb))

        except:
            pass
        sys.__excepthook__(excType, excValue, tb)


ExceptionHook()