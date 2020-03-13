import os
import threading
import time
import traceback
from configparser import ConfigParser
from os import path

import log
from deploy.mysql import DBUtils
from deploy.mysql.DataSource import getDS
from public_module import to_bytes, to_text
from public_module.config import BackupConfig, threadSafeConfig
import public_module.config as config
from public_module.global_vars import getNotifier
from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import formatDate, formatDateTime
from ui.myThread import MyThread

SHELL_SUCCESS=0
DEFAULT_BUFFER_SIZE=4096

def backup(backupconfig:BackupConfig):
    try:
        with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
            cmd = '/usr/bin/xtrabackup --defaults-file=/database/my3578/my.cnf -usuper -p8845  --target-dir="/data/backup/my3578/2020-03-13" --slave-info --safe-slave-backup  --backup  --safe-slave-backup-timeout=3000   --socket=/database/my3578/var/3578.socket  2>&1 '
            log.debug(cmd)
            stat,_ = execute_cmd(cmd,sclient=pk)
            log.info(stat)
            if stat == SHELL_SUCCESS:
                cmd = b'echo "compress=True \r\ncompress-threads=4 " > /data/backup/my3578/2020-03-13/backup_params.record'
                stat,_ = execute_cmd(cmd,sclient=pk)
                log.info(str(stat))
                cmd = r'cp /database/my3578/my.cnf  /data/backup/my3578/2020-03-13/'
                stat,_ = execute_cmd(cmd,sclient=pk)
                log.info(str(stat))
            return stat
    except BaseException as e:
        log.error(traceback.format_exc())


def backup_new():
    _config = threadSafeConfig.get()[config.MYSQL_BACKUP_CATEGORY]
    ds = getDS()
    conn = ds.get_conn()
    log.debug('connect to {}'.format(_config.get('host')))
    with ParamikoConnection(_config.get('host',None),_config.get('ssh_user',None),
                            _config.get('ssh_password',None)) as pk:
        log.debug('connect to {} success !'.format(_config.get('host')))
        if _config.get('operate',None) == BackupConfig._CONS_OPERATE_BACKUP:
            return inner_backup(pk,_config,conn)
        else:
            return inner_restore(pk,_config,conn)



def inner_backup(pk,pconfig,conn):
    cnfpath = getcnf(pk,conn)
    outcnf = ConfigParser()
    outcnf['backup_mode'] = pconfig['backup_mode']
    pconfig['backup_dir'] = pconfig['backup_base_dir'] + '/' + formatDate()
    log.info('check if backup dir exists')
    if fileExists(pk,pconfig['backup_dir']):
        log.info('backup dir {} exists,rename it !'.format(pconfig['backup_dir']))
        rename(pk,pconfig['backup_dir'])
    else:
        mkdir(pk,pconfig['backup_dir'])
    if pconfig['backup_mode'] == BackupConfig._CONS_BACKUP_MODE_FULL:
        cmd = pconfig['backup_software'] + ' --defaults-file=' + cnfpath + ' -u' + pconfig['user']
        outcnf['backup_software'] = pconfig['backup_software']
        cmd += ' -p' + pconfig['password'] + ' --target-dir=' + pconfig['backup_dir']
        cmd += ' --slave-info --safe-slave-backup  --backup  --safe-slave-backup-timeout=3000   --socket=' + DBUtils.getVariable(conn,'socket')
        if pconfig['compress']:
            cmd += ' --compress --compress-threads=4 '
            outcnf['compress'] = 'True'
            pass
        cmd += ' 2>&1'
        log.debug('ready to backup ! ')
        stat,_ = execute_cmd(cmd,sclient=pk)
        log.info('exit status = '+ str(stat))
        tmpfile = path.join(path.split(__file__)[0],'backup_params.record')
        if path.exists(tmpfile):
            os.rename(tmpfile,tmpfile+time.strftime("%Y%m%d%H%M%S", time.localtime()))
        with open(tmpfile,'w+') as f:
            outcnf.write(tmpfile)
        transferFileToRemote(tmpfile,pconfig['backup_dir']+'backup_params.record')
        cmd = 'cp ' + cnfpath + ' ' + pconfig['backup_dir'] + '/'
        execute_cmd(cmd,sclient=pk)
        if stat == 0:
            log.info('backup success!')
        else:
            log.error('backup failed!')
        return stat




def mkdir(pk,path):
    try:
        if fileExists(path):
            rename(path)
        sc = pk.open_sftp()
        sc.mkdir(path)
        return True
    except IOError as e:
        pass
    return False

def rename(pk,oldname,newname=None):
    if not newname:
        newname = oldname+formatDateTime()
    try:
        sc = pk.open_sftp()
        sc.rename(oldname,newname)
        return True
    except IOError as e:
        pass
    return False

def fileExists(pk,path):
    try:
        sc = pk.open_sftp()
        msg = sc.stat(path)
        return True
    except IOError as e:
        pass
    return False

def getcnf(pk,conn):
    datadir = DBUtils.getVariable(conn,'datadir')
    if datadir[-1] == '/':
        datadir = datadir[:-1]
    cnfpath = datadir.rpartition('/')[0] + '/my.cnf'
    if fileExists(pk,cnfpath):
        return cnfpath
    return None



