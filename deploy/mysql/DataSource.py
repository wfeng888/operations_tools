from deploy import mysql as connector
from abc import ABCMeta, abstractmethod

from deploy.mysql import InterfaceError
from deploy.mysql import PooledMySQLConnection,MySQLConnectionPool

from Exceptions import ParamNotMatchException


class AbstractDataSource(metaclass=ABCMeta):

    def set_class_attr(self, connParams):
        # self._host = connParams[1]
        # self._port = connParams[2]
        # self._user_name = connParams[3]
        # self._pass_word = connParams[4]
        # self._data_base = connParams[5]
        self._conn_params = {'user':connParams[0],'password':connParams[1], \
                             'host':connParams[2],'port':connParams[3],'database':connParams[4]}

    def __init__(self, *args,**kwargs):
        try:
            if args:
                self.set_class_attr(args)
            elif kwargs:
                self.set_class_attr((kwargs['user'], kwargs['password'], kwargs['host'], kwargs['port'],kwargs['database']))
        except KeyError as err:
            print(err.with_traceback())
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
        self._conn_params['use_pure'] = True
        # self._pool = PooledDB(connector,maxcached=8,maxconnections=50,**{'user':self._user_name,'password':self._pass_word,'host':self._host,'port':self._port,'database':self._data_base,'use_pure':True})
        self._pool = PooledDB(connector,maxcached=8,maxconnections=50,**self._conn_params)



    def get_conn(self):
        return self._pool.dedicated_connection()



class MysqlPooledDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self._conn_params['use_pure'] = True
        self._conn_params['pool_name'] = 'test_pool'
        self._conn_params['pool_size'] = 10
        # self._pool = MySQLConnectionPool(**{'user':self._user_name,'password':self._pass_word,\
        #                                     'host':self._host,'port':self._port,'database':self._data_base,\
        #                                     'use_pure':True,'pool_name':"test_pool",'pool_size':10})
        try:
            self._traceback = None
            self._pool = MySQLConnectionPool(**self._conn_params)
        except InterfaceError as e:
            print('MysqlPooledDataSource connect error')
            e.with_traceback(self._traceback)
            raise e


    def get_conn(self):
        return PooledMySQLConnection(self,self._pool.get_connection())