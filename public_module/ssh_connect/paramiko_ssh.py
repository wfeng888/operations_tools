import threading
import traceback
from functools import wraps

from paramiko import SSHClient, WarningPolicy, Channel

import log
from public_module import to_bytes, to_text
from public_module.ssh_connect import ConnectionBase


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

    # def execute_cmd(self,cmd):
    #     channel,stdin,stdout = self.newChannel()
    #     channel.exec_command(cmd)
    #     return channel,stdin,stdout

    def connect(self):
        self._init_client()

    @initial_only
    def newChannel(self):
        channel = self._sclint.get_transport().open_session()
        channel.get_pty('vt100',200,50)
        stdout = channel.makefile('rb',self.DEFAULT_BUFFER_SIZE)
        stdin = channel.makefile_stdin('wb',self.DEFAULT_BUFFER_SIZE)
        channel.set_combine_stderr(True)
        return channel,stdin,stdout

    def wait_until_end(self,channel:Channel):
        status  = channel.recv_exit_status()
        return status

    def close_channel(self,channel:Channel):
        channel.close()

    def close(self):
        if self._sclint:
            self._sclint.close()
            del self._sclint

    @initial_only
    def open_sftp(self):
        return self._sclint.open_sftp()


    def execute_backupground(self,cmd,consumeoutput=True,logtofile=None):
        channel,stdin,stdout = self.newChannel()
        channel.invoke_shell()
        stdin.write(to_bytes(cmd))
        stdin.flush()
        def timerstop():
            threading.Event().wait(1)
            channel.close()
        threading.Thread(target=timerstop).start()
        data = stdout.readline()
        while(data or not channel.closed):
            if consumeoutput:
                log.info(to_text(data))
            if logtofile:
                pass
            data = stdout.readline()
        return data

    def execute_cmd(self,cmd,consumeoutput=True,logtofile=None):
        try:
            log.debug(cmd)
            channel,_,_ = self.execute_cmd(to_bytes(cmd))
            result = bytes()
            data = channel.recv(self.DEFAULT_BUFFER_SIZE)
            while(data):
                if consumeoutput:
                    log.info(to_text(data))
                else:
                    result += data
                data = channel.recv(self.DEFAULT_BUFFER_SIZE)
            stat = channel.recv_exit_status()
            if channel:
                del channel
            return stat,result
        except BaseException as e:
            log.error(traceback.format_exc())


    def fileExists(self,path):
        try:
            sc = self.open_sftp()
            msg = sc.stat(path)
            return True
        except IOError as e:
            pass
        return False