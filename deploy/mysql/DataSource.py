import mysql.connector  as connector
from abc import ABCMeta, abstractmethod

from mysql.connector import InterfaceError
from mysql.connector.pooling import PooledMySQLConnection,MySQLConnectionPool

from deploy.mysql.Exception import ParamNotMatchException

from public_module.config import  MYSQL_CATEGORY,getConfig
import log
from deploy.mysql.DBUtils import formatErrorMsg



class AbstractDataSource(metaclass=ABCMeta):

    def set_class_attr(self, connParams):
        self._conn_params = {'user':connParams[0],'password':connParams[1], \
                             'host':connParams[2],'port':connParams[3],'database':connParams[4]}

    def __init__(self, *args,**kwargs):
        try:
            if args:
                self.set_class_attr(args)
            elif kwargs:
                self.set_class_attr((kwargs['user'], kwargs['password'], kwargs['host'], kwargs['port'],kwargs['database']))
        except KeyError as err:
            log.error(formatErrorMsg(err))
            raise ParamNotMatchException('database connection parames not match ')

    @abstractmethod
    def get_conn(self):
        return None

    # @property
    # def _pool(self):
    #     return self._pool
    #
    # @_pool.setter
    # def _pool(self,pool):
    #     self._pool = pool

    def close(self):
        try:
            self._pool.close()
        except:
            return False
        else:
            return True


class DBUtilPooledDBDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        from DBUtils.PooledDB import PooledDB
        # self._conn_params['use_pure'] = True
        # self._pool = PooledDB(connector,maxcached=8,maxconnections=50,**{'user':self._user_name,'password':self._pass_word,'host':self._host,'port':self._port,'database':self._data_base,'use_pure':True})
        self._pool = PooledDB(connector,maxcached=8,maxconnections=50,**self._conn_params)



    def get_conn(self):
        return self._pool.dedicated_connection()

class MysqlPooledDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        # self._conn_params['use_pure'] = True
        self._conn_params['pool_name'] = 'test_pool'
        self._conn_params['pool_size'] = 10
        # self._pool = MySQLConnectionPool(**{'user':self._user_name,'password':self._pass_word,\
        #                                     'host':self._host,'port':self._port,'database':self._data_base,\
        #                                     'use_pure':True,'pool_name':"test_pool",'pool_size':10})
        try:
            self._traceback = None
            self._pool = MySQLConnectionPool(**self._conn_params)
        except InterfaceError as e:
            log.error('MysqlPooledDataSource connect error')
            log.error(formatErrorMsg(e))
            raise e


    def get_conn(self):
        return PooledMySQLConnection(self,self._pool.get_connection())


def getDS():
    return DBUtilPooledDBDataSource(**getConfig()[MYSQL_CATEGORY])