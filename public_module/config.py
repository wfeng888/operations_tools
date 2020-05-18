from configparser import ConfigParser
from os import path

from public_module.fields import FieldMeta
from public_module.utils import getCurrentThreadID


class ThreadSafeHouse(object):

    def __init__(self,mouse):
        self._store = {}
        self._mouse = mouse

    def add(self):
        curThreadid = getCurrentThreadID()
        self._store[curThreadid] = self._mouse.copy()

    def get(self):
        return self._store.get(getCurrentThreadID())

    def remove(self):
        self._store.pop(getCurrentThreadID(),None)

class ConfigBase(object,metaclass=FieldMeta):
    host:str
    port:int
    user:str
    password:str

    def __init__(self):
        self._attributes = {}
    def __repr__(self):
        vs = {}
        for k in self._attribute_names:
            if k.find('password') < 0:
                vs[k] = getattr(self,k)
        return vs.__repr__()

    def copy(self,target=None):
        cls = self.__class__
        if not target:
            target = cls()
        for k in self._attribute_names:
            setattr(target,k,getattr(self,k,None))
        return target

    def update(self,source):
        if source:
            for k in (set(self._attribute_names) & set(source._attribute_names)):
                setattr(self,k,getattr(source,k,None))

    def fieldsNotNull(self):
        for k in self._attribute_names:
            if not getattr(self,k,None):
                return False
        return True

    def resetFields(self):
        for k in dir(self.__class__):
            if  not k.startswith('_') and not callable(getattr(self,k)) :
                setattr(self,k,None)

    def check_enum(self,name):
        if hasattr(self,name):
            if hasattr(self,'__'+name):
                return False if getattr(self,name) not in (getattr(self,'__'+name)).get('options') else True
            return True
        return False


def _checkEqual(source,target):
    try:
        for item in target:
            if not source[item]:
                return False
    except KeyError as e:
        return False
    return True


cparser = ConfigParser()
cparser.read(path.join(path.split(__file__)[0],'config.ini'))




