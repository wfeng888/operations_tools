import time
from enum import Enum


class LogLevel(Enum):
    DEBUG = 0
    VERBOSE = 1
    INFO = 2
    WARNING = 3
    ERROR = 4

currentLevel = LogLevel.WARNING

def debug(msg):
    if LogLevel.DEBUG.value >= currentLevel.value:
        _log_msg(LogLevel.DEBUG,msg)

def verbose(msg):
    if LogLevel.VERBOSE.value >= currentLevel.value:
        _log_msg(LogLevel.VERBOSE,msg)

def info(msg):
    if LogLevel.INFO.value >= currentLevel.value:
        _log_msg(LogLevel.INFO,msg)

def warning(msg):
    if LogLevel.WARNING.value >= currentLevel.value:
        _log_msg(LogLevel.WARNING,msg)

def error(msg):
    if LogLevel.ERROR.value >= currentLevel.value:
        _log_msg(LogLevel.ERROR,msg)

def _log_msg(level:LogLevel,msg:str):
    print('{} {}:{}'.format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())),currentLevel.name,msg)