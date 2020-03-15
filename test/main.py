# import copy
# import os
# import sys
# import threading
# from configparser import ConfigParser
# from pathlib import Path
#
# from deploy.mysql.backup import execute_cmd
# from deploy.until import list_sqlfile, _sort, valid
# from public_module import to_bytes, to_text
# from public_module.config import BackupConfig
# from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
#
#
# def list_sqlfile_new(filepath):
#     base = Path(filepath)
#     if base.exists():
#         if base.is_dir():
#             curlist = {}
#             num = 0
#             curdir = os.path.split(filepath)[1]
#             subfiles = _sort([i for i in os.listdir(filepath) if valid(os.path.join(filepath,i))])
#             curfiles = []
#             for i in subfiles:
#                 if os.path.isdir(os.path.join(filepath,i)):
#                     s = list_sqlfile_new(os.path.join(filepath,i))
#                     if s[0]:
#                         num = num+s[1]
#                         curfiles.append(s[0])
#                 else:
#                     curfiles.append(os.path.join(filepath,i))
#                     num = num + 1
#             if curfiles:
#                 curlist[curdir] = curfiles
#                 return curlist,num
#             else:
#                 return None,0
#         else:
#             if os.path.splitext(filepath)[1].upper() == '.SQL':
#                 return filepath,1
#     return None,0
#
#
#
# def test_paramiko():
#     with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
#         # mysqlpath = '/usr/local/mysql-5.7.23-el7-x86_64/bin/mysqld_safe'
#         # start_shell = mysqlpath+' --defaults-file=/database/my3579/my.cnf '
#         # cmd = 'echo " nohup ' + start_shell + ' &" > /database/my3579/start.sh '
#         # execute_cmd(cmd,sclient=pk)
#         cmd = 'nohup sh /database/my3579/start.sh > /dev/null 2>&1 & '
#         stat,_ = execute_cmd(cmd,sclient=pk)
#
#
# def execute_backupground():
#     cmd = '/usr/local/mysql-5.7.23-el7-x86_64/bin/mysqld_safe --defaults-file=/database/my3579/my.cnf & \r\n'
#     with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
#         channel,stdin,stdout = pk.newChannel()
#         channel.invoke_shell()
#         stdin.write(to_bytes(cmd))
#         stdin.flush()
#         def timerstop():
#             threading.Event().wait(3)
#             channel.close()
#         threading.Thread(target=timerstop).start()
#         data = stdout.readline()
#         while(data or not channel.closed):
#             print(to_text(data))
#             data = stdout.readline()
#
# class A(object):
#
#     def __init__(self,pa,pb):
#         self.a = pa
#         self.b = pb
#
#
#
# def isFileExists():
#     with ParamikoConnection('10.45.156.210','mysql','8845') as pk:
#         sc = pk.open_sftp()
#         msg = sc.stat('/database/my3578/my.cnf')
#         print(msg)
#         sc = pk.open_sftp()
#         msg1 = sc.stat('/database/my3578/my.cnf.bk')
#         print(msg1)
import re
import traceback


class A(object):

    def __init__(self):
        self.a = 1
        self.b = 2

    def __delete__(self, instance):
        print('__delete__')
        print(instance)

    def __del__(self):
        print('__del__')

class B(object):
    ca = 1
    cb = 2

    def __init__(self,p):
        self._p = p


    def instance_func(self,param):
        print('{},{},{}'.format('instance_func',param,self._p))

    @classmethod
    def class_func(cls,param):
        print('{},{}'.format('class_func',param))

class C(B):
    ca = 3

def test_static_field():
    oa = B()
    ob = B()
    print(id(oa.ca))
    print(id(ob.ca))
    print(id(B.ca))
    B.ca = 10
    print(id(oa.ca))
    print(id(ob.ca))
    print(id(B.ca))
    oa.ca = 20
    print(id(oa.ca))
    print(id(ob.ca))
    print(id(B.ca))
    del oa.ca
    print(id(oa.ca))
    print(id(ob.ca))
    print(id(B.ca))

