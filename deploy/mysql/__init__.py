from public_module.ssh_connect import ConnectionBase


class BackupException(Exception):
    def __init__(self,msg):
        self._msg = msg

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
    def __init__(self,msg):
        if msg:
            self._msg = msg
        super(CheckMysqlBackupFileException, self).__init__(self._msg)

class ReadBackupParamException(BackupException):
    _msg = 'read backup param failed,please check backup param file '
    def __init__(self,filepath):
        if filepath:
            self._msg += ' ' + filepath
        super(ReadBackupParamException, self).__init__(self._msg)



class ReadBackupConfigFileException(BackupException):
    _msg = 'read backup param failed,please check backup config file '
    def __init__(self,filepath):
        if filepath:
            self._msg += ' ' + filepath
        super().__init__(self._msg)

class BackupDecompressException(BackupException):
    _msg = 'decompress backup directory %s failed. decompress need install qpress software '
    def __init__(self,filepath):
        if filepath:
            self._msg += ' ' + filepath
        super().__init__(self._msg)


class EnvironmentCheckException(BackupException):
    _msg = 'Environment check failed! '
    def __init__(self,filepath):
        if filepath:
            self._msg += ' ' + filepath
        super().__init__(self._msg)


def checkStatAndRaise(stat,cls,*args):
    if stat != ConnectionBase.SHELL_SUCCESS:
        raise cls(*args)