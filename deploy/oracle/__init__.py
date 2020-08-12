import cx_Oracle
from cx_Oracle import  Error

import log
from public_module.config import ConfigBase
from public_module.datasource import AbstractDataSource
from public_module.sql_execute import AbstractSQLExecute, initial_only


# Set the NLS_DATE_FORMAT for a session
def initSession(connection, requestedTag):
    with connection.cursor() as cursor:
        cursor.execute("""
            begin
            execute immediate 'ALTER SESSION SET NLS_DATE_FORMAT = ''YYYY-MM-DD HH24:MI'' nls_language = AMERICAN';
            end;
            """)

class OraclePooledDBDataSource(AbstractDataSource):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)

        self._pool = cx_Oracle.SessionPool(self._conn_params.get('user'), self._conn_params.get('password'), '%s:%d/%s' % (self._conn_params.get('host'),int(self._conn_params.get('port')),self._conn_params.get('database')),
                                     min=2, max=5, increment=1, threaded=True, sessionCallback=initSession, encoding="UTF-8")
        self._closed = False



    def _inner_close(self):
        self._pool.close()

    def get_conn(self):
        return self._pool.acquire()

    def release_conn(self,conn):
        self._pool.release(conn)


class OracleSQLExecute(AbstractSQLExecute):

    def __init__(self,connection=None,ds=None):
        super(OracleSQLExecute, self).__init__(connection,ds)


    def exception_handle(self,e) -> int:
        if isinstance(e,Error):
            log.error(self._formatErrorMsg(e))
            return 1
        return -1

    def _formatErrorMsg(self,e):
        if not isinstance(e,(tuple,list)):
            e=(e,)
        _s = ''
        for item in e:
            for _r in item.args:
                _s += 'Error %s , at row offset %s  ;'%(getattr(_r,'message',None),getattr(_r,'offset',None))
        return _s

    @initial_only
    def executemany(self,stat,params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.executemany(stat,params,batcherrors=True)
                for error in cursor.getbatcherrors():
                    log.error("Error", error.message, "at row offset", error.offset)
                return cursor.rowcount
        except BaseException as e:
            self.handle_exception(e)
            return -1

    def with_rows(self,cursor):
        return True

    @initial_only
    def isDBExists(self,dbname):
        if self._conn:
            return True
        return False

    def getVariable(self,variablename,globalv=False):
        return None


    def batch_exec(self,statements):
        _stat = 'begin '
        for stat in statements:
            _stat += stat
        _stat += 'end ;'
        return self.exec_statement(_stat)


class OracleConfig(ConfigBase):
    service:str