import copy
import traceback

import mysql.connector  as connector
from abc import ABCMeta, abstractmethod

from mysql.connector import InterfaceError
from mysql.connector.pooling import PooledMySQLConnection,MySQLConnectionPool

from deploy.mysql.Exception import ParamNotMatchException

import log
from deploy.mysql.DBUtils import formatErrorMsg
from deploy.until import safe_doing
from public_module.config import getConfig, MYSQL_CATEGORY

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
                # self.set_class_attr((kwargs['user'], kwargs['password'], kwargs['host'], kwargs['port'],kwargs['database']))
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
            safe_doing(cls._ds[k].close())

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

    @abstractmethod
    def is_closed(self):
        pass

class DBUtilPooledDBDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        from DBUtils.PooledDB import PooledDB
        # self._conn_params['use_pure'] = True
        self._pool = PooledDB(connector,maxcached=8,maxconnections=50,**self._conn_params)
        self._closed = False

    def _inner_close(self):
        self._pool.close()

    def get_conn(self):
        return self._pool.dedicated_connection()


class MysqlPooledDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # self._conn_params['use_pure'] = True
        self._conn_params['pool_name'] = 'test_pool'
        self._conn_params['pool_size'] = 10
        try:
            self._pool = MySQLConnectionPool(**self._conn_params)
            self._closed = False
        except InterfaceError as e:
            log.error('MysqlPooledDataSource connect error')
            log.error(formatErrorMsg(e))
            raise e

    def _inner_close(self):
        self._pool.close()

    def get_conn(self):
        return PooledMySQLConnection(self,self._pool.get_connection())

# def getDS():
#     return DBUtilPooledDBDataSource.get_ds(**getConfig()[MYSQL_CATEGORY])


def getDS(*args,**kwargs):
    if not ( args or kwargs ):
        return DBUtilPooledDBDataSource.get_ds(**getConfig()[MYSQL_CATEGORY])
    return DBUtilPooledDBDataSource.get_ds(*args,**kwargs)

def destroyDS():
    DBUtilPooledDBDataSource.destroy()