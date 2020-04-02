import threading

import copy

from PyQt5.QtCore import QThread

getCurrentThreadID = QThread.currentThread

notifiers = dict()
notifierLock = threading.Lock()
def addNotifier(notifyobj):
    global notifiers,notifierLock
    notifierLock.acquire()
    curThreadid = getCurrentThreadID()
    notifiers[curThreadid] = notifyobj
    # notifiers[notifyobj] = curThreadid
    notifierLock.release()

def removeNotifier(threadid = None):
    global notifiers,notifierLock
    try:
        notifierLock.acquire()
        # if notifiers.has_key(notiobj):
        #     curThreadid = notifiers[notiobj]
        #     del notifiers[notiobj]
        #     del notifiers[curThreadid]
        if not threadid:
            threadid = getCurrentThreadID()
        if notifiers.has_key(threadid):
            # curnotifier =  notifiers[threadid]
            del notifiers[threadid]
            # del notifiers[curnotifier]
    except BaseException :
        pass
    finally:
        try:
            notifierLock.release()
        except BaseException:
            pass

def getNotifier():
    global notifiers
    curThreadid = getCurrentThreadID()
    return notifiers.get(curThreadid,None)




