import configparser
import os
import re
import time
import traceback
from configparser import ConfigParser
from os import path

import log
from deploy.fields import FieldMeta
from deploy.mysql import DBUtils
from deploy.mysql.DBUtils import safe_close, getVariable
from deploy.mysql.DataSource import getDS
from deploy.mysql.constant import MYSQL57_CNF_VAR_PREFERENCE
from public_module import to_bytes, to_text, ContextManager
from public_module.config import BackupConfig, threadSafeConfig
import public_module.config as config
from public_module.ssh_connect import ConnectionBase

from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import formatDate, none_null_stringNone, record_log, string_true_bool, path_join


class ConfigWriter(object):
    def __init__(self):
        self._content = ''

    def write(self,msg):
        self._content += msg

    def get(self):
        return self._content

class BackupBase(ContextManager):

    RESULT_SUCCESS,RESULT_PARTIAL_SUCCESS,RESULT_FAIL = range(3)

    result_stat = RESULT_FAIL
    cmd:str
    user = ['--user',None]
    password = ['--password',None]
    port = ['--port',None]

    def __init__(self,sshobject:ParamikoConnection,backupconfig):
        self._sshobject = sshobject
        self._config = backupconfig

    def updateConfig(self):
        self.user[1] = self._config.user
        self.password[1] = self._config.password
        self.port[1] = self._config.port

    def prepareEnv(self):
        pass

    def preInit(self):
        self._config.backup_dir = path_join(self._config.backup_base_dir,formatDate())


    def beforeBackup(self):
        pass

    def do_backup(self):
        pass

    def afterBackup(self):
        pass

    def beforeRestore(self):
        pass

    def do_restore(self):
        pass

    def afterRestore(self):
        pass

    def close(self):
        del self._config
        self._sshobject.close()

    @record_log
    def doAction(self):
        self.preInit()
        self.updateConfig()
        self.prepareEnv()
        if self._config.operate == BackupConfig._CONS_OPERATE_BACKUP:
            self.beforeBackup()
            if self.do_backup() == ConnectionBase.SHELL_SUCCESS:
                self.result_stat = self.RESULT_PARTIAL_SUCCESS
                if self.afterBackup() == ConnectionBase.SHELL_SUCCESS:
                    self.result_stat = self.RESULT_SUCCESS
            else:
                self.result_stat = self.RESULT_FAIL
        else:
            self.beforeRestore()
            if self.do_restore() == ConnectionBase.SHELL_SUCCESS:
                self.result_stat = self.RESULT_PARTIAL_SUCCESS
                if self.afterRestore() == ConnectionBase.SHELL_SUCCESS:
                    self.result_stat = self.RESULT_SUCCESS
            else:
                self.result_stat = self.RESULT_FAIL
        return self.result_stat

    def getLocalTmpDir(self):
        return path.split(__file__)[0]


class MysqlBackup(BackupBase):

    backup_param:str
    softwarepath:str
    software = ['software',None]
    login_path = ['--login-path',None]
    target_dir = ['--target-dir',None]

    def close(self):
        safe_close(self._conn)
        super(MysqlBackup, self).close()


    def __init__(self, sshobject, backupconfig: config.MysqlBackupConfig, ds=None, conn=None):
        super(MysqlBackup, self).__init__(sshobject,backupconfig)
        if not conn:
            self._ds = ds if ds else getDS(*(self._config.user,self._config.password,self._config.host,self._config.port,self._config.database))
            self._conn = self._ds.get_conn()
        else:
            self._conn = conn

    @record_log
    def getMysqldCommand(self):
        cmd = 'sudo netstat -apn|grep -w ' + str(self._config.port) + ' |grep -w LISTEN|sed \'s= \{1,\}= =g\'|cut -d \' \' -f 7|cut -d \'/\' -f 1|xargs ps --no-headers  -f -p |sed \'s= \{1,\}= =g\'|cut -d \' \' -f8-'
        stat,data = self._sshobject.execute_cmd(cmd,False)
        if stat == ConnectionBase.SHELL_SUCCESS:
            return data
        return None

    def setSoftWarePath(self):
        pass


    def preInit(self):
        super(MysqlBackup, self).preInit()

    @record_log
    def prepareEnv(self):
        super(MysqlBackup, self).prepareEnv()
        if self._sshobject.fileExists(self.target_dir[1]):
            self._sshobject.rename(self.target_dir[1])
        if self._sshobject.mkdir(self.target_dir[1]):
            return ConnectionBase.SHELL_SUCCESS
        return ConnectionBase.SHELL_FAILED

