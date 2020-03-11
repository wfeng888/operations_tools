from paramiko import SSHClient, WarningPolicy, Channel

from public_module import to_bytes
from public_module.ssh_connect import ConnectionBase, _DEFAULT_BUFFER_SIZE


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


    def execute_cmd(self,cmd):
        channel,stdin,stdout = self.newChannel()
        channel.exec_command(cmd)
        return channel,stdin,stdout

    def connect(self):
        self._init_client()

    def newChannel(self):
        if not self._sclint:
            self._init_client()
        channel = self._sclint.get_transport().open_session()
        channel.get_pty('vt100',200,50)
        stdout = channel.makefile('rb',_DEFAULT_BUFFER_SIZE)
        stdin = channel.makefile_stdin('rb',_DEFAULT_BUFFER_SIZE)
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

    def open_sftp(self):
        self._init_client()
        return self._sclint.open_sftp()