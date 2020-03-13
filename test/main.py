import copy
import os
import sys
import threading
from configparser import ConfigParser
from pathlib import Path

from deploy.mysql.backup import execute_cmd
from deploy.until import list_sqlfile, _sort, valid
from public_module import to_bytes, to_text
from public_module.config import BackupConfig
from public_module.ssh_connect.paramiko_ssh import ParamikoConnection


def list_sqlfile_new(filepath):
    base = Path(filepath)
    if base.exists():
        if base.is_dir():
            curlist = {}
            num = 0
            curdir = os.path.split(filepath)[1]
            subfiles = _sort([i for i in os.listdir(filepath) if valid(os.path.join(filepath,i))])
            curfiles = []
            for i in subfiles:
                if os.path.isdir(os.path.join(filepath,i)):
                    s = list_sqlfile_new(os.path.join(filepath,i))
                    if s[0]:
                        num = num+s[1]
                        curfiles.append(s[0])
                else:
                    curfiles.append(os.path.join(filepath,i))
                    num = num + 1
            if curfiles:
                curlist[curdir] = curfiles
                return curlist,num
            else:
                return None,0
        else:
            if os.path.splitext(filepath)[1].upper() == '.SQL':
                return filepath,1
    return None,0



def test_paramiko():
    with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
        # mysqlpath = '/usr/local/mysql-5.7.23-el7-x86_64/bin/mysqld_safe'
        # start_shell = mysqlpath+' --defaults-file=/database/my3579/my.cnf '
        # cmd = 'echo " nohup ' + start_shell + ' &" > /database/my3579/start.sh '
        # execute_cmd(cmd,sclient=pk)
        cmd = 'nohup sh /database/my3579/start.sh > /dev/null 2>&1 & '
        stat,_ = execute_cmd(cmd,sclient=pk)


def execute_backupground():
    cmd = '/usr/local/mysql-5.7.23-el7-x86_64/bin/mysqld_safe --defaults-file=/database/my3579/my.cnf & \r\n'
    with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
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
            print(to_text(data))
            data = stdout.readline()

class A(object):

    def __init__(self,pa,pb):
        self.a = pa
        self.b = pb



def isFileExists():
    with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
        sc = pk.open_sftp()
        msg = sc.stat('/database/my3578/my.cnf')
        print(msg)
        sc = pk.open_sftp()
        msg1 = sc.stat('/database/my3578/my.cnf.bk')
        print(msg1)
if '__main__' == __name__:
    # oa = A(1,2)
    # ob = copy.deepcopy(oa)
    # print('id:{},{}'.format(id(oa),id(ob)))
    # print('value:%d,%d' % (oa.a,ob.a))
    # ob.a = 3
    # print('value:%d,%d' % (oa.a,ob.a))

    # for i in dir(BackupConfig):
    #     print(i)
    # bc.databases = 'db1;db2;db3'
    # print(bc.databases)
    # test_paramiko()
    # execute_backupground()
    # sqlfiles,num = list_sqlfile_new('C:/Users/ZNV/Desktop/znvdb/vcms2.0/scimdb_objects/procedure')
    # print(num)
    # print(sqlfiles)
    # SimpleDeploy.exec(sqlfiles)
    # print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
    # v = ['1.0.2','1.0']
    # sort(v)
    # for i in  range(3,4):
    #     print(i)
    # print(sys.platform)
    s = '/abc/def'
    print(s[:-1])
    print(s.rpartition('/')[0])
    # isFileExists()

    outcnf = ConfigParser(allow_no_value=True)
    outcnf['a']='A'
    outcnf['b']='B'