class MysqlHotBackup(MysqlBackup):
    defaults_file = ['--defaults-file',None]
    defaults_extra_file = ['--defaults-extra-file',None]
    defaults_group_suffix = ['--defaults-group-suffix',None]
    socket = ['--socket',None]

    @record_log
    def makeCnf(self):
        cnf = ConfigParser(allow_no_value=True)
        for sec in MYSQL57_CNF_VAR_PREFERENCE.keys():
            cnf.add_section(sec)
            for option in MYSQL57_CNF_VAR_PREFERENCE[sec]:
                if isinstance(option,(list,tuple)):
                    cnf.set(sec,option[0],str(getVariable(option[1].replace('-','_'),self._conn)))
                else:
                    cnf.set(sec,option,str(getVariable(option.replace('-','_'),self._conn)))
        cw = ConfigWriter()
        cnf.write(cw)
        tmpcnfpath = ('~/backup_my.cnf')
        self._sshobject.execute_cmd('echo "' + cw.get() + '" > ' + tmpcnfpath)
        return tmpcnfpath

    @record_log
    def setCnfFile(self,cnffile=None,force=False):
        if not none_null_stringNone(self.defaults_file[1]) and not force:
            return
        if self._config.operate == BackupConfig._CONS_OPERATE_BACKUP:
            data = to_text(self.getMysqldCommand())
            if data:
                r = re.search('(socket)=([\S]+)',data)
                if r:
                    self.setSocket(r.group(2))
                r = re.search('(defaults-file)=([\S]+)',data)
                if r:
                    self.defaults_file[1] = r.group(2)
                    return
            self.defaults_file[1] = self.makeCnf()
        else:
            if self._sshobject.fileExists(path_join(self._config.backup_dir,'my.cnf')):
                self.defaults_file[1] = path_join(self._config.backup_dir,'my.cnf')

    @record_log
    def setSocket(self,socketfile=None,force=False):
        if not none_null_stringNone(self.socket[1]) and not force:
            return
        self.socket[1] = socketfile if socketfile else getVariable('socket',self._conn)



    @record_log
    def do_backup(self):
        log.debug('doing backup')
        self.cmd = self.getBackupCmd()
        stat,data =self._sshobject.execute_cmd(self.cmd)
        if stat == ConnectionBase.SHELL_SUCCESS:
            self.result_stat = self.RESULT_PARTIAL_SUCCESS
        return stat

    def formatOption(self,opt:str):
        results = []
        if opt:
            opts = opt.strip().split()
            for i in opts:
                values = i.partition('=')
                results.append(values)
        return results

    @record_log
    def afterBackup(self):
        param = ConfigParser(allow_no_value=True)
        param.set(None,'cmd',self.cmd)
        opts = self.formatOption(self.backup_param)
        if opts:
            for i in opts:
                param.set(None,i[0],i[2])
        tmppath = path.join(self.getLocalTmpDir(),'backup.param')
        with open(tmppath,'w') as wf:
            param.write(wf)
            wf.flush()
        if self._sshobject.transferFileToRemote(tmppath,path_join(self.target_dir[1],'backup.param')):
            return ConnectionBase.SHELL_SUCCESS
        return ConnectionBase.SHELL_FAILED

    @record_log
    def updateConfig(self):
        super(MysqlHotBackup, self).updateConfig()
        self.setSoftWarePath()
        self.setBackupDir()
        self.setCnfFile()
        self.setSocket()

class Xtrabackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(Xtrabackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.software[1] = 'xtrabackup'

    backup = '--backup'
    prepare = '--prepare'
    apply_log_only = '--apply-log-only'
    target_dir = ['--target-dir',None]
    stats = '--stats'
    export = '--export'
    print_param = '--print-param'
    use_memory = ['--use-memory',None]
    throttle = ['--throttle',None]
    log = ['--log',None]
    log_copy_interval = ['--log-copy-interval',None]
    extra_lsndir = ['--extra-lsndir',None]
    incremental_lsn = ['--incremental-lsn',None]
    incremental_basedir = ['--incremental-basedir',None,None]
    incremental_dir = ['--incremental-dir',None]
    to_archived_lsn = ['--to-archived-lsn',None]
    tables = ['--tables',None]
    _tables_file = ['--tables-file',None]
    databases = ['--databases',None]
    databases_file = ['--databases-file',None]
    tables_exclude = ['--tables-exclude',None]
    databases_exclude = ['--databases-exclude',None]
    stream = ['--stream',None]
    compress = ['--compress','quicklz',None]
    compress_threads = ['--compress-threads',None]
    compress_chunk_size = ['--compress-chunk-size',None]
    encrypt = ['--encrypt',None]
    copy_back = '--copy-back'
    move_back = '--move-back'
    slave_info = '--slave-info'
    safe_slave_backup = '--safe-slave-backup'
    safe_slave_backup_timeout = ['--safe-slave-backup-timeout',3000]
    rsync = '--rsync'
    decompress = '--decompress'
    parallel = ['--parallel',4,True]
    log_bin = ['--log-bin',None]


    @record_log
    def setSoftWarePath(self):
        cmd = 'which ' + self.software[1]
        nostr = 'no ' + self.software[1] + ' in'
        stat,data = self._sshobject.execute_cmd(cmd,False)
        if stat == ConnectionBase.SHELL_SUCCESS:
            data = to_text(data)
            for s in data.splitlines():
                i = s.find(nostr)
                if i >= 0 :
                    return None
            self.softwarepath = data.replace('\r','').replace('\n','')

    @record_log
    def updateConfig(self):
        super(Xtrabackup, self).updateConfig()
        self.compress[2] = self._config.compress
        if string_true_bool(self.compress[2]):
            self.compress_threads[1] = 4


    @record_log
    def compactItem(self,erase,*args):
        cmd = ''
        for item in args:
            if isinstance(item,(list,tuple)):
                if len(item) > 2 and string_true_bool(item[2]) or len(item) == 2:
                    name = item[0]
                    if erase:
                        name = item[0].lstrip('-')
                    cmd += ' ' + name
                    if not none_null_stringNone(item[1]):
                        cmd += '=' + str(item[1])
            else:
                cmd += ' ' + str(item)
        return cmd

    @record_log
    def getBackupCmd(self):
        cmd = self.compactItem(False,self.softwarepath,self.defaults_file,self.user,self.password,self.target_dir,self.slave_info,self.safe_slave_backup,self.safe_slave_backup_timeout,self.socket,self.compress,self.compress_threads,self.incremental_basedir,self.backup,'2>&1')
        self.backup_param = self.compactItem(True,self.software,self.compress,self.incremental_basedir)
        return cmd

    @record_log
    def afterBackup(self):
        log.debug('after backup')
        return super(Xtrabackup, self).afterBackup()

    @record_log
    def setBackupDir(self):
        if self.target_dir[1]:
            return self.target_dir[1]
        else:
            if self._config.operate == BackupConfig._CONS_OPERATE_BACKUP:
                self.target_dir[1] = self._config.backup_dir if self._config.backup_dir else self._config.backup_base_dir + '/' + formatDate()

class MysqlEnterpriseBackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlEnterpriseBackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.software[1] = 'mysqlbackup'

class MysqlLogicBackup(MysqlBackup):


    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlLogicBackup, self).__init__(sshobject,backupconfig,ds,conn)
        if self._config.operate == self._config._CONS_OPERATE_BACKUP:
            self.software[1] = 'mysqldump'
        else:
            self.software[1] = 'mysql'

    def setSoftWarePath(self):
        data = self.getMysqldCommand()
        if data:
            data = to_text(data).replace('--','')
            res = data.partition(' ')
        self.softwarepath = path_join(path.dirname(res[0]),self.software[1])


