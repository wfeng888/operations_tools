import sys
from configparser import ConfigParser
from os import path

from public_module.config import ConfigBase, ThreadSafeHouse, cparser
from public_module.utils import none_null_stringNone


class MysqlConfig(ConfigBase):
    database:str
    logfiledir:str
    ignore_error:str

class CreateMysqlConfig(MysqlConfig):
    sqlfiledir:str
    log_statement:bool

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
    master_ip:str
    master_port:int
    master_user:str
    master_password:str
    create_slave:bool
    replica_user:str
    replica_password:str
    server_id:str

    def checkConfig(self):
        result = True
        result_msg = ''
        if (none_null_stringNone(self.host) or none_null_stringNone(self.port) or none_null_stringNone(self.ssh_password) \
                or none_null_stringNone(self.ssh_port) or none_null_stringNone(self.ssh_user) or none_null_stringNone(self.backup_base_dir)):
            result = False
            result_msg += ' host or port  or ssh_user or ssh_password or ssh_port is null '
        if self.operate == self._CONS_OPERATE_BACKUP:
            if (none_null_stringNone(self.user) or none_null_stringNone(self.password)):
                result = False
                result_msg += ' user or password is null '
            if self.backup_mode == self._CONS_BACKUP_MODE_INCREMENT:
                if none_null_stringNone(self.backup_base_dir):
                    result = False
                    result_msg += ' user or password is null '
        else:
            if (none_null_stringNone(self.restore_target_dir) or none_null_stringNone(self.mysql_software_path)):
                result = False
                result_msg += ' restore_target_dir or mysql_software_path is null '
            if self.operate == self._CONS_BACKUP_MODE_LOGIC:
                if (none_null_stringNone(self.user) or none_null_stringNone(self.password)):
                    result = False
                    result_msg += ' user or password is null '
            else:
                if self.create_slave:
                    if ( none_null_stringNone(self.master_ip) or none_null_stringNone(self.master_password) or none_null_stringNone(self.master_port)\
                             or none_null_stringNone(self.master_user) or none_null_stringNone(self.replica_password) or none_null_stringNone(self.replica_user) \
                            or none_null_stringNone(self.server_id)):
                        result = False
                        result_msg += ' create slave ,but master info is null  '
                if self.operate == self._CONS_BACKUP_MODE_INCREMENT:
                    if none_null_stringNone(self.backup_base_dir):
                        result = False
                        result_msg += ' user or password is null '
        return result,result_msg


class MasterSlaveConfig():
    master_conn_user:str
    master_conn_password:str
    master_host:str
    master_port:int
    slave_conn_user:str
    slave_conn_password:str
    slave_host:str
    slave_port:str
    repl_user:str
    repl_password:str
    gtid_enable:bool
    binlog_file:str
    binlog_pos:int

    def check_config(self):
        result = True
        result_msg = ''
        if (none_null_stringNone(self.master_conn_user) or none_null_stringNone(self.master_conn_password) or none_null_stringNone(self.master_host) or \
                none_null_stringNone(self.master_port) or none_null_stringNone(self.slave_conn_user) or none_null_stringNone(self.slave_conn_password) or \
                none_null_stringNone(self.slave_host) or none_null_stringNone(self.slave_port)):
            result = False
            result_msg += ' user or password or host or port is null '
        if not self.gtid_enable:
            if (none_null_stringNone(self.binlog_file)  or none_null_stringNone(self.binlog_pos) ):
                result = False
                result_msg += ' binlog file or binlog pos if null '
        return result,result_msg


# def getConfig():
#     _config =  threadSafeMysqlConfig.get()
#     return _config

def updateMysqlConfig(backupconfig:MysqlBackupConfig):
    return MYSQL_CONFIG.copy(backupconfig)

def initMysqlConfigFromConfigFile():
    config = MysqlConfig()
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