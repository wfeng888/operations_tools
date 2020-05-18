import functools
import math
import os
import threading
from re import RegexFlag
import re

import yaml

import log
from deploy.es import ESInstallCheckException
from deploy.es.es_config import ESInstallConfig, get_yml_value
from public_module import to_text, ssh_connect
from public_module.ssh_connect import ConnectionBase, checkAndRaise
from public_module.ssh_connect.paramiko_ssh import ParamikoConnection
from public_module.utils import none_null_stringNone, path_join, formatDateTime


def testSSHConnect(connetobj):
    stat,data = connetobj.execute_cmd('echo ~')
    if stat == ConnectionBase.SHELL_SUCCESS:
        return True
    return False


def isPortBusy(port,connectobj):
    port = str(port)
    cmd = "netstat -apn|grep -w -E '(\\S+):%s'|grep -w 'LISTEN'|wc -l"%port
    if not re.match(r'[1-9][0-9]+',port,RegexFlag.IGNORECASE):
        return False
    stat,data = connectobj.execute_cmd(cmd,False)
    if stat == ConnectionBase.SHELL_SUCCESS and int(to_text(data)) < 1:
        return False
    return True



def install_check(configs):
    if none_null_stringNone(configs):
        log.error('can not install es with no config setting')
    for config in configs:
        with ParamikoConnection(config.ssh_host,config.ssh_user,config.ssh_passwd,config.ssh_port) as pk:
            if not testSSHConnect(pk):
                log.error('ssh connect to %s@%s:/%s failed, please check!'%(config.ssh_host,config.ssh_user,config.ssh_port))
                raise ESInstallCheckException('ssh connect to %s@%s:/%s failed, please check!'%(config.ssh_host,config.ssh_user,config.ssh_port))
                return False
            if not pk.fileExists(config.es_tgz_path):
                log.error('elasticsearch software tgz file not exists, stop install!')
                raise ESInstallCheckException('elasticsearch software tgz file not exists, stop install!')
                return False
            if isPortBusy(get_yml_value(config.yml_config,*('http','port')),pk) or isPortBusy(get_yml_value(config.yml_config,*('transport','tcp','port')),pk):
                log.error('http port %s or transport port %s is busy, stop install!'%(get_yml_value(config.yml_config,*('http','port')),get_yml_value(config.yml_config,*('transport','tcp','port'))))
                raise ESInstallCheckException('http port %s or transport port %s is busy, stop install!'%(get_yml_value(config.yml_config,*('http','port')),get_yml_value(config.yml_config,*('transport','tcp','port'))))
                return False

def re_construct_config(configs):
    size = len(configs)
    minimum_master_nodes = math.floor(size/2) + 1
    discovery_zen_ping_unicast_hosts = []
    for config in configs:
        discovery_zen_ping_unicast_hosts.append('%s:%s'%(get_yml_value(config.yml_config,*('transport','host')),get_yml_value(config.yml_config,*('transport','tcp','port'))))
    for config in configs:
        config.yml_config['discovery.zen.minimum_master_nodes'] = minimum_master_nodes
        config.yml_config['discovery.zen.ping.unicast.hosts'] = discovery_zen_ping_unicast_hosts

def start_es(config):
    with ParamikoConnection(config.ssh_host,config.ssh_user,config.ssh_passwd,config.ssh_port) as pk:
        cmd = 'su -l elasticsearch -c "sh %s"'%path_join(config.es_base_path,('scripts','start.sh'))
        pk.execute_backupground(cmd,logfile=path_join(get_yml_value(config.yml_config,*('path','logs')),get_yml_value(config.yml_config,*('cluster','name'))))

