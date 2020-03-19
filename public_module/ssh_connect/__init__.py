import traceback
from abc import ABCMeta, abstractmethod

import log
from public_module import ContextManager
from public_module.utils import formatDateTime


class ConnectionBase(ContextManager,metaclass=ABCMeta):

    SHELL_FAILED=-1
    SHELL_SUCCESS=0
    DEFAULT_BUFFER_SIZE=4096

    def __init__(self,host,user,password,port=22):
        self._host = host
        self._user = user
        self._password = password
        self._port = port


    @abstractmethod
    def fileExists(self):
        pass

    @abstractmethod
    def open_sftp(self):
        pass


    def mkdir(self,path):
        try:
            if self.fileExists(path):
                self.rename(path)
            cmd = 'mkdir -p %s'%path
            stat,_ = self.execute_cmd(cmd)
            return  stat == self.SHELL_SUCCESS
        except IOError as e:
            pass
        return False

    def rename(self,oldname,newname=None):
        if not newname:
            newname = oldname+formatDateTime()
        try:
            sc = self.open_sftp()
            sc.rename(oldname,newname)
            return True
        except IOError as e:
            pass
        return False


    def execute_cmd(self,cmd,consumeoutput=True,logtofile=None):
        pass

    @abstractmethod
    def execute_backupground(self,cmd,consumeoutput=True,logtofile=None):
        pass

    def transferFileToRemote(self,localpath,remotepath,compress=True):
        try:
            self.open_sftp().put(localpath,remotepath)
            return True
        except IOError as e:
            log.error('transfer local file {} to remote {} failed.'.format(localpath,remotepath))
            log.error(traceback.format_exc())
            return False



    def transferFileFromRemote(self,remotepath,localpath,compress=True):
        try:
            self.open_sftp().get(remotepath,localpath)
            return True
        except IOError as e:
            log.error('transfer local file {} to remote {} failed.'.format(localpath,remotepath))
            log.error(traceback.format_exc())
            return False



