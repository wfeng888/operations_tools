import sys
from configparser import ConfigParser
from os import path

from deploy.fields import FieldMeta
from public_module.global_vars import  ThreadSafeHouse


class ConfigBase(object,metaclass=FieldMeta):
    host:str
    port:int
    user:str
    password:str

    def __repr__(self):
        vs = {}
        for k in self._attribute_names:
            if k.find('password') < 0:
                vs[k] = getattr(self,k)
        return vs.__repr__()

    def copy(self,target=None):
        cls = self.__class__
        if not target:
            target = cls()
        for k in self._attribute_names:
            setattr(target,k,getattr(self,k,None))
        return target

    def update(self,source):
        if source:
            for k in (set(self._attribute_names) & set(source._attribute_names)):
                setattr(self,k,getattr(source,k,None))

    def fieldsNotNull(self):
        for k in self._attribute_names:
            if not getattr(self,k,None):
                return False
        return True

    def resetFields(self):
        for k in dir(self.__class__):
            if  not k.startswith('_') and not callable(getattr(self,k)) :
                setattr(self,k,None)

    def check_enum(self,name):
        if hasattr(self,name):
            if hasattr(self,'__'+name):
                return False if getattr(self,name) not in (getattr(self,'__'+name)).get('options') else True
            return True
        return False

class MysqlConfig(ConfigBase):
    database:str
    logfiledir:str

class CreateMysqlConfig(MysqlConfig):
    sqlfiledir:str

class BackupConfig(ConfigBase):

    _CONS_OPERATE_BACKUP='backup'
    _CONS_OPERATE_RESTORE='restore'
    _CONS_BACKUP_MODE_LOGIC = 'logic'
    _CONS_BACKUP_MODE_FULL = 'full'
    _CONS_BACKUP_MODE_INCREMENT = 'increment'

    ssh_port:int
    __ssh_port = {'options':(),'default':(22)}
    ssh_user:str
    ssh_password:str
    is_remote_host:bool

    backup_base_dir:str
    backup_dir:str
    incremental_basedir:str
    local_path:str

    restore_target_dir:str

    is_save_to_local:bool

    operate:str
    __operate = {'options':('backup','restore'),'default':()}
    backup_mode:str
    __backup_mode = {'options':('logic','full','increment'),'default':('full')}

    backup_software:str
    backup_software_path:str
    os_platform:str = sys.platform

class MysqlBackupConfig(MysqlConfig,BackupConfig):
    _CONS_BACKUP_SOFTWARE_XTRABACKUP = 'xtrabackup'
    _CONS_BACKUP_SOFTWARE_MYSQLBACKUP = 'mysqlbackup'
    _CONS_BACKUP_SOFTWARE_MYSQL = 'mysql'
    _CONS_BACKUP_SOFTWARE_MYSQLDUMP = 'mysql_dump'
    __backup_software = {'options':('xtrabackup','mysqlbackup','mysql_dump','mysql'),'default':('xtrabackup')}
    databases:list
    compress:bool
    compress_threadnum:int
    defaults_file:str
    socket_file:str
    backup_sql_file:str
    mysql_software_path:str

def _checkEqual(source,target):
    try:
        for item in target:
            if not source[item]:
                return False
    except KeyError as e:
        return False
    return True

def getConfig():
    _config =  threadSafeMysqlConfig.get()
    return _config

def updateMysqlConfig(backupconfig:MysqlBackupConfig):
    return MYSQL_CONFIG.copy(backupconfig)

def initMysqlConfigFromConfigFile():
    config = MysqlConfig()
    cparser = ConfigParser()
    cparser.read(path.join(path.split(__file__)[0],'config.ini'))
    config.user = cparser.get('mysql','user')
    config.password = cparser.get('mysql','password')
    config.host = cparser.get('mysql','host')
    config.port = cparser.get('mysql','port')
    config.database = cparser.get('mysql','database')
    return config

def initMysqlConfig(mysqlconfig:MysqlConfig):
    if mysqlconfig:
        MYSQL_CONFIG.update(mysqlconfig)

def checkConfigForMysqlCreateDB():
    global CREATE_MYSQL_CONFIG
    CREATE_MYSQL_CONFIG.update(MYSQL_CONFIG)
    return CREATE_MYSQL_CONFIG.database and CREATE_MYSQL_CONFIG.user and CREATE_MYSQL_CONFIG.port and CREATE_MYSQL_CONFIG.host and CREATE_MYSQL_CONFIG.password and CREATE_MYSQL_CONFIG.sqlfiledir

def checkConfigForMysqlAlive():
    global MYSQL_CONFIG
    return MYSQL_CONFIG.database and MYSQL_CONFIG.user and MYSQL_CONFIG.port and MYSQL_CONFIG.host and MYSQL_CONFIG.password

MYSQL_CONFIG=initMysqlConfigFromConfigFile()
CREATE_MYSQL_CONFIG = CreateMysqlConfig()
BACKUP_MYSQL_CONFIG = MysqlBackupConfig()

threadSafeMysqlConfig = ThreadSafeHouse(MYSQL_CONFIG)
threadSafeCreateMysqlConfig = ThreadSafeHouse(CREATE_MYSQL_CONFIG)
threadSafeBackupMysqlConfig = ThreadSafeHouse(BACKUP_MYSQL_CONFIG)