def inner_restore(pk,pconfig):
    pass

def restore(backupconfig:BackupConfig):
    try:
        with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
            cmd = '/usr/bin/xtrabackup --target-dir="/data/backup/my3578/2020-03-13"  --prepare '
            # cmd = r"netstat -apn|grep -w LISTEN|sed 's= \{1,\}= =g'|cut -d ' ' -f 4|cut -d':' -f 4|grep -v -E '^$'"
            stat,_ = execute_cmd(cmd,sclient=pk)
            if stat == SHELL_SUCCESS:
                cmd = 'mkdir -p /database/my3579/data /database/my3579/var  /database/my3579/log'
                stat,_ = execute_cmd(cmd,sclient=pk)
                if stat == SHELL_SUCCESS:
                    cmd = 'cat /data/backup/my3578/2020-03-13/my.cnf'
                    stat,data = execute_cmd(cmd,sclient=pk,consumeoutput=False)
                    mycnf = ConfigParser(allow_no_value=True)
                    log.debug(to_text(data))
                    mycnf.read_string(to_text(data))
                    basepath = str()
                    tmpfile = path.join(path.split(__file__)[0],'my.cnf')
                    if path.exists(tmpfile):
                        os.rename(tmpfile,tmpfile+time.strftime("%Y%m%d%H%M%S", time.localtime()))
                    with open(tmpfile,'w+') as f:
                        for sec in mycnf.sections():
                            f.write('[' + sec + ']\r\n')
                            for k,v in mycnf.items(sec,True):
                                if k == 'basedir':
                                    basepath = v
                                v = str(v)
                                v = v.replace("/database/my3578","/database/my3579")
                                v = v.replace("3578","3579")
                                if not v or v == 'None' :
                                    f.write(k + '\r\n')
                                else:
                                    f.write(k + '=' + v + '\r\n')
                    # cmd = 'cat>/database/my3579/my.cnf<<EOF\r\n'+configstr+'EOF'
                    transferFileToRemote(tmpfile,'/database/my3579/my.cnf',pk)
                    cmd = '/usr/bin/xtrabackup --defaults-file=/database/my3579/my.cnf --target-dir="/data/backup/my3578/2020-03-13" --copy-back '
                    stat,_ = execute_cmd(cmd,sclient=pk)
                    cmd = 'cat /dev/null > /database/my3579/log/log.err'
                    execute_cmd(cmd,sclient=pk)
                    start_shell = basepath + '/bin/mysqld_safe '+' --defaults-file=/database/my3579/my.cnf  & \r\n'
                    execute_backupground(start_shell,pk)
                    cmd = 'ps -ef|grep 3579|grep -v grep|grep mysqld '
                    execute_cmd(cmd,sclient=pk)
                    cmd = 'ps -ef|grep 3579|grep -v grep|grep mysqld |wc -l'
                    stat,data = execute_cmd(cmd,sclient=pk,consumeoutput=False)
                    log.debug(str(stat))
                    if not (stat == 0 and int(data) > 0):
                        stat = 1
                        log.info(stat)
                        log.error('restored database start failed !')
                    else:
                        log.info('restore success !')
                    return stat
    except BaseException as e:
        log.error(traceback.format_exc())

def transferFileToRemote(localpath,remotepath,sclient,compress=True):
    try:
        sftpclient = sclient.open_sftp()
        sftpclient.put(localpath,remotepath)
        return True
    except IOError as e:
        log.error('transfer local file {} to remote {} failed.'.format(localpath,remotepath))
        log.error(traceback.format_exc())
        return False


def transferFileFromRemote(remotepath,localpath,sclient,compress=True):
    try:
        sftpclient = sclient.open_sftp()
        sftpclient.get(remotepath,localpath)
        return True
    except IOError as e:
        log.error('transfer local file {} to remote {} failed.'.format(localpath,remotepath))
        log.error(traceback.format_exc())
        return False

def execute_cmd(cmd,channel=None,sclient=None,consumeoutput=True,logtofile=None):
    try:
        log.debug(cmd)
        stdin = stdout = None
        if channel:
            channel.execute_cmd(to_bytes(cmd))
        elif sclient:
            channel,stdin,stdout = sclient.execute_cmd(to_bytes(cmd))
        else:
            return None,None
        result = bytes()
        data = channel.recv(DEFAULT_BUFFER_SIZE)
        while(data):
            if consumeoutput:
                log.info(to_text(data))
            else:
                result += data
            if logtofile:
                pass
            data = channel.recv(DEFAULT_BUFFER_SIZE)
        stat = channel.recv_exit_status()
        if channel:
            del channel
        if stdin:
            del stdin
        if stdout:
            del stdout
        return stat,result
    except BaseException as e:
        log.error(traceback.format_exc())


def execute_backupground(cmd,pk,consumeoutput=True,logtofile=None):
    channel,stdin,stdout = pk.newChannel()
    channel.invoke_shell()
    stdin.write(to_bytes(cmd))
    stdin.flush()
    def timerstop():
        threading.Event().wait(3)
        channel.close()
    threading.Thread(target=timerstop).start()
    data = stdout.readline()
    while(data or not channel.closed):
        if consumeoutput:
            log.info(to_text(data))
        if logtofile:
            pass
        data = stdout.readline()