def test_father_static():
    oc = B('poc')
    oc1 = C('poc1')
    print(oc.ca)
    print(oc1.ca)
    print(oc.cb)
    print(oc1.cb)


def safe_doing(func,*args):
    try:
        func(*args)
    except BaseException as e:
        print(traceback.format_exc())

def test_safe_doing():
    ob = B('ob')
    oa = B('oa')
    safe_doing(oa.instance_func,*(1,))
    safe_doing(ob.instance_func,*(2,))
    safe_doing(B.class_func,*(2,))

def test_null():
    if ' ':
        print(1)
    if ' '.strip():
        print(2)

def re_search():
    content = r'''no extrabackup in
    [root@mha-master my3578]# which extrabackup
/usr/bin/which: no extrabackup in (/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/bigdata/hadoop/hadoop-3.1.2/bin:/bigdata/hbase/hbase-2.2.0/bin:/bigdata/spark/spark-2.4.3-bin-hadoop2.7/bin:/access/test/mysql/bin:/access/test/mysql-5.7.27-linux-x86_64_VCMS_2.0.20190910_R1/mysql/bin:/access/mysql/bin:/access/mysql/bin:/access/mysql/bin:/test/mysql/bin:/root/bin)
[root@mha-master my3578]# which xtrabackup
/usr/bin/xtrabackup'''
    # m = re.search('no extrabackup in','content', re.RegexFlag.IGNORECASE)
    index = content.find('which xtrabackup')
    print(index)

def test_split():
    cont = '/access/test/mysql/bin/mysqld --basedir=/access/test/mysql --datadir=/access/test/mysql/data --plugin-dir=/access/test/mysql/lib/plugin --user=mysql --log-error=/access/test/mysql/log/log.err --pid-file=/access/test/mysql/data/mha-master.pid --socket=/access/test/mysql/var/mysql.sock --port=3306'
    r = cont.partition(' ')
    print(r)
    r = r[2].split(maxsplit=90)
    print(r)


reg = {
    'Yes':'Y',
    'No':'N',
    'Both':'B',
    'Session':'S',
    'Global':'G',
    'Varies':'V'
}

def convert(p):
    if not p:
        return 'None'
    else:
        return reg[p]

def format_var():
    with open('D:/tmp/my57.var') as f:
        with open('D:/tmp/my57.var.format','w+') as w:
            i = 0
            data = f.readline()
            while(data):
                res = data.split('\t')
                if not res[0].startswith('- Variable:'):
                    w.write("'"+res[0]+"':("+convert(res[1])+","+convert(res[2])+","+convert(res[3])+","+convert(res[4])+","+convert(res[5])+","+convert(res[6].replace("\n",""))+"),\n")
                if res[2] == 'Yes':
                    i += 1
                data = f.readline()
            w.flush()
            print(i)


def format_cnf():
    with open('D:/tmp/my.cnf.template') as f:
        with open('D:/tmp/my.cnf.template.format','w+') as w:
            i = 0
            data = f.readline()
            while(data):
                if data.strip():
                    res = data.partition('=')
                    w.write("'"+res[0].strip()+"',")
                data = f.readline()
            w.flush()
            print(i)


if '__main__' == __name__:
    format_cnf()
    # test_split()
    # re_search()
    # test_null()
    # test_father_static()
    # ob.ca = 11
    # va = 10
    # print(id(oa.ca))
    # print(id(ob.ca))
    # print(id(B.ca))
    # print(id(va))
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
    # s = '/abc/def'
    # print(s[:-1])
    # print(s.rpartition('/')[0])
    # # isFileExists()
    #
    # outcnf = ConfigParser(allow_no_value=True)
    # outcnf['a']='A'
    # outcnf['b']='B'
    # a = '123,'
    # a = a.split(',')
    # a[2] = '456'
    # print(a)

    # sa = A()
    #
    # del sa.a
    # del sa