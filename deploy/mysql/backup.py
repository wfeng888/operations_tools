import configparser
import re
from configparser import ConfigParser
from os import path

import log
from deploy.mysql import *
from deploy.mysql import constant, DBUtils

from deploy.mysql.DBUtils import safe_close, getVariable
from deploy.mysql.DataSource import getDS
from deploy.mysql.constant import MYSQL57_CNF_VAR_PREFERENCE
from public_module import  to_text, ContextManager
from public_module.config import BackupConfig,MysqlBackupConfig
import public_module.config as config
from public_module.ssh_connect import ConnectionBase

from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import formatDate, none_null_stringNone, record_log, string_true_bool, path_join, \
    formatDateTime, whichPath


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
    cmd=['cmd',None]
    user = ['--user',None]
    password = ['--password',None]
    port = ['--port',None]
    host = ['--host',None]
    socket = ['--socket',None]
    tmp_dir:str

    def __init__(self,sshobject:ParamikoConnection,backupconfig):
        self._sshobject = sshobject
        self._config = backupconfig

    def updateConfig(self):
        self.user[1] = self._config.user
        self.password[1] = self._config.password
        self.port[1] = self._config.port

    def updateBackupConfig(self):
        pass

    def updateRestoreConfig(self):
        pass

    def prepareEnv(self):
        pass

    def prepareBackupEnv(self):
        pass

    def prepareRestoreEnv(self):
        pass

    def preInit(self):
        cmd = 'cd ~;pwd'
        _,tmp_dir = self._sshobject.execute_cmd(cmd,False)
        self.tmp_dir = path_join(to_text(tmp_dir),formatDateTime())
        self._sshobject.mkdir(self.tmp_dir)

    def backupInit(self):
        self._config.backup_dir = path_join(self._config.backup_base_dir,formatDate())


    def restoreInit(self):
        self._config.backup_dir = self._config.backup_base_dir

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
        try:
            if self._config.operate == BackupConfig._CONS_OPERATE_BACKUP:
                self.preInit()
                self.backupInit()
                self.updateConfig()
                self.updateBackupConfig()
                self.prepareEnv()
                self.prepareBackupEnv()
                self.beforeBackup()
                if self.do_backup() == ConnectionBase.SHELL_SUCCESS:
                    self.result_stat = self.RESULT_PARTIAL_SUCCESS
                    if self.afterBackup() == ConnectionBase.SHELL_SUCCESS:
                        self.result_stat = self.RESULT_SUCCESS
                else:
                    self.result_stat = self.RESULT_FAIL
            else:
                self.preInit()
                self.restoreInit()
                self.updateConfig()
                self.updateRestoreConfig()
                self.prepareEnv()
                self.prepareRestoreEnv()
                self.beforeRestore()
                if self.do_restore() == ConnectionBase.SHELL_SUCCESS:
                    self.result_stat = self.RESULT_PARTIAL_SUCCESS
                    if self.afterRestore() == ConnectionBase.SHELL_SUCCESS:
                        self.result_stat = self.RESULT_SUCCESS
                else:
                    self.result_stat = self.RESULT_FAIL
        except RestoreFailedException:
            self.result_stat = self.RESULT_FAIL
        except BackupFailedException:
            self.result_stat = self.RESULT_FAIL
        return self.result_stat

    def getLocalTmpDir(self):
        return path.split(__file__)[0]