def backup_restore(backupconfig: config.MysqlBackupConfig):
    with ParamikoConnection(backupconfig.host,backupconfig.ssh_user,backupconfig.ssh_password,backupconfig.ssh_port) as pk:
        ba = None
        if backupconfig.backup_mode == config.MysqlBackupConfig._CONS_BACKUP_MODE_LOGIC:
            ba = MysqlLogicBackup(pk,backupconfig)
        else:
            ba = Xtrabackup(pk,backupconfig)
        stat = ba.doAction()
        if stat == BackupBase.RESULT_SUCCESS:
            msg = ' completely successful ! Congratulations ! '
        elif stat == BackupBase.RESULT_PARTIAL_SUCCESS:
            msg = ' success , but has some job failed ! please check '
        else:
            msg = ' failed ! '
        log.info(backupconfig.operate + msg)
        ba.close()


# def backup(backupconfig:BackupConfig):
#     try:
#         with ParamikoConnection(backupconfig.host,backupconfig.ssh_user,backupconfig.ssh_password,backupconfig.ssh_port) as pk:
#             backup = None
#             if backupconfig.backup_mode == backupconfig._CONS_BACKUP_MODE_LOGIC:
#                 backup = MysqlLogicBackup(pk,backupconfig)
#             else:
#                 backup = Xtrabackup(pk,backupconfig)
#             cmd = '/usr/bin/xtrabackup --defaults-file=/database/my3578/my.cnf -usuper -p8845  --target-dir="/data/backup/my3578/2020-03-13" --slave-info --safe-slave-backup  --backup  --safe-slave-backup-timeout=3000   --socket=/database/my3578/var/3578.socket  2>&1 '
#             log.debug(cmd)
#             stat,_ = execute_cmd(cmd,sclient=pk)
#             log.info(stat)
#             if stat == SHELL_SUCCESS:
#                 cmd = b'echo "compress=True \r\ncompress-threads=4 " > /data/backup/my3578/2020-03-13/backup_params.record'
#                 stat,_ = execute_cmd(cmd,sclient=pk)
#                 log.info(str(stat))
#                 cmd = r'cp /database/my3578/my.cnf  /data/backup/my3578/2020-03-13/'
#                 stat,_ = execute_cmd(cmd,sclient=pk)
#                 log.info(str(stat))
#             return stat
#     except BaseException as e:
#         log.error(traceback.format_exc())
#
#
# def backup_new():
#     _config = threadSafeConfig.get()[config.MYSQL_BACKUP_CATEGORY]
#     ds = getDS()
#     conn = ds.get_conn()
#     log.debug('connect to {}'.format(_config.get('host')))
#     with ParamikoConnection(_config.get('host',None),_config.get('ssh_user',None),
#                             _config.get('ssh_password',None)) as pk:
#         log.debug('connect to {} success !'.format(_config.get('host')))
#         if _config.get('operate',None) == BackupConfig._CONS_OPERATE_BACKUP:
#             return inner_backup(pk,_config,conn)
#         else:
#             return inner_restore(pk,_config,conn)
#
#
# def inner_backup(pk,pconfig,conn):
#     cnfpath = getcnf(pk,conn)
#     outcnf = ConfigParser()
#     outcnf['backup_mode'] = pconfig['backup_mode']
#     pconfig['backup_dir'] = pconfig['backup_base_dir'] + '/' + formatDate()
#     log.info('check if backup dir exists')
#     if fileExists(pk,pconfig['backup_dir']):
#         log.info('backup dir {} exists,rename it !'.format(pconfig['backup_dir']))
#         rename(pk,pconfig['backup_dir'])
#     else:
#         mkdir(pk,pconfig['backup_dir'])
#     if pconfig['backup_mode'] == BackupConfig._CONS_BACKUP_MODE_FULL:
#         cmd = pconfig['backup_software'] + ' --defaults-file=' + cnfpath + ' -u' + pconfig['user']
#         outcnf['backup_software'] = pconfig['backup_software']
#         cmd += ' -p' + pconfig['password'] + ' --target-dir=' + pconfig['backup_dir']
#         cmd += ' --slave-info --safe-slave-backup  --backup  --safe-slave-backup-timeout=3000   --socket=' + DBUtils.getVariable(conn,'socket')
#         if pconfig['compress']:
#             cmd += ' --compress --compress-threads=4 '
#             outcnf['compress'] = 'True'
#             pass
#         cmd += ' 2>&1'
#         log.debug('ready to backup ! ')
#         stat,_ = execute_cmd(cmd,sclient=pk)
#         log.info('exit status = '+ str(stat))
#         tmpfile = path.join(path.split(__file__)[0],'backup_params.record')
#         if path.exists(tmpfile):
#             os.rename(tmpfile,tmpfile+time.strftime("%Y%m%d%H%M%S", time.localtime()))
#         with open(tmpfile,'w+') as f:
#             outcnf.write(tmpfile)
#         transferFileToRemote(tmpfile,pconfig['backup_dir']+'backup_params.record')
#         cmd = 'cp ' + cnfpath + ' ' + pconfig['backup_dir'] + '/'
#         execute_cmd(cmd,sclient=pk)
#         if stat == 0:
#             log.info('backup success!')
#         else:
#             log.error('backup failed!')
#         return stat
#
# def inner_restore(pk,pconfig):
#     pass
#
# def restore(backupconfig:BackupConfig):
#     try:
#         with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
#             cmd = '/usr/bin/xtrabackup --target-dir="/data/backup/my3578/2020-03-13"  --prepare '
#             # cmd = r"netstat -apn|grep -w LISTEN|sed 's= \{1,\}= =g'|cut -d ' ' -f 4|cut -d':' -f 4|grep -v -E '^$'"
#             stat,_ = execute_cmd(cmd,sclient=pk)
#             if stat == SHELL_SUCCESS:
#                 cmd = 'mkdir -p /database/my3579/data /database/my3579/var  /database/my3579/log'
#                 stat,_ = execute_cmd(cmd,sclient=pk)
#                 if stat == SHELL_SUCCESS:
#                     cmd = 'cat /data/backup/my3578/2020-03-13/my.cnf'
#                     stat,data = execute_cmd(cmd,sclient=pk,consumeoutput=False)
#                     mycnf = ConfigParser(allow_no_value=True)
#                     log.debug(to_text(data))
#                     mycnf.read_string(to_text(data))
#                     basepath = str()
#                     tmpfile = path.join(path.split(__file__)[0],'my.cnf')
#                     if path.exists(tmpfile):
#                         os.rename(tmpfile,tmpfile+time.strftime("%Y%m%d%H%M%S", time.localtime()))
#                     with open(tmpfile,'w+') as f:
#                         for sec in mycnf.sections():
#                             f.write('[' + sec + ']\r\n')
#                             for k,v in mycnf.items(sec,True):
#                                 if k == 'basedir':
#                                     basepath = v
#                                 v = str(v)
#                                 v = v.replace("/database/my3578","/database/my3579")
#                                 v = v.replace("3578","3579")
#                                 if not v or v == 'None' :
#                                     f.write(k + '\r\n')
#                                 else:
#                                     f.write(k + '=' + v + '\r\n')
#                     # cmd = 'cat>/database/my3579/my.cnf<<EOF\r\n'+configstr+'EOF'
#                     transferFileToRemote(tmpfile,'/database/my3579/my.cnf',pk)
#                     cmd = '/usr/bin/xtrabackup --defaults-file=/database/my3579/my.cnf --target-dir="/data/backup/my3578/2020-03-13" --copy-back '
#                     stat,_ = execute_cmd(cmd,sclient=pk)
#                     cmd = 'cat /dev/null > /database/my3579/log/log.err'
#                     execute_cmd(cmd,sclient=pk)
#                     start_shell = basepath + '/bin/mysqld_safe '+' --defaults-file=/database/my3579/my.cnf  & \r\n'
#                     execute_backupground(start_shell,pk)
#                     cmd = 'ps -ef|grep 3579|grep -v grep|grep mysqld '
#                     execute_cmd(cmd,sclient=pk)
#                     cmd = 'ps -ef|grep 3579|grep -v grep|grep mysqld |wc -l'
#                     stat,data = execute_cmd(cmd,sclient=pk,consumeoutput=False)
#                     log.debug(str(stat))
#                     if not (stat == 0 and int(data) > 0):
#                         stat = 1
#                         log.info(stat)
#                         log.error('restored database start failed !')
#                     else:
#                         log.info('restore success !')
#                     return stat
#     except BaseException as e:
#         log.error(traceback.format_exc())



