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