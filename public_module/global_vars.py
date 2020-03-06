import threading
from public_module.utils import getCurrentThreadID
import copy

notifiers = dict()
notifierLock = threading.Lock()
def addNotifier(notifyobj):
    global notifiers,notifierLock
    notifierLock.acquire()
    curThreadid = getCurrentThreadID()
    notifiers[curThreadid] = notifyobj
    notifiers[notifyobj] = curThreadid
    notifierLock.release()

def removeNotifier(notiobj=None,threadid = None):
    global notifiers,notifierLock
    try:
        notifierLock.acquire()
        if notifiers.has_key(notiobj):
            curThreadid = notifiers[notiobj]
            del notifiers[notiobj]
            del notifiers[curThreadid]
        if notifiers.has_key(threadid):
            curnotifier =  notifiers[threadid]
            del notifiers[threadid]
            del notifiers[curnotifier]
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


class ThreadSafeHouse(object):

    def __init__(self,mouse):
        self._store = {}
        self._mouse = mouse

    def add(self):
        curThreadid = getCurrentThreadID()
        self._store[curThreadid] = copy.deepcopy(self._mouse)

    def get(self):
        return self._store.get(getCurrentThreadID())

    def remove(self):
        self._store.pop(getCurrentThreadID(),None)

