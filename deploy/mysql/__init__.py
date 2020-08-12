from mysql.connector import Error

import log
from public_module.sql_execute import AbstractSQLExecute, initial_only
from public_module.ssh_connect import ConnectionBase


class BackupException(Exception):
    _msg =  ' '
    def __init__(self,msg):
        if msg:
            self._msg += ' ' + msg

    def __repr__(self):
        return self._msg

class MysqlCnfFileNotExistsException(BackupException):
    pass

class MysqldNotRunningException(BackupException):
    pass

class MysqlVersionNotMatchException(BackupException):
    pass

class FileCopyException(BackupException):
    pass

class CheckMysqlBackupFileException(BackupException):
    _msg = 'check backup file failed , is the backup file exists ? the other reason may be the last backup had not completed success!'


class ReadBackupParamException(BackupException):
    _msg = 'read backup param failed,please check backup param file '

class ReadRemoteFileContentException(BackupException):
    _msg = 'read backup param failed,please check backup param file '

class ReadBackupConfigFileException(BackupException):
    _msg = 'read backup param failed,please check backup config file '


class BackupDecompressException(BackupException):
    _msg = 'decompress backup directory %s failed. decompress need install qpress software '


class EnvironmentCheckException(BackupException):
    _msg = 'Environment check failed! '


class RestoreFailedException(BackupException):
    _msg =  'Restore failed! '

class BackupFailedException(BackupException):
    _msg =  'Backup failed! '


def checkStatAndRaise(stat,cls,*args):
    if stat != ConnectionBase.SHELL_SUCCESS:
        raise cls(*args)



class MySQLSQLExecute(AbstractSQLExecute):

    def __init__(self,connection=None,ds=None):
        super(MySQLSQLExecute, self).__init__(connection,ds)


    def exception_handle(self,e) -> int:
        if isinstance(e,Error):
            log.error(self._formatErrorMsg(e))
            return 1
        return -1

    def _formatErrorMsg(self,e):
        return ('error_num:%d,error_msg:%s' %(e.errno,e.msg))


    def with_rows(self,cursor):
        return cursor.with_rows

    @initial_only
    def isDBExists(self,dbname):
        try:
            self._conn.database = dbname
            return True
        except Error as e:
            log.error(self._formatErrorMsg(e))
        return False

    def getVariable(self,variablename,globalv=False):
        stat = 'select @@{}'.format(variablename)
        try:
            return self.query(stat)[0][0]
        except Error as e:
            log.error(self._formatErrorMsg(e))
            return None


    @initial_only
    def batch_exec(self,statements):
        _stats = ''
        if not isinstance(statements,(tuple,list)):
            statements = (statements,)
        for _item in statements:
            _stats += _item
        with self._conn.cursor() as cursor:
            return cursor.execute(_stats,multi=True)