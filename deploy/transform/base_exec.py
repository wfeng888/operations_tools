import traceback
from enum import Enum

import log
from deploy import UnSupportOperation
from deploy.transform import oper

FLAG_ERROR_TERMINATE = 1



class BaseExec:
    def __init__(self,stage:Enum,executor:{}):
        self._executor = executor

    def start(self,sqllist:{},stage):
        _failures = 0
        for i in stage:
            try:
                s = sqllist.get(i,None)
                if s:
                    log.debug('begin stage: %s. '%i)
                    for item in s:
                        _func = None
                        if item[0] == oper.EXEC:
                            _func = lambda: self.exec(item[1],item[2])
                        elif item[0] == oper.INSERT:
                            _func = lambda: self.insert(item[1],item[2],item[3],item[4],FLAG_ERROR_TERMINATE)
                        else:
                            raise UnSupportOperation('UnSupport Operation %s'%item[0].name())
                        if -1 == _func():
                            _failures += 1
                            if FLAG_ERROR_TERMINATE == self._getflag(item)&FLAG_ERROR_TERMINATE:
                                return i,_failures
                    log.debug('finished stage: %s. '%i)
            except BaseException as e:
                log.error(traceback.format_exc())
        return i,_failures


    def exec(self,ds,sql):
        log.debug('exec statement %s '%sql)
        _result = self._executor.get(ds).exec_statement(sql)
        if -1 == _result:
            self._executor.get(ds).exec_statement('rollback')
            log.error(' faild. ')
        else :
            self._executor.get(ds).exec_statement('commit')
            log.debug(' success. ')
        return _result

    def insert(self,s_ds,s_sql,i_ds,i_sql,flag):
        _batch_size = 500
        _row_count = 0
        _total_size = 0
        _failures = 0
        _s_exector = self._executor[s_ds]
        _i_exector = self._executor[i_ds]
        log.debug('select statement %s '%s_sql)
        log.debug('insert statement %s '%i_sql)
        for _result_set in _s_exector.query(s_sql,batchsize=_batch_size):
            if _result_set:
                if i_sql:
                    _row_count = _i_exector.insert(i_sql,_result_set)
                else:
                    _result_set =  [ _item[0] for _item  in _result_set ]
                    _i_exector.insert(_result_set)
                if _row_count>=0 :
                    _total_size += _row_count
                    log.debug('insert row_counts: %d'%_row_count)
                elif -1 == _row_count:
                    _failures += 1
                    if FLAG_ERROR_TERMINATE == FLAG_ERROR_TERMINATE&flag:
                        _i_exector.exec_statement('rollback')
                        return -1
        _i_exector.exec_statement('commit')
        log.debug('total insert %d records. '%_total_size)
        return _total_size

    def _getflag(self,item):
        _len = len(item)
        if _len in (4,6):
            return item[_len - 1 ]
        return FLAG_ERROR_TERMINATE

    def _test_exec(self,func,flag):
        pass