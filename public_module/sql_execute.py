import traceback
from abc import ABCMeta, abstractmethod
from functools import wraps

import log
from public_module.Exception import ParamNotMatchException
from public_module.utils import record_log


def initial_only(func):
    @wraps(func)
    def _inner_func(self,*args,**kwargs):
        self._init_conn()
        return func(self,*args,**kwargs)
    return _inner_func

class AbstractSQLExecute(metaclass=ABCMeta):
    def __init__(self,connection=None,ds=None):
        if not (connection or ds):
            raise ParamNotMatchException()
        self._conn = connection
        self._ds = ds

    def _init_conn(self):
        if not self._conn:
            self._conn = self._ds.get_conn()

    def formatErrorMsg(self,e):
        try:
            return self._formatErrorMsg(e)
        except BaseException:
            return traceback.format_exc()

    @initial_only
    @abstractmethod
    def _formatErrorMsg(self,e):
        pass

    @initial_only
    @abstractmethod
    def exception_handle(self,e) -> int:
        pass


    def handle_exception(self,e):
        if self.exception_handle(e) < 0:
            log.error(traceback.format_exc())

    @initial_only
    def exec_stts(self,statements,log_statement=False,error_terminate=True):
            for i in range(len(statements)):
                stt = statements.popleft()
                # if config.log_statement:
                #     log.info('exec statement:{}'.format(stt))
                if -1 == self.exec_statement(stt):
                    break
                    return -1
            return 0

    @initial_only
    def  exec_statement(self,statement):
        with self._conn.cursor() as cursor:
            try:
                cursor.execute(statement)
            except BaseException as e:
                self.handle_exception(e)
                return -1
            return 0

    @initial_only
    def query(self,stat,params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.execute(stat,params)
                if cursor.with_rows:
                    return cursor.fetchall()
                return ()
        except BaseException as e:
            if self.exception_handle(e) < 0:
                log.error(traceback.format_exc())
            return -1

    @initial_only
    def insert(self,statement,params=()):
        if params:
            return self.executemany(statement,params)
        else:
            return self.batch_exec(statement)

    @abstractmethod
    def with_rows(self,cursor):
        pass

    @initial_only
    def query(self,statement,params=(),batchsize=-1):
        with self._conn.cursor() as cursor:
            cursor.execute(statement,params)
            if self.with_rows(cursor):
                if batchsize < 1 :
                    return cursor.fetchall()
                else:
                    _size = batchsize
                    while _size > 0:
                        _rows = cursor.fetchmany(batchsize)
                        _size = len(_rows)
                        yield _rows
            return ()

    @initial_only
    def executemany(self,statement,params=()):
        try:
            with self._conn.cursor() as cursor:
                cursor.executemany(statement,params)
                return cursor.rowcount
        except BaseException as e:
            self.handle_exception(e)
            return -1


    @abstractmethod
    def isDBExists(self,dbname):
        pass

    @abstractmethod
    def getVariable(self,variablename,globalv=False):
        pass

    @abstractmethod
    def batch_exec(self,statement):
        pass