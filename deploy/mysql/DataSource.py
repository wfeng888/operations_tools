import mysql.connector  as connector

from mysql.connector import InterfaceError
from mysql.connector.pooling import PooledMySQLConnection,MySQLConnectionPool

import log
from deploy.mysql.DBUtils import formatErrorMsg
from deploy.mysql.mysql_config import  MYSQL_CONFIG
from public_module.datasource import AbstractDataSource


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

    def release_conn(self,conn):
        conn.close()



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

    def release_conn(self,conn):
        conn.close()

# def getDS():
#     return DBUtilPooledDBDataSource.get_ds(**getConfig()[MYSQL_CATEGORY])


def getDS(*args,**kwargs):
    if not ( args or kwargs ):
        return DBUtilPooledDBDataSource.get_ds(*(MYSQL_CONFIG.user,MYSQL_CONFIG.password,MYSQL_CONFIG.host,MYSQL_CONFIG.port,MYSQL_CONFIG.database))
    return DBUtilPooledDBDataSource.get_ds(*args,**kwargs)

def destroyDS():
    DBUtilPooledDBDataSource.destroy()