import configparser
import re
from configparser import ConfigParser
from os import path

import log
from deploy.mysql import MysqldNotRunningException, MysqlCnfFileNotExistsException, MysqlVersionNotMatchException, \
    constant

from deploy.mysql.DBUtils import safe_close, getVariable
from deploy.mysql.DataSource import getDS
from deploy.mysql.constant import MYSQL57_CNF_VAR_PREFERENCE
from public_module import  to_text, ContextManager
from public_module.config import BackupConfig,MysqlBackupConfig
import public_module.config as config
from public_module.ssh_connect import ConnectionBase

from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import formatDate, none_null_stringNone, record_log, string_true_bool, path_join, \
    formatDateTime


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
    tmp_dir:str

    def __init__(self,sshobject:ParamikoConnection,backupconfig):
        self._sshobject = sshobject
        self._config = backupconfig

    def updateBackupConfig(self):
        pass

    def updateRestoreConfig(self):
        pass

    def updateConfig(self):
        self.user[1] = self._config.user
        self.password[1] = self._config.password
        self.port[1] = self._config.port



    def prepareBackupEnv(self):
        pass

    def prepareRestoreEnv(self):
        pass

    def prepareEnv(self):
        pass


    def preBackupInit(self):
        self._config.backup_dir = path_join(self._config.backup_base_dir,formatDate())

    def preRestoreInit(self):
        self._config.backup_dir = path_join(self._config.backup_base_dir)

    def preInit(self):
        cmd = 'cd ~;pwd'
        tmp_dir = self._sshobject.execute_cmd(cmd,False)
        tmp_dir = path_join(tmp_dir,formatDateTime())
        self._sshobject.mkdir(tmp_dir)
        self.tmp_dir = tmp_dir

    def backupInit(self):
        pass

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
            self.preRestoreInit()
            self.updateConfig()
            self.updateRestoreConfig()
            self.prepareEnv()
            self.prepareBackupEnv()
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

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(Xtrabackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.init()

    def init(self):
        self.backup_param:str
        self.backup_param_filename = 'backup.param'
        self.full_backup_param_config = ConfigParser(allow_no_value=True)
        self.full_backup_decompress=False
        self.incremental_backup_param_config = None
        self.incremental_backup_decompress=False
        self.backupsoftwarepath:str
        self.backupsoftware = ['backupsoftware',None]
        self.mysql_version = ['mysql_version',None]
        self.mysql_base = ['--basedir',None]
        self.login_path = ['--login-path',None]
        self.target_dir = ['--target-dir',None]
        self.full_dir=['--target-dir',None]
        self.mysql_software_path:str=None
        self.mysqld_safe_software_path:str = None
        self.datadir = ['--datadir',None]

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

    def preRestoreInit(self):
        self.mysql_software_path = self._config.mysql_software_path

    def updateRestoreConfig(self):
        super(MysqlBackup, self).updateRestoreConfig()
        cmd = 'cp -a {} {}'%(self.full_dir[1],self.tmp_dir)
        self._sshobject.execute_cmd(cmd)
        self.full_dir[1] = path_join(self.tmp_dir,self.full_dir[1].rpartition('/')[2])
        paramf = path_join(self.full_dir[1],self.backup_param_filename)
        self.getBackupParam(paramf,self.full_backup_param_config)
        self.mysql_version[1] = self.full_backup_param_config.get(configparser.DEFAULTSECT,self.mysql_version[0],fallback=None)
        tmpmysqlpath = self.full_backup_param_config.get(configparser.DEFAULTSECT,self.mysql_base[0].replace('-',''),fallback=None)
        self.mysql_base[1] = self.getRestoredMysqlBase((self.mysql_software_path,tmpmysqlpath))
        self.mysql_software_path = path_join(self.mysql_base[1],'bin/mysql')
        self.mysqld_safe_software_path = path_join(self.mysql_base[1],'bin/mysqld_safe')

    def updateBackupConfig(self):
        self.mysql_version[1] = self.getMysqldVersion()
        self.mysql_base[1] = getVariable(self.mysql_base[0].replace('-',''),self._conn)
        self.datadir = getVariable(self.datadir[0].replace('-',''),self._conn)

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

    def getRestoredMysqlBase(self,mysqldpath:str):
        if not isinstance(mysqldpath,(list,tuple)):
            mysqldpath = (mysqldpath,)
        for mpath in mysqldpath:
            if self._sshobject.isFile(mpath):
                mpath = mpath.rpartition('/')[0]
            cmd =  'find . -name mysqld '
            mysqlds = to_text(self._sshobject.execute_cmd(cmd,False))
            for p in mysqlds.splitlines():
                sv = self.findMysqldVersion(path_join(mpath,p))
                if sv == self.mysql_version[1]:
                    return path_join(mpath,p).rpartition('/')[0].rpartition('/')[0]
        raise MysqlVersionNotMatchException('Can not find a mysql which version match with  backup files')


    @record_log
    def prepareBackupEnv(self):
        super(MysqlBackup, self).prepareBackupEnv()
        if self._sshobject.fileExists(self.target_dir[1]):
            self._sshobject.rename(self.target_dir[1])
        if self._sshobject.mkdir(self.target_dir[1]):
            return ConnectionBase.SHELL_SUCCESS
        return ConnectionBase.SHELL_FAILED

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
                        cmd += '=' + str(item[1])
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
        super(Xtrabackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.init()

    def init(self):
        self.defaults_file = ['--defaults-file',None]
        self.defaults_extra_file = ['--defaults-extra-file',None]
        self.defaults_group_suffix = ['--defaults-group-suffix',None]
        self.socket = ['--socket',None]
        self.restore_target_dir:str
        self.restored_mysql_cnfname='backup_my.cnf'
        self.mysql_cnf_config = ConfigParser(allow_no_value=True)
        self.incremental_basedir = ['--incremental-basedir',None,None]
        self.incremental_dir = ['--incremental-dir',None,None]
        self.decompress = ['--decompress',None,None]
        self.parallel = ['--parallel',4,True]
        self.log_bin = ['--log-bin',None]
        self.compress = ['--compress','quicklz',None]
        self.target_dir = ['--target-dir',None]

    def preBackupInit(self):
        pass

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
        cw = ConfigWriter()
        cnf.write(cw)
        tmpcnfpath = path_join(self.tmp_dir,self.restored_mysql_cnfname)
        self._sshobject.execute_cmd('echo "' + cw.get() + '" > ' + tmpcnfpath)
        return tmpcnfpath

    def preInit(self):
        super(MysqlHotBackup, self).preInit()
        self.restore_target_dir = self._config.restore_target_dir

    @record_log
    def setBackupCnfFile(self,cnffile=None,force=False):
        if not none_null_stringNone(self.defaults_file[1]) and not force:
            return
            data = to_text(self.getMysqldCommand())
            if data:
                r = re.search('(socket)=([\S]+)',data)
                if r:
                    self.setSocket(r.group(2))
                r = re.search('(defaults-file)=([\S]+)',data)
                if r:
                    self.defaults_file[1] = r.group(2)
                else:
                    self.defaults_file[1] = self.makeCnf()
            else:
                raise MysqldNotRunningException('mysqld process not running , it shoud be')

    def setRestoreCnfFile(self):
        cnf = path_join(self.full_dir[1],self.restored_mysql_cnfname)
        if self._sshobject.fileExists(cnf):
            self.defaults_file[1] = cnf
        else:
            raise MysqlCnfFileNotExistsException('can not find mysql config file in backup directory : {}'.format(self.full_dir[1]))
        cmd = 'cat %s'%cnf
        cnfContent = self._sshobject.execute_cmd(cmd,False)
        self.mysql_cnf_config.read_string(to_text(cnfContent))
        new_softwarebase = self.mysql_base[1]
        old_softwarebase = self.getOldBackupConfig(self.mysql_base[0].replace('-',''))
        new_data_base = self.datadir[1].rpartition('/')
        old_data_base = self.getOldBackupConfig(self.datadir[0].replace('-',''))
        def replace_cnfconfig(type,sec,option):
            if type == constant.SOFTWARE_PATH:
                o = old_softwarebase
                n = new_softwarebase
            else:
                o = old_data_base
                n = new_data_base
            ov = self.mysql_cnf_config.get(sec,option,None)
            if ov:
                self.mysql_cnf_config.set(sec,option,ov.replace(o,n))
        for sec in MYSQL57_CNF_VAR_PREFERENCE.keys():
            for item in MYSQL57_CNF_VAR_PREFERENCE[sec]:
                if isinstance(item,(list,tuple)):
                    if item[2]:
                        replace_cnfconfig(item[2],sec,item[0])
        tmplocalpath = path.join(self.getLocalTmpDir(),self.restored_mysql_cnfname)
        with open(tmplocalpath,'w') as wf:
            self.mysql_cnf_config.write(wf)
        self._sshobject.transferFileToRemote(tmplocalpath,self.defaults_file[1])


    def getBackupParam(self,path,parser):
        cmd = 'cat %s'%path
        paramContent = self._sshobject.execute_cmd(cmd)
        parser.read_string(to_text(paramContent))


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
        super(MysqlHotBackup, self).afterBackup()
        param = ConfigParser(allow_no_value=True)
        param.set(None,'cmd',self.cmd)
        opts = self.formatOption(self.backup_param)
        if opts:
            for i in opts:
                param.set(None,i[0],i[2])
        tmppath = path.join(self.getLocalTmpDir(),self.backup_param_filename)
        with open(tmppath,'w') as wf:
            param.write(wf)
            wf.flush()
        if self._sshobject.transferFileToRemote(tmppath,path_join(self.target_dir[1],self.backup_param_filename)):
            return ConnectionBase.SHELL_SUCCESS
        return ConnectionBase.SHELL_FAILED

    @record_log
    def setBackupSoftWarePath(self):
        cmd = 'which ' + self.backupsoftware[1]
        nostr = 'no ' + self.backupsoftware[1] + ' in'
        stat,data = self._sshobject.execute_cmd(cmd,False)
        if stat == ConnectionBase.SHELL_SUCCESS:
            data = to_text(data)
            for s in data.splitlines():
                i = s.find(nostr)
                if i >= 0 :
                    return None
            self.backupsoftwarepath = data.replace('\r','').replace('\n','')

    def preRestoreInit(self):
        if self._config.backup_mode == MysqlBackupConfig._CONS_BACKUP_MODE_INCREMENT:
            self.incremental_dir[1] = self._config.backup_dir
            self.full_dir[1] = self._config.incremental_basedir
        else:
            self.full_dir[1] = self._config.backup_dir

    def updateRestoreConfig(self):
        super(MysqlHotBackup, self).updateRestoreConfig()
        if self.full_backup_param_config.get(configparser.DEFAULTSECT,self.compress[0].replace('-',''),fallback=None):
            self.full_backup_decompress = True
        if self.incremental_dir[1]:
            cmd = 'cp -a {} {}'%(self.incremental_dir[1],self.tmp_dir)
            self._sshobject.execute_cmd(cmd)
            self.incremental_dir[1] = path_join(self.tmp_dir,self.incremental_dir[1].rpartition('/')[2])
            paramf = path_join(self.incremental_dir[1],self.backup_param_filename)
            if self.incremental_backup_param_config == None:
                self.incremental_backup_param_config = ConfigParser(allow_no_value=True)
            self.getBackupParam(paramf,self.incremental_backup_param_config)
            if self.incremental_backup_param_config.get(configparser.DEFAULTSECT,self.compress[0].replace(0).replace('-',''),fallback=None):
                self.incremental_backup_decompress = True
        self.setRestoreCnfFile()


    def updateBackupConfig(self):
        super(MysqlHotBackup, self).updateBackupConfig()
        if self._config.incremental_basedir:
            self.incremental_basedir[1] = self._config.incremental_basedir
        self.setBackupCnfFile()
        self.setSocket()

    def updateConfig(self):
        super(MysqlHotBackup, self).updateConfig()
        self.setBackupSoftWarePath()

    def prepareRestoreEnv(self):
        if not self._sshobject.fileExists(self.restore_target_dir):
            self._sshobject.mkdir()
        self._sshobject.execute_cmd('cd {};mkdir -p data var log'.format(self.restore_target_dir))
        self.datadir[1] = path_join(self.restore_target_dir,'data')

    def afterRestore(self):
        super(MysqlHotBackup, self).afterRestore()
        cmd = self.compactItem(False,self.mysqld_safe_software_path,self.defaults_file,'&')
        self._sshobject.execute_backupground(cmd)


class Xtrabackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(Xtrabackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.init()

    def init(self):
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
        super(Xtrabackup, self).updateBackupConfig()
        self.compress[2] = self._config.compress
        if string_true_bool(self.compress[2]):
            self.compress_threads[1] = 4

    @record_log
    def getBackupCmd(self):
        cmd = self.compactItem(False,self.backupsoftwarepath,self.defaults_file,self.user,self.password,self.target_dir,self.slave_info,self.safe_slave_backup,self.safe_slave_backup_timeout,self.socket,self.compress,self.compress_threads,self.incremental_basedir,self.backup,'2>&1')
        self.backup_param += ' ' + self.compactItem(True,self.compress,self.incremental_basedir)
        return cmd

    @record_log
    def afterBackup(self):
        log.debug('after backup')
        return super(Xtrabackup, self).afterBackup()

    def beforeRestore(self):
        super(Xtrabackup, self).beforeRestore()
        for k,v in ((self.incremental_backup_decompress,self.incremental_dir[1]),(self.full_backup_decompress,self.full_dir[1])):
            if k:
                self.target_dir[1] = v
                self.decompress[2] = k
                cmd = self.compactItem(False,self.backupsoftwarepath,self.decompress,self.target_dir,'2>&1')
                self._sshobject.execute_cmd(cmd)

        cmd = self.compactItem(False,self.backupsoftwarepath,self.target_dir,self.incremental_dir,self.prepare,'2>&1')
        stat,_ = self._sshobject.execute_cmd(cmd)
        return stat

    def do_restore(self):
        super(Xtrabackup, self).do_restore()
        cmd = 'cp %s  %s' % (self.defaults_file[1],path_join(self.restore_target_dir,'my.cnf'))
        self._sshobject.execute_cmd(cmd)
        self.defaults_file[1] = path_join(self.restore_target_dir,'my.cnf')
        self.target_dir[1] = self.full_dir[1]
        cmd = self.compactItem(False,self.backupsoftwarepath,self.defaults_file,self.target_dir,self.copy_back,'2>&1')
        stat,_ = self._sshobject.execute_cmd(cmd)
        return stat






class MysqlEnterpriseBackup(MysqlHotBackup):

    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlEnterpriseBackup, self).__init__(sshobject,backupconfig,ds,conn)
        self.backupsoftware[1] = 'mysqlbackup'

class MysqlLogicBackup(MysqlBackup):


    def __init__(self,sshobject,backupconfig,ds=None,conn=None):
        super(MysqlLogicBackup, self).__init__(sshobject,backupconfig,ds,conn)
        if self._config.operate == self._config._CONS_OPERATE_BACKUP:
            self.backupsoftware[1] = 'mysqldump'
        else:
            self.backupsoftware[1] = 'mysql'

    def setSoftWarePath(self):
        data = self.getMysqldCommand()
        if data:
            data = to_text(data).replace('--','')
            res = data.partition(' ')
        self.backupsoftwarepath = path_join(path.dirname(res[0]),self.backupsoftware[1])

    def preRestoreInit(self):
        self.full_dir[1] = self._config.backup_dir

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