def install(config):
    with ParamikoConnection(config.ssh_host,config.ssh_user,config.ssh_passwd,config.ssh_port) as pk:
        execute_cmd = functools.partial(ssh_connect.exec,pk.execute_cmd)
        mkdir = functools.partial(ssh_connect.exec,pk.mkdir)
        mkdir((config.es_base_path,))
        mkdir((get_yml_value(config.yml_config,*('path','data')),))
        mkdir((get_yml_value(config.yml_config,*('path','logs')),))
        mkdir((path_join(config.es_base_path,'config'),))
        mkdir((path_join(config.es_base_path,'scripts'),))
        mkdir((path_join(config.es_base_path,'var'),))
        mkdir((path_join(config.es_base_path,'software'),))
        cmd = 'cp %s %s'%(config.es_tgz_path,path_join(config.es_base_path,'software'))
        execute_cmd((cmd,))
        cmd = 'cd %s ; tar -xzpvf %s '%(path_join(config.es_base_path,'software'),os.path.split(config.es_tgz_path)[1])
        execute_cmd((cmd,))
        software_name= os.path.split(config.es_tgz_path)[1][:-7]
        cmd = 'cp %s %s'%(path_join(config.es_base_path,('software',software_name,'config','log4j2.properties')), \
                                 path_join(config.es_base_path,'config'))
        execute_cmd((cmd,))
        cmd = 'cp %s %s'%(path_join(config.es_base_path,('software',software_name,'config','jvm.options')), \
                                 path_join(config.es_base_path,'config'))
        execute_cmd((cmd,))
        transferFileToRemote = functools.partial(ssh_connect.exec,pk.transferFileToRemote)
        result = transferFileToRemote((os.path.join(os.path.dirname(os.path.abspath(__file__)),'root_execute.sh'),path_join(config.es_base_path,('scripts','root_execute.sh'))))
        if config.ssh_user == 'root':
            cmd = 'chmod u+x %s'%path_join(config.es_base_path,('scripts','root_execute.sh'))
            execute_cmd((cmd,))
            cmd = 'sh %s'%path_join(config.es_base_path,('scripts','root_execute.sh'))
            execute_cmd(cmd)
        tmp_file=os.path.join(os.path.dirname(os.path.abspath(__file__)),'elasticsearch.yml'+formatDateTime()+get_yml_value(config.yml_config,*('http','host')) + \
                              get_yml_value(config.yml_config,*('http','port')))
        with open(tmp_file,'w',encoding='utf-8') as f:
            yaml.dump(config.yml_config,f)
        result = transferFileToRemote((tmp_file,path_join(config.es_base_path,('config','elasticsearch.yml'))))
        s = 'sed -r -i -e \"s=\"\'^\\s*-Xms[0-9]+g\\s*$\'\"=-Xms%s=\" -e  \"s=\"\'^\\s*-Xmx[0-9]+g\\s*$\'\"=-Xmx%s=\" %s'
        for jvm_path in (path_join(config.es_base_path,('config','jvm.options')),path_join(config.es_base_path,('software',software_name,'config','jvm.options'))):
            cmd = s%(config.jvm_heap,config.jvm_heap,jvm_path)
            execute_cmd((cmd,))
        transferFileToRemote((os.path.join(os.path.dirname(os.path.abspath(__file__)),'start.sh'),path_join(config.es_base_path,('scripts','start.sh'))))
        transferFileToRemote((os.path.join(os.path.dirname(os.path.abspath(__file__)),'stop.sh'),path_join(config.es_base_path,('scripts','stop.sh'))))
        user_es = 'elasticsearch'
        cmd = 'id -u %s'%user_es
        _,data = execute_cmd((cmd,False))
        data = to_text(data)
        if not re.match(r'^[0-9]+',data):
            cmd = 'useradd -m -s /sbin/nologin -U %s'%user_es
            execute_cmd((cmd,))
        cmd = 'chown -R %s:%s  %s  %s  %s'%(user_es,user_es,config.es_base_path,get_yml_value(config.yml_config,*('path','data')),get_yml_value(config.yml_config,*('path','logs')))
        execute_cmd((cmd,))

    # for config in configs:
    #     threading.Thread(target=start_es,args=(config,)).start()



def install_all(configs):
    for config in configs:
        install(config)





