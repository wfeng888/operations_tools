import copy
import traceback
from abc import abstractmethod, ABCMeta

import log
from public_module.Exception import ParamNotMatchException
from public_module.utils import safe_doing, formatErrorMsg


def get_key(*args,**kwargs):
    if args:
        return str(args[0]) + '_' + str(args[1]) + '_' + str(args[2]) + '_' + str(args[3])
    else:
        return str(kwargs['user']) + '_' + str(kwargs['password']) + '_' + str(kwargs['host']) + '_' + str(kwargs['port'])

class AbstractDataSource(metaclass=ABCMeta):

    _ds = {}

    def set_class_attr(self, connParams):
        self._conn_params = {'user':connParams[0],'password':connParams[1], \
                             'host':connParams[2],'port':connParams[3],'database':connParams[4]}

    def __init__(self, *args,**kwargs):
        try:
            if args:
                self.set_class_attr(args)
            elif kwargs:
                for i in ('user','password','host','port','database'):
                    kwargs.get(i)
                self._conn_params = copy.deepcopy(kwargs)
                self._closed = True
        except KeyError as err:
            log.error(formatErrorMsg(err))
            raise ParamNotMatchException('database connection parames not match ')

    @abstractmethod
    def get_conn(self):
        return None

    @classmethod
    def get_ds(cls,*args,**kwargs):
        k = get_key(*args,**kwargs)
        ds = cls._ds.get(k,None)
        if not ds or ds.is_closed():
            ds = cls(*args,**kwargs)
            cls._ds[k] = ds
        return cls._ds[k]

    @classmethod
    def destroy(cls):
        for k in cls._ds:
            safe_doing(cls._ds[k].close)

    # @property
    # def _pool(self):
    #     return self._pool
    #
    # @_pool.setter
    # def _pool(self,pool):
    #     self._pool = pool

    @abstractmethod
    def _inner_close(self):
        pass

    def close(self):
        try:
            if not self._closed:
                self._inner_close()
        except BaseException as e:
            log.error(formatErrorMsg(e))
            log.error(formatErrorMsg(traceback.format_exc()))
        self._closed = True
        return self._closed

    def is_closed(self):
        return self._closed

    @abstractmethod
    def release_conn(self,conn):
        pass