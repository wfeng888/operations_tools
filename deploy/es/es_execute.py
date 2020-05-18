import logging
import os
import traceback
from functools import wraps

from elasticsearch.client import _make_path
from elasticsearch import Elasticsearch, ElasticsearchException, TransportError

import log
from deploy.es.es_config import ESConfig, ESDeployConfig, ESSnapshotRestoreConfig
from deploy.until import Sort, TYPE_ES
from public_module.global_vars import getNotifier
from public_module.utils import format_exc, formatDateTime, none_null_stringNone


def getClusterState(esconfig:ESConfig):
    log.debug('begin to check es cluster info')
    connects = [k for k  in esconfig.http_connect]
    client = Elasticsearch(connects)
    try:
        cluster = client.cluster.health()
        nodes = client.transport.perform_request('GET',_make_path('_cat','nodes'),params={'v':'y'})
        nodes = nodes.splitlines()
    except Exception as e:
        log.error(format_exc())
    else:
        log.debug(cluster.__repr__())
        for node in nodes:
            log.debug(node)

def file_exec(client,file,config,notifier=None):
    if not os.path.exists(file):
        return
    filename = os.path.splitext(os.path.split(file)[1])[0]
    items = filename.split('#')
    _oper = items[1]
    items = items[2:]
    _url = _make_path(*items)
    _body = None
    if not _oper.upper() == 'DELETE':
        with open(file,'r',encoding='utf-8') as f:
            _body = f.read()
    if config.log_statement:
        log.info(_url)
        log.info(_body)
    try:
        client.transport.perform_request(_oper,_url,body=_body)
    except ElasticsearchException as e:
        if isinstance(e,TransportError):
            log.error('status:%d, errorinfo: %s'% (e.status_code , e.error))
        else:
            log.error(traceback.format_exc())
        return -1
    return 0


def exec(client,sqlfiles,total=0,curnum=0,config=None,notifier=None):
    if isinstance(sqlfiles,dict):
        for k,v in sqlfiles.items():
            if -1 == exec(client,v,total,curnum,config,notifier) and not config.ignore_error:
                return -1
        return 0
    elif isinstance(sqlfiles,(tuple,list)):
        for k in sqlfiles:
            if -1 == exec(client,k,total,curnum,config,notifier) and not config.ignore_error:
                return -1
        return 0
    elif isinstance(sqlfiles,str):
        res = file_exec(client,sqlfiles,config,notifier)
        if -1 == res and not config.ignore_error:
            return -1
        cur_num = curnum +1
        notify_progress(cur_num*100/total,notifier)
        return 0

def notify_progress(value,notifer=None):
    if notifer:
        notifer.notifyProgress(value)

def result_wrap(func):
    @wraps(func)
    def wrapper(*args,**kwargs):
        status = -1
        res = {}
        try:
            res = func(*args,**kwargs)
            status = 0
        except ElasticsearchException as e:
            if getattr(e,'status_code',None) and getattr(e,'error',None):
                log.error('status:%d, error: %s, info: %s'% (e.status_code,e.error,e.info))
                res['error'] = e.error
            else:
                _msg = traceback.format_exc()
                log.error(_msg)
                res['error'] = _msg
        return res,status
    return wrapper

def exec_warp(esdepconfig:ESDeployConfig):
    client = Elasticsearch(esdepconfig.http_connect)
    notifer = getNotifier()
    sort = Sort(TYPE_ES,'.JSON')
    sqlfiles,num = sort.list_sqlfile(esdepconfig.file_path)
    exec(client,sqlfiles,num,0,esdepconfig,notifer)
    return True

@result_wrap
def exec_request(esconfig:ESConfig,_oper,urlitems,params={},body=None):
    client = Elasticsearch(esconfig.http_connect)
    if not isinstance(urlitems,(list,tuple)):
        urlitems = (urlitems,)
    return client.transport.perform_request(_oper,_make_path(*urlitems),body=body)


@result_wrap
def exec_snapshot(esconfig:ESConfig,repository,indices=(),ignore_unavailable=False,include_global_state=False,metadata={},url_params=()):
    client = Elasticsearch(esconfig.http_connect)
    body = '{'
    if indices:
        body += '"indices": "' + ','.join(indices) +  '",'
    body += '"ignore_unavailable":' + str(ignore_unavailable).lower() + ','
    body += '"include_global_state":' + str(include_global_state).lower() + ','
    if metadata:
        body += '"metadata":{'
        for k,v in metadata.items():
            body += '"' + str(k) + '": "' + '"' + str(v) + '",'
        body = body[:-1]
        body += '},'
    body = body[:-1]
    body += '}'
    snapshot = repository + formatDateTime()
    res = {}
    res['snapshot'] = snapshot
    res['result'] = client.snapshot.create(repository, snapshot, body, *url_params)
    log.debug(res)
    return res

