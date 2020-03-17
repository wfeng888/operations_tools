import os
import sys
from configparser import ConfigParser
from os import path

from deploy.fields import FieldMeta
import log
from public_module.global_vars import  ThreadSafeHouse

MYSQL_CATEGORY = 'mysql_pub'
MYSQL_BACKUP_CATEGORY = 'mysql_backup'
MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG = 'sqldirectory'
MYSQL_GENERAL_CONFIG = ('host','port','user','password','database')
MYSQL_CREATEDB_CONFIG = list()
MYSQL_CREATEDB_CONFIG.extend(MYSQL_GENERAL_CONFIG)
MYSQL_CREATEDB_CONFIG.append(MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG)


class ConfigBase(object,metaclass=FieldMeta):
    host:str
    port:int
    user:str
    password:str

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

class MysqlConfig(metaclass=FieldMeta):
    database:str

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

    def check_backupconfig(self):
        return True
        if not (self.check_enum('backup_mode') and self.check_enum('operate') ):
            return False
        if self.backup_mode in ('logic'):
            if not self.backup_sql_file:
                return False
        if self.backup_mode not in ('logic') and not self.defaults_file :
            return False
        if not (self.socket_file or self.port):
            return False

        if self.remote_host and not( self.ssh_password and self.ssh_port and self.ssh_user):
            return False

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

def init_mysqlconfig(**kw):
    global CONFIG
    mysqlconfig = MysqlConfig()
    if not kw:
        mConfigParser = ConfigParser();
        mConfigParser.read(path.join(path.split(__file__)[0],'config.ini'),'utf-8')
        kw = {}
        for k,v in mConfigParser.items(MYSQL_CATEGORY):
            kw[k] = v
    try:
        if not CONFIG.get(MYSQL_CATEGORY):
            CONFIG[MYSQL_CATEGORY] = {}
        CONFIG[MYSQL_CATEGORY]['host'] = mysqlconfig.host = kw['host']
        CONFIG[MYSQL_CATEGORY]['port'] = mysqlconfig.port = kw['port']
        CONFIG[MYSQL_CATEGORY]['user'] = mysqlconfig.user = kw['user']
        CONFIG[MYSQL_CATEGORY]['password'] = mysqlconfig.password = kw['password']
        CONFIG[MYSQL_CATEGORY]['database'] = mysqlconfig.database = kw['database']
    except KeyError as e:
        log.error("set mysql config failed!")
        del CONFIG[MYSQL_CATEGORY]

def setSQLFileDirectory(dir):
    global CONFIG
    CONFIG[MYSQL_CATEGORY][MYSQL_CREATEDB_SQL_DIRECTORY_CONFIG] = dir


def _checkEqual(source,target):
    try:
        for item in target:
            if not source[item]:
                return False
    except KeyError as e:
        return False
    return True

def checkConfigForMysqlCreateDB():
    global CONFIG
    return _checkEqual(CONFIG[MYSQL_CATEGORY],MYSQL_CREATEDB_CONFIG)


def checkGeneralConfigForMysql():
    global CONFIG
    return _checkEqual(CONFIG[MYSQL_CATEGORY],MYSQL_GENERAL_CONFIG)




def getMysqlHost():
    return CONFIG[MYSQL_CATEGORY].get('host')

def getMysqlPort():
    return CONFIG[MYSQL_CATEGORY].get('port')

def getMysqlUser():
    return CONFIG[MYSQL_CATEGORY].get('user')

def getMysqlDatabase():
    return CONFIG[MYSQL_CATEGORY].get('database')

def getMysqlPassword():
    return CONFIG[MYSQL_CATEGORY].get('password')

def getConfig():
    _config =  threadSafeConfig.get()
    return _config if _config else CONFIG

CONFIG = {}
init_mysqlconfig()



def updateBackConfig(backupconfig:BackupConfig):
    global CONFIG
    backconfig_keys = [k for k in dir(BackupConfig) if not k.startswith('_') and not callable(getattr(backupconfig,k)) ]
    if CONFIG.get(MYSQL_CATEGORY,'None'):
        for k in CONFIG[MYSQL_CATEGORY].keys():
            if k in backconfig_keys:
                setattr(backupconfig,k,CONFIG[MYSQL_CATEGORY][k])
    if not backupconfig.check_backupconfig():
        return False
    CONFIG[MYSQL_BACKUP_CATEGORY] = {}
    for k in dir(BackupConfig):
        if not k.startswith('_') and not callable(getattr(backupconfig,k)):
            CONFIG[MYSQL_BACKUP_CATEGORY][k] = getattr(backupconfig,k)
    return True


threadSafeConfig = ThreadSafeHouse(CONFIG)