class MysqlBackup(BackupBase):
    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlBackup, self).__init__(sshobject,backupconfig)
        if not self._config.operate == MysqlBackupConfig._CONS_OPERATE_RESTORE:
            if not conn:
                self._ds = ds if ds else getDS(*(self._config.user,self._config.password,self._config.host,self._config.port,self._config.database))
                self._conn = self._ds.get_conn()
            else:
                self._conn = conn
        else:
            self._ds = None
            self._conn = None
        self.backup_param = ''
        self.backup_param_filename = 'backup.param'
        self.backup_log_filename = 'backup.log'
        self.restore_log_name='restore.log'
        self.full_backup_param_config = ConfigParser(allow_no_value=True)
        self.full_backup_decompress=False
        self.incremental_backup_param_config = None
        self.incremental_backup_decompress=False
        self.backupsoftwarepath = ''
        self.backupsoftware = ['backupsoftware',None]
        self.mysql_version = ['mysql_version',None]
        self.mysql_base = ['--basedir',None]
        self.login_path = ['--login-path',None]
        self.target_dir = ['--target-dir',None]
        self.full_dir=['--target-dir',None]
        self.datadir = ['--datadir',None]
        self.log_err_dir = None
        self.databases = ['--databases',None]
        self.backup_success_flag = 'completed OK'
        self.socket = ['--socket',None]

    def checkBackupOk(self,*args):
        pass

    def getSocketFromCommand(self,cmd):
        r = re.search('(socket)=([\S]+)',cmd)
        if r:
            return r.group(2)

    def formatOption(self,opt:str):
        results = []
        if opt:
            opts = opt.strip().split()
            for i in opts:
                values = i.partition('=')
                results.append(values)
        return results

    def afterBackup(self):
        paramf_stat = 1
        param = ConfigParser(allow_no_value=True)
        param.set(None,self.cmd[0],self.cmd[1])
        opts = self.formatOption(self.backup_param)
        if opts:
            for i in opts:
                param.set(None,i[0],i[2])
        tmppath = path.join(self.getLocalTmpDir(),self.backup_param_filename)
        with open(tmppath,'w',encoding='utf-8') as wf:
            param.write(wf)
            wf.flush()
        if self._sshobject.transferFileToRemote(tmppath,path_join(self.target_dir[1],self.backup_param_filename)):
            paramf_stat = 0
        return paramf_stat

    def _checkBackupOk(self,logdir):
        logpath = path_join(logdir,self.backup_log_filename)
        if self._sshobject.fileExists(logpath):
            cmd = 'tail -1 %s '%logpath
            stat,data = self._sshobject.execute_cmd(cmd,False)
            if data:
                data = to_text(data)
                if data.find(self.backup_success_flag) > -1:
                    return True
        return False

    def close(self):
        safe_close(self._conn)
        super(MysqlBackup, self).close()

    def getBackupParam(self,path,parser):
        cmd = 'cat %s'%path
        stat,paramContent = self._sshobject.execute_cmd(cmd,False)
        checkStatAndRaise(stat,ReadBackupParamException,*(path,))
        parser.read_string(to_text(paramContent))

    def updateRestoreConfig(self):
        super(MysqlBackup, self).updateRestoreConfig()
        if not self.checkBackupOk():
            raise CheckMysqlBackupFileException('check backup file failed , is the backup file exists ? the other reason may be the last backup had not completed success!')
        cmd = 'cp -a %s  %s'%(self.full_dir[1],self.tmp_dir)
        stat,_ = self._sshobject.execute_cmd(cmd)
        if stat != ConnectionBase.SHELL_SUCCESS:
            raise FileCopyException('copy backup file from %s to temp directory %s failed!' %(self.full_dir[1],self.tmp_dir))
        self.full_dir[1] = path_join(self.tmp_dir,self.full_dir[1].rpartition('/')[2])


    def updateBackupConfig(self):
        super().updateBackupConfig()
        self.mysql_version[1] = getVariable('innodb_version',self._conn)
        self.mysql_base[1] = getVariable(self.mysql_base[0].replace('-',''),self._conn)
        self.datadir[1] = getVariable(self.datadir[0].replace('-',''),self._conn)
        self.target_dir[1] = self._config.backup_dir

    @record_log
    def getMysqldCommand(self):
        cmd = 'sudo netstat -apn|grep -w ' + str(self._config.port) + ' |grep -w LISTEN|sed \'s= \{1,\}= =g\'|cut -d \' \' -f 7|cut -d \'/\' -f 1|xargs ps --no-headers  -f -p |sed \'s= \{1,\}= =g\'|cut -d \' \' -f8-'
        stat,data = self._sshobject.execute_cmd(cmd,False)
        if stat == ConnectionBase.SHELL_SUCCESS:
            return data
        return None

    def getMysqldVersion(self):
        data = self.getMysqldCommand()
        mysqldpath = to_text(data).replace('--','').partition(' ')[0]
        return self.findMysqldVersion(mysqldpath)

    def findMysqldVersion(self,mysqldpath):
        cmd = '%s --version'%mysqldpath
        data = to_text(self._sshobject.execute_cmd(cmd,False))
        # eg: mysqld  Ver 8.0.17
        r = re.search('mysqld  Ver ([1-9]+\.[0-9]+\.[0-9]+)',data)
        if r:
            return r.group(1)
        return None

    def getRestoredMysqlBase(self,mysqldpath):
        if not isinstance(mysqldpath,(list,tuple)):
            mysqldpath = (mysqldpath,)
        for mpath in mysqldpath:
            if self._sshobject.isFile(mpath):
                mpath = mpath.rpartition('/')[0]
            cmd =  'cd %s;find . -name mysqld '%mpath
            stat,mysqlds = self._sshobject.execute_cmd(cmd,False)
            mysqlds = to_text(mysqlds)
            for p in mysqlds.splitlines():
                sv = self.findMysqldVersion(path_join(mpath,p))
                if sv == self.mysql_version[1]:
                    return path_join(mpath,p).rpartition('/')[0].rpartition('/')[0]
        raise MysqlVersionNotMatchException('Can not find a mysql which version match with  backup files')


    @record_log
    def prepareBackupEnv(self):
        super(MysqlBackup, self).prepareBackupEnv()
        if self._sshobject.mkdir(self.target_dir[1]):
            return ConnectionBase.SHELL_SUCCESS
        raise EnvironmentCheckException('')

    def beforeBackup(self):
        self.backup_param += ' ' + self.compactItem(True,self.backupsoftware,self.mysql_version,self.mysql_base)

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
                        s = item[1]
                        if not isinstance(s,(tuple,list)):
                            s = (s,)
                        cmd += '='
                        for k in s:
                            cmd += str(k) +','
                        cmd = cmd[:-1]
            else:
                cmd += ' ' + str(item)
        return cmd

    def getOldBackupConfig(self,option,section='mysqld'):
        if getattr(self,'mysql_cnf_config',None):
            v = getattr(self,'mysql_cnf_config').get(section,option,fallback=None)
            if not v:
                if self.incremental_backup_param_config:
                    v = self.incremental_backup_param_config.get(section,option,fallback=None)
                    if not v:
                        v = self.full_backup_param_config.get(section,option,fallback=None)
        return v

