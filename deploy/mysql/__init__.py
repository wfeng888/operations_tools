

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