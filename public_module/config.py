
from configparser import ConfigParser
from os import path

from deploy.fields import FieldMeta
import log
from public_module.global_vars import  ThreadSafeHouse

MYSQL_CATEGORY = 'mysql'
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

class MysqlConfig(ConfigBase):
    database:str


class BackupConfig(MysqlConfig):
    ssh_port:int
    ssh_user:str
    ssh_password:str
    backup_base_dir:str
    backup_mode:str
    full_backup_base:str
    databases:list
    compress:bool
    compress_threadnum:int
    defaults_file:str
    socket_file:str





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


threadSafeConfig = ThreadSafeHouse(CONFIG)