@result_wrap
def register_snapshot(esconfig:ESSnapshotRestoreConfig,repository,type='fs',compress=True,bytes_per_sec='40mb',settings={},params={}):
    client = Elasticsearch(esconfig.http_connect)
    if not repository:
        repository = 'repository_' + os.path.split(esconfig.directory)[1]
    body = ''
    if type == 'fs':
        body += '"type": "fs",'
        for i in settings.keys():
            if i in ('location','chunk_size','max_restore_bytes_per_sec','max_snapshot_bytes_per_sec'):
                body += '"' + i + '": "' + str(settings.get(i)) + '",'
            if i in ('compress'):
                body += '"' + i + '":' + str(settings.get(i)).lower() + ','
        if body.find('compress') == -1:
            body += '"compress":' + str(compress).lower() + ','
        if body.find('max_restore_bytes_per_sec') == -1:
            body += '"max_restore_bytes_per_sec": "' + bytes_per_sec + '",'
        if body.find('max_snapshot_bytes_per_sec') == -1:
            body += '"max_snapshot_bytes_per_sec": "' + bytes_per_sec + '",'
        body = body[:-1]
    res = client.snapshot.create_repository(repository,body,params)
    res['repository'] = repository
    return res

def get_repository(config:ESConfig):
    res,stats = exec_request(config,'GET',('_snapshot','_all'))
    if 0 == stats:
        return res.keys()
    return None

@result_wrap
def get_repository_location(config:ESConfig):
    res,stats = exec_request(config,'GET',('_snapshot','_all'))
    locations = []
    if stats == 0:
        for i in res.keys():
            if res[i]['type'] == 'fs':
                locations.append((res[i],'fs','',res[i]['settings']['location']))
            if res[i]['type'] == 'hdfs':
                locations.append((res[i],'hdfs',res[i]['settings']['uri']))
    return locations


def list_snapshots(config:ESConfig):
    res = get_repository(config)
    snapshots = {}
    for repository in res:
        res,stats = exec_request(config,'GET',('_snapshot',repository,'*'))
        if 0 == stats:
            snapshots[repository] = {}
            for snapshot in res['snapshots']:
                snapshots[repository][snapshot['snapshot']] = snapshot['indices']
    return snapshots

def expand(param={}):
    body = '{'
    for k,v in param.items():
        if not none_null_stringNone(v):
            body += '"' + k +'":'
            if isinstance(v,bool):
                body += str(v).lower()
            elif isinstance(v,(int,float)):
                body += str(v)
            elif isinstance(v,str):
                body += '"' + v + '"'
            elif isinstance(v,(tuple,list)):
                _v = [_i for _i in v if not none_null_stringNone(_i)]
                body += _v.__repr__()
            if isinstance(v,dict):
                # value = expand(v)
                # if value != '{}':
                #     body += value
                body += expand(v)
            body += ','
    if body[-1] == ',':
        body = body[:-1]
    body += '}'
    return body

def checkAndSet(obj,attr,target,t_attr=None):
    _v = getattr(obj,attr,None)
    if not none_null_stringNone(_v):
        if not t_attr:
            t_attr = attr
        target[t_attr] = _v
#
# POST _snapshot/restore_readonly_repository/snapshot_1056/_restore
# {
#     "indices": "human*,ac_blog",
#     "rename_pattern": "(.+)",
#     "rename_replacement": "restored_index_$1",
#     "ignore_unavailable": true,
#     "include_global_state": true,
#     "partial":true,
#     "index_settings":{
#         "index.number_of_replicas":0
#     },
#     "include_aliases": false,
#     "ignore_index_settings":[
#         "index.refresh_interval"
#     ]
# }
@result_wrap
def exec_restore(config:ESSnapshotRestoreConfig,repository,snapshotid):
    client = Elasticsearch(config.http_connect)
    body = {}
    checkAndSet(config,'index_name',body,'indices')
    checkAndSet(config,'rename_pattern',body)
    checkAndSet(config,'ignore_unavailable',body)
    checkAndSet(config,'include_global_state',body)
    checkAndSet(config,'partial',body)
    checkAndSet(config,'index_settings',body)
    checkAndSet(config,'include_aliases',body)
    checkAndSet(config,'ignore_index_settings',body)
    checkAndSet(config,'rename_replacement',body)
    body = expand(body)
    log.debug(config.http_connect)
    log.debug('%s %s'%('POST',_make_path('_snapshot',repository,snapshotid,'_restore')))
    log.debug(body)
    res = client.snapshot.restore(repository,snapshotid,body)
    return res