class MysqlHotBackup(MysqlBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlHotBackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.defaults_file = ['--defaults-file',None]
        self.defaults_extra_file = ['--defaults-extra-file',None]
        self.defaults_group_suffix = ['--defaults-group-suffix',None]

        self.restore_target_dir=None
        self.restored_mysql_cnfname='my.cnf'
        self.backup_mysql_cnfname='my.cnf.bak'
        self.mysql_cnf_config = ConfigParser(allow_no_value=True)
        self.incremental_basedir = ['--incremental-basedir',None,None]
        self.incremental_dir = ['--incremental-dir',None,None]
        self.decompress = ['--decompress',None,None]
        self.parallel = ['--parallel',4]
        self.log_bin = ['--log-bin',None]
        self.compress = ['--compress','quicklz',None]

    @record_log
    def makeCnf(self):
        cnf = ConfigParser(allow_no_value=True)
        for sec in MYSQL57_CNF_VAR_PREFERENCE.keys():
            cnf.add_section(sec)
            for option in MYSQL57_CNF_VAR_PREFERENCE[sec]:
                if isinstance(option,(list,tuple)) and option[1]:
                    cnf.set(sec,option[0],str(getVariable(option[1].replace('-','_'),self._conn)))
                else:
                    cnf.set(sec,option,str(getVariable(option.replace('-','_'),self._conn)))
        tmplocalcnfpath = path.join(self.getLocalTmpDir(),self.backup_mysql_cnfname)
        with open(tmplocalcnfpath,'w',encoding='utf-8') as wf:
            cnf.write(wf)
        tmpcnfpath = path_join(self.tmp_dir,self.backup_mysql_cnfname)
        self._sshobject.transferFileToRemote(tmplocalcnfpath,tmpcnfpath)
        return tmpcnfpath

    @record_log
    def setBackupCnfFile(self,cnffile=None,force=False):
        if not none_null_stringNone(self.defaults_file[1]) and not force:
            return
        data = to_text(self.getMysqldCommand())
        if data:
            self.setSocket(self.getSocketFromCommand(data))
            r = re.search('(defaults-file)=([\S]+)',data)
            if r:
                self.defaults_file[1] = r.group(2)
            else:
                self.defaults_file[1] = self.makeCnf()
        else:
            raise MysqldNotRunningException('mysqld process not running , it shoud be')

    def setRestoreCnfFile(self):
        cnf = path_join(self.full_dir[1],self.backup_mysql_cnfname)
        if self._sshobject.fileExists(cnf):
            self.defaults_file[1] = cnf
        else:
            raise MysqlCnfFileNotExistsException('can not find mysql config file in backup directory : {}'.format(self.full_dir[1]))
        cmd = 'cat %s'%cnf
        stat,cnfContent = self._sshobject.execute_cmd(cmd,False)
        checkStatAndRaise(stat,ReadBackupConfigFileException,cnf)
        self.mysql_cnf_config.read_string(to_text(cnfContent))
        new_softwarebase = self.mysql_base[1]
        old_softwarebase = self.getOldBackupConfig(self.mysql_base[0].replace('-',''))
        new_data_base = self.datadir[1].rpartition('/')[0]
        old_data_base = self.getOldBackupConfig(self.datadir[0].replace('-','')).rpartition('/')[0]
        def replace_cnfconfig(type,sec,option):
            if type == constant.SOFTWARE_PATH:
                o = old_softwarebase
                n = new_softwarebase
            else:
                o = old_data_base
                n = new_data_base
            ov = self.mysql_cnf_config.get(sec,option,fallback=None)
            if ov:
                self.mysql_cnf_config.set(sec,option,ov.replace(o,n))
        for sec in MYSQL57_CNF_VAR_PREFERENCE.keys():
            for item in MYSQL57_CNF_VAR_PREFERENCE[sec]:
                if isinstance(item,(list,tuple)):
                    if item[2]:
                        replace_cnfconfig(item[2],sec,item[0])
            self.mysql_cnf_config.set(sec,'port',str(self._config.port))
        tmplogpath = self.mysql_cnf_config.get('mysqld','log-error',fallback=None)
        if not tmplogpath:
            tmplogpath = path_join(self.log_err_dir,'log.err')
            self.mysql_cnf_config.set('mysqld','log-error',tmplogpath)
        if not self._sshobject.fileExists(tmplogpath):
            cmd = 'touch %s'%tmplogpath
            self._sshobject.execute_cmd(cmd)
        tmplocalpath = path.join(self.getLocalTmpDir(),self.backup_mysql_cnfname)
        with open(tmplocalpath,'w') as wf:
            self.mysql_cnf_config.write(wf)
        self._sshobject.transferFileToRemote(tmplocalpath,self.defaults_file[1])

    @record_log
    def setSocket(self,socketfile=None,force=False):
        if not none_null_stringNone(self.socket[1]) and not force:
            return
        self.socket[1] = socketfile if socketfile else getVariable('socket',self._conn)

    def getBackupCmd(self,cmd=None):
        pass

    @record_log
    def do_backup(self):
        log.debug('doing backup')
        self.cmd[1] = self.getBackupCmd()
        tmpbackuplog = path.join(self.getLocalTmpDir(),self.backup_log_filename)
        stat,data =self._sshobject.execute_cmd(self.cmd[1],logfile=tmpbackuplog)
        self._sshobject.transferFileToRemote(tmpbackuplog,path_join(self.target_dir[1],self.backup_log_filename))
        if stat == ConnectionBase.SHELL_SUCCESS:
            self.result_stat = self.RESULT_PARTIAL_SUCCESS
        return stat

    @record_log
    def afterBackup(self):
        paramf_stat = super().afterBackup()
        cmd = 'cp %s  %s '%(self.defaults_file[1],path_join(self.target_dir[1],self.backup_mysql_cnfname))
        cnf_stat,_ = self._sshobject.execute_cmd(cmd)
        return paramf_stat|cnf_stat

    @record_log
    def setBackupSoftWarePath(self):
        data = whichPath(self.backupsoftware[1],self._sshobject)
        if data:
            self.backupsoftwarepath = data

    def restoreInit(self):
        super(MysqlHotBackup, self).restoreInit()
        if self._config.backup_mode == MysqlBackupConfig._CONS_BACKUP_MODE_INCREMENT:
            self.incremental_dir[1] = self._config.backup_dir
            self.incremental_dir[2] = True
            self.full_dir[1] = self._config.incremental_basedir
        else:
            self.full_dir[1] = self._config.backup_dir

    def updateRestoreConfig(self):
        super(MysqlHotBackup, self).updateRestoreConfig()
        self.restore_target_dir = self._config.restore_target_dir
        if not self._sshobject.fileExists(self.restore_target_dir):
            self._sshobject.mkdir(self.restore_target_dir)
        if self._sshobject.listdir(self.restore_target_dir):
            raise EnvironmentCheckException('Restore target directory %s must be empty' %self.restore_target_dir)

        paramf = path_join(self.full_dir[1],self.backup_param_filename)
        self.getBackupParam(paramf,self.full_backup_param_config)
        self.mysql_version[1] = self.full_backup_param_config.get(configparser.DEFAULTSECT,self.mysql_version[0],fallback=None)
        tmpmysqlpath = self.full_backup_param_config.get(configparser.DEFAULTSECT,self.mysql_base[0].replace('-',''),fallback=None)
        self.mysql_base[1] = self.getRestoredMysqlBase((self._config.mysql_software_path,tmpmysqlpath))

        if self.full_backup_param_config.get(configparser.DEFAULTSECT,self.compress[0].replace('-',''),fallback=None):
            self.full_backup_decompress = True
        if self.incremental_dir[1]:
            cmd = 'cp -a %s %s'%(self.incremental_dir[1],self.tmp_dir)
            self._sshobject.execute_cmd(cmd)
            self.incremental_dir[1] = path_join(self.tmp_dir,self.incremental_dir[1].rpartition('/')[2])
            paramf = path_join(self.incremental_dir[1],self.backup_param_filename)
            if self.incremental_backup_param_config == None:
                self.incremental_backup_param_config = ConfigParser(allow_no_value=True)
            self.getBackupParam(paramf,self.incremental_backup_param_config)
            if self.incremental_backup_param_config.get(configparser.DEFAULTSECT,self.compress[0].replace('-',''),fallback=None):
                self.incremental_backup_decompress = True

        self._sshobject.execute_cmd('cd {};mkdir -p data var log'.format(self.restore_target_dir))
        self.datadir[1] = path_join(self.restore_target_dir,'data')
        self.log_err_dir = path_join(self.restore_target_dir,'log')
        self.setRestoreCnfFile()


    def updateBackupConfig(self):
        super().updateBackupConfig()
        if self._config.incremental_basedir:
            self.incremental_basedir[1] = self._config.incremental_basedir
            self.incremental_basedir[2] = True
        self.setBackupCnfFile()
        self.setSocket()

    def updateConfig(self):
        super(MysqlHotBackup, self).updateConfig()
        self.setBackupSoftWarePath()

    def afterRestore(self):
        super(MysqlHotBackup, self).afterRestore()
        cmd = self.compactItem(False,path_join(self.mysql_base[1],'bin/mysqld_safe'),self.defaults_file,'&')
        self._sshobject.execute_backupground(cmd)
        if self.getMysqldCommand():
            return ConnectionBase.SHELL_SUCCESS

    def checkBackupOk(self,*args):
        if none_null_stringNone(self.full_dir[1]) or \
                self._config.backup_mode == MysqlBackupConfig._CONS_BACKUP_MODE_INCREMENT and none_null_stringNone(self.incremental_dir[1]):
            return False
        for item in (self.full_dir[1],self.incremental_dir[1]):
            if item:
                if not self._checkBackupOk(item):
                    return False
        return True

class Xtrabackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(Xtrabackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.backup = '--backup'
        self.prepare = '--prepare'
        self.apply_log_only = '--apply-log-only'
        self.stats = '--stats'
        self.export = '--export'
        self.print_param = '--print-param'
        self.use_memory = ['--use-memory',None]
        self.throttle = ['--throttle',None]
        self.log = ['--log',None]
        self.log_copy_interval = ['--log-copy-interval',None]
        self.extra_lsndir = ['--extra-lsndir',None]
        self.incremental_lsn = ['--incremental-lsn',None]
        self.to_archived_lsn = ['--to-archived-lsn',None]
        self.tables = ['--tables',None]
        self._tables_file = ['--tables-file',None]
        self.databases = ['--databases',None]
        self.databases_file = ['--databases-file',None]
        self.tables_exclude = ['--tables-exclude',None]
        self.databases_exclude = ['--databases-exclude',None]
        self.stream = ['--stream',None]
        self.compress_threads = ['--compress-threads',4]
        self.compress_chunk_size = ['--compress-chunk-size',None]
        self.encrypt = ['--encrypt',None]
        self.copy_back = '--copy-back'
        self.move_back = '--move-back'
        self.slave_info = '--slave-info'
        self.safe_slave_backup = '--safe-slave-backup'
        self.safe_slave_backup_timeout = ['--safe-slave-backup-timeout',3000]
        self.rsync = '--rsync'
        self.backupsoftware[1] = 'xtrabackup'


    def prepareRestoreEnv(self):
        super(Xtrabackup, self).prepareRestoreEnv()
        if self.incremental_basedir[1]:
            cmd = 'cp -a %s  %s'%(self.incremental_basedir[1],self.tmp_dir)
            self._sshobject.execute_cmd(cmd)
            self.incremental_basedir[1] = path_join(self.tmp_dir,self.incremental_basedir[1].rpartition('/'))

    @record_log
    def updateBackupConfig(self):
        super().updateBackupConfig()
        self.compress[2] = self._config.compress
        if string_true_bool(self.compress[2]):
            self.compress_threads[1] = 4

    @record_log
    def getBackupCmd(self):
        cmd = self.compactItem(False,self.backupsoftwarepath,self.defaults_file,self.user,self.password,self.target_dir,self.slave_info,self.safe_slave_backup,self.safe_slave_backup_timeout,self.socket,self.compress,self.compress_threads,self.incremental_basedir,self.backup,'2>&1')
        self.backup_param += ' ' + self.compactItem(True,self.compress,self.incremental_basedir)
        return cmd

    def beforeRestore(self):
        super(Xtrabackup, self).beforeRestore()
        stat = 0
        for k,v in ((self.incremental_backup_decompress,self.incremental_dir[1]),(self.full_backup_decompress,self.full_dir[1])):
            if k:
                self.target_dir[1] = v
                self.decompress[2] = k
                cmd = self.compactItem(False,self.backupsoftwarepath,self.decompress,self.target_dir,self.parallel,'2>&1')
                stat,_ = self._sshobject.execute_cmd(cmd)
                checkStatAndRaise(stat,RestoreFailedException,' when decompress backup files .')
        self.target_dir[1] = self.full_dir[1]
        cmd = self.compactItem(False,self.backupsoftwarepath,self.target_dir,self.prepare)
        if self.incremental_dir[1]:
            cmd += self.compactItem(False,self.apply_log_only)
        cmd += self.compactItem(False,'2>&1')
        stat,_ = self._sshobject.execute_cmd(cmd)
        checkStatAndRaise(stat,RestoreFailedException,' when prepare full backup files .')
        if self.incremental_dir[1]:
            cmd = self.compactItem(False,self.backupsoftwarepath,self.target_dir,self.incremental_dir,self.prepare,'2>&1')
            stat,_ = self._sshobject.execute_cmd(cmd)
            checkStatAndRaise(stat,RestoreFailedException,' when decompress backup files .')
        return stat

    def do_restore(self):
        super(Xtrabackup, self).do_restore()
        cmd = 'cp %s  %s' % (self.defaults_file[1],path_join(self.restore_target_dir,self.restored_mysql_cnfname))
        self._sshobject.execute_cmd(cmd)
        self.defaults_file[1] = path_join(self.restore_target_dir,self.restored_mysql_cnfname)
        self.target_dir[1] = self.full_dir[1]
        cmd = self.compactItem(False,self.backupsoftwarepath,self.defaults_file,self.target_dir,self.copy_back,'2>&1')
        stat,_ = self._sshobject.execute_cmd(cmd)
        checkStatAndRaise(stat,RestoreFailedException,' when copy backup files to restore target directory.')
        return stat

class MysqlEnterpriseBackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlEnterpriseBackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.backupsoftware[1] = 'mysqlbackup'


class MysqlLogicBackup(MysqlBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlLogicBackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.restore_log_file=None
        self.sql_file_name='backup.sql'
        self.sql_file = None
        self.backup_log_file = None

    def restoreInit(self):
        super(MysqlLogicBackup, self).restoreInit()
        self.full_dir[1] = self._config.backup_dir

    def updateBackupConfig(self):
        super(MysqlLogicBackup, self).updateBackupConfig()
        self.backup_log_file = path_join(self.target_dir[1],self.backup_log_filename)
        self.sql_file = path_join(self.target_dir[1],self.sql_file_name)
        self.databases[1] = self._config.databases

    def updateRestoreConfig(self):
        super(MysqlLogicBackup, self).updateRestoreConfig()
        self.restore_log_file = path_join(self.full_dir[1],self.restore_log_name)
        self.sql_file = path_join(self.full_dir[1],self.sql_file_name)



    def updateConfig(self):
        super(MysqlLogicBackup, self).updateConfig()
        self.mysql_base[1] = self.getRestoredMysqlBase()
        self.backupsoftwarepath = self.mysql_base[1]+'/bin/' + self.backupsoftware[1]
        self.socket[1] =  getVariable('socket',self._conn)

    def getRestoredMysqlBase(self):
        data = getVariable('basedir',self._conn)
        if data and self._sshobject.fileExists(data):
            return data
        data = self.getMysqldCommand()
        if data:
            return to_text(data).split()[0].rpartition('/')[0].rpartition('/')[0]
        raise MysqldNotRunningException('mysql not running')


class MysqlDump(MysqlLogicBackup):
    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlDump, self).__init__(sshobject,backupconfig,ds,conn)
        self.add_drop_database = ['--add-drop-database',None]
        self.add_drop_table = ['--add-drop-table',None]
        self.add_drop_trigger=['--add-drop-trigger',None]
        self.allow_keywords=['--allow-keywords',None]
        self.compress=['--compress',None]
        self.extended_insert=['--extended-insert',None]
        self.skip_lock_tables=['--skip-lock-tables',None]
        self.protocol=['--protocol',None,None]
        self.routines=['--routines',None]
        self.triggers=['--triggers',None]
        self.events=['--events',None]
        self.single_transaction=['--single-transaction',None]
        self.backupsoftware[1] = 'mysqldump'

    def updateBackupConfig(self):
        super(MysqlDump, self).updateBackupConfig()
        if not self.databases[1]:
           self.databases[1] = [k[0] for k in DBUtils.query(self._conn,'show databases') if k[0] not in ('mysql','sys','information_schema','performance_schema')]



    def do_backup(self):
        self.cmd[1] = self.compactItem(False,self.backupsoftwarepath,self.add_drop_database,self.add_drop_table,self.add_drop_trigger,self.allow_keywords,\
                               self.extended_insert,self.skip_lock_tables,self.protocol,self.routines,self.triggers,self.events,self.single_transaction,\
                                self.user,self.socket,self.password)
        self.cmd[1] += ' ' + self.databases[0] + ' '
        for i in self.databases[1]:
            self.cmd[1] += ' ' + i
        self.cmd[1] +=  self.compactItem(False,'>',self.sql_file,'2>',self.backup_log_file)

        self.backup_param = self.compactItem(True,self.add_drop_database,self.add_drop_table,self.add_drop_trigger,self.allow_keywords, \
                                             self.extended_insert,self.skip_lock_tables,self.protocol,self.routines,self.triggers,self.events,self.single_transaction, \
                                             self.databases)
        self._sshobject.execute_backupground(self.cmd[1],logfile=self.backup_log_file,wait=True)
        cmd = 'echo "%s" >> %s'%(self.backup_success_flag,self.backup_log_file)
        self._sshobject.execute_cmd(cmd)
        return 0

class MysqlMysqlClient(MysqlLogicBackup):
    PROTOCOL_TCP='tcp'
    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlMysqlClient, self).__init__(sshobject,backupconfig,ds,conn)
        self.force = '-f'
        self.protocol=['--protocol','tcp',False]
        self.backupsoftware[1] = 'mysql'

    def checkBackupOk(self):
        return self._checkBackupOk(self.full_dir[1])

    def do_restore(self):
        super(MysqlMysqlClient, self).do_restore()
        self.cmd[1] = self.compactItem(False,self.backupsoftwarepath,self.force,self.user,self.socket,self.password,self.sql_file,'>/dev/null','2>',self.restore_log_file)
        self._sshobject.execute_backupground(self.cmd[1],logfile=self.restore_log_file,wait=True)
        return 0

    def versionGt(self,v1,v2):
        v1 = v1.split('.')
        v2 = v2.split('.')
        for i in range(len(v1)):
            if v1[i]>v2[i]:
                return True
        return False

def backup_restore(backupconfig: config.MysqlBackupConfig):
    with ParamikoConnection(backupconfig.host,backupconfig.ssh_user,backupconfig.ssh_password,backupconfig.ssh_port) as pk:
        ba = None
        if backupconfig.backup_mode == config.MysqlBackupConfig._CONS_BACKUP_MODE_LOGIC:
            if backupconfig.operate == config.MysqlBackupConfig._CONS_OPERATE_BACKUP:
                ba = MysqlDump(pk,backupconfig)
            else:
                ba = MysqlMysqlClient(pk,backupconfig)
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
