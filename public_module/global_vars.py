import threading

from PyQt5.QtCore import QThread

getCurrentThreadID = QThread.currentThread

notifiers = dict()
notifierLock = threading.Lock()
def addNotifier(notifyobj,type='default'):
    global notifiers,notifierLock
    notifierLock.acquire()
    curThreadid = getCurrentThreadID()
    if not notifiers.get(curThreadid,None):
        notifiers[curThreadid] = {}
    notifiers[curThreadid][type] = notifyobj
    # notifiers[notifyobj] = curThreadid
    notifierLock.release()

def removeNotifier(threadid = None,type='default'):
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
            curnotifier =  notifiers[threadid]
            if curnotifier.has_key(type):
                del curnotifier[type]
            if len(curnotifier) < 1:
                del notifiers[threadid]
            # del notifiers[curnotifier]
    except BaseException :
        pass
    finally:
        try:
            notifierLock.release()
        except BaseException:
            pass

def getNotifier(type='default'):
    global notifiers
    curThreadid = getCurrentThreadID()
    curnotifier = notifiers.get(curThreadid,None)
    if curnotifier:
        return curnotifier.get(type,None)
    return None




