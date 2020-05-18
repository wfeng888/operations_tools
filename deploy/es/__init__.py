


def compact(name,value=None,required=True):
    return {'name':name,'value':value,'required':required}

CONSTANTS_CONFIG=(
    compact('ssh_host','10.45.156.201'),
    compact('ssh_port','22'),
    compact('ssh_user','root'),
    compact('ssh_passwd','8845'),
    compact('es_base_path','/bigdata/cluster_t'),
    compact('es_tgz_path','/home/elasticsearch/elasticsearch-5.4.3.tar.gz'),
    compact('jvm_heap','1G'),
    compact('path.data','/bigdata/cluster_t/data'),
    compact('path.logs','/bigdata/cluster_t/log'),
    compact('cluster.name','cluster_t'),
    compact('node.name','MYSQL1'),
    compact('network.host','10.45.156.201'),
    compact('http.host','10.45.156.201'),
    compact('http.port','9400'),
    compact('transport.host','10.45.156.201'),
    compact('transport.tcp.port','9500'),
    compact('node.master','true'),
    compact('node.data','true'),
    compact('node.ingest','true')
)



class ESInstallCheckException(Exception):
    _msg =  ' '
    def __init__(self,msg):
        if msg:
            self._msg += ' ' + msg

    def __repr__(self):
        return self._msg