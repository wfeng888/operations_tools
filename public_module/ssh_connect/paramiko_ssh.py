import re
import threading
import traceback
from functools import wraps

from paramiko import SSHClient, WarningPolicy, Channel
import stat

import log
from public_module import to_bytes, to_text
from public_module.ssh_connect import ConnectionBase
from public_module.utils import safe_doing, none_null_stringNone


def initial_only(func):
    @wraps(func)
    def _inner_func(self,*args,**kwargs):
        self._init_client()
        return func(self,*args,**kwargs)

    return _inner_func

class ParamikoConnection(ConnectionBase):
    def __init__(self,host,user,password,port=22):
        super(ParamikoConnection, self).__init__(host,user,password,port)
        self._sclint = None
        self._transport = None

    def _init_client(self):
        if not self._sclint:
            self._sclint = SSHClient()
            self._sclint.load_system_host_keys()
            self._sclint.set_missing_host_key_policy(WarningPolicy)
            self._sclint.connect(self._host,self._port,self._user,self._password)
            self._transport = self._sclint.get_transport()
            self._transport.set_keepalive(5)

    def inner_execute_cmd(self,cmd):
        channel,stdin,stdout = self.newChannel()
        channel.exec_command(cmd)
        return channel,stdin,stdout

    def connect(self):
        self._init_client()

    @initial_only
    def newChannel(self,combine=True):
        channel = self._sclint.get_transport().open_session()
        channel.get_pty('vt100',200,50)
        stdout = channel.makefile('rb',self.DEFAULT_BUFFER_SIZE)
        stdin = channel.makefile_stdin('wb',self.DEFAULT_BUFFER_SIZE)
        if combine:
            channel.set_combine_stderr(True)
            return channel,stdin,stdout
        else:
            stderror = channel.makefile_stderr('rb',self.DEFAULT_BUFFER_SIZE)
            return channel,stdin,stdout,stderror


    def wait_until_end(self,channel:Channel):
        status  = channel.recv_exit_status()
        return status

    def close_channel(self,channel:Channel):
        channel.close()

    def close(self):
        if self._sclint:
            self._sclint.close()
            # del self._sclint

    @initial_only

    def open_sftp(self):
        return self._sclint.open_sftp()


    def execute_backupground(self,cmd,consumeoutput=True,logfile=None,logmode='r',mode='w',wait=False):
        cmd = cmd.strip()
        if cmd[-1] != '&':
            cmd += ' &'
        log.debug(cmd)
        channel,stdin,stdout = self.newChannel()
        channel.invoke_shell()
        stdin.write(to_bytes(cmd + '\r\n'))
        stdin.flush()
        def timerstop(spread=2):
            threading.Event().wait(spread)
            channel.close()
        def wait_process_end(processid):
            pinfo = processid
            while(none_null_stringNone(pinfo)):
                timerstop(10)
                cmd = 'ps --no-header -p %s'%processid
                st,pinfo = self.execute_cmd(cmd)
                if st == 0 and pinfo:
                    tpid = to_text(pinfo).strip().split()[0]
                    if tpid == pinfo:
                        continue
                break
            safe_doing(channel.close)
        def outputlog():
            while (not self.fileExists(logfile) and not channel.closed):
                threading.Event().wait(1)
            if self.fileExists(logfile) and not channel.closed:
                cmd = 'tail -f %s '%logfile
                stdin.write(to_bytes(cmd) + '\r\n')
                stdin.flush()
                data = stdout.readline()
                while(data or not channel.closed):
                    log.info(to_text(data))
                    data = stdout.readline()
        data = stdout.readline()
        while(data):
            pid = to_text(data).split()[1]
            if re.match('[0-9]+',pid):
                break
            data = stdout.readline()
        if wait:
            if re.match('[0-9]+',pid):
                threading.Thread(target=wait_process_end,args=(pid,)).start()
                outputlog()
            else:
                safe_doing(channel.close)
        else:
            threading.Thread(target=timerstop).start()
            while(data or not channel.closed):
                if consumeoutput:
                    log.info(to_text(data))
                if logfile:
                    pass
                data = stdout.readline()


    def execute_cmd(self,cmd,consumeoutput=True,logfile=None,mode='w'):
        try:
            log.debug(cmd)
            channel,_,_ = self.inner_execute_cmd(to_bytes(cmd))
            result = bytes()
            data = channel.recv(self.DEFAULT_BUFFER_SIZE)
            l = None
            if logfile:
                l =  open(logfile,mode)
            while(data):
                if consumeoutput:
                    log.info(to_text(data))
                else:
                    result += data
                if l:
                    l.write(data)
                data = channel.recv(self.DEFAULT_BUFFER_SIZE)
            stat = channel.recv_exit_status()
            if channel:
                del channel
            if l:
                safe_doing(l.close)
            return stat,result
        except BaseException as e:
            log.error(traceback.format_exc())

    def stat(self,remotepath):
        try:
            return self.open_sftp().stat(remotepath)
        except IOError as e:
            return None

    def fileExists(self,path):
        msg = self.stat(path)
        if msg:
            return True
        return False

    def isDir(self,path):
        msg = self.stat(path)
        if msg:
            return stat.S_ISDIR(msg.st_mode)
        else:
            return None

    def isFile(self,path):
        msg = self.stat(path)
        if msg:
            return stat.S_ISREG(msg.st_mode)
        else:
            return None

    def isLink(self,path):
        msg = self.stat(path)
        if msg:
            return stat.S_ISLNK()
        else:
            None

    def listdir(self,dir):
        return self.open_sftp().listdir(dir)