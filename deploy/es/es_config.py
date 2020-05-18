from enum import Enum

from public_module.config import ConfigBase
from public_module.utils import none_null_stringNone


class ESConfig(ConfigBase):
    http_connect:list

class ESDeployConfig(ESConfig):
    file_path:str
    ignore_error:bool
    log_statement:bool

class SnapshotRestoreStatus(Enum):
    IN_PROGRESS = 'IN_PROGRESS'
    SUCCESS = 'SUCCESS'
    FAILED = 'FAILED'
    PARTIAL = 'PARTIAL'
    INCOMPATIBLE = 'INCOMPATIBLE'

class ESSnapshotRestoreConfig(ESConfig):
    directory:str
    repository:str
    index_name:str
    ignore_unavailable:bool
    include_global_state:bool
    url_params:dict
    snapshotid:str
    rename_pattern:str
    partial:bool
    index_settings:dict
    include_aliases:bool
    ignore_index_settings:list
    rename_replacement:str
    _CONS_STATUS = SnapshotRestoreStatus

class ESInstallConfig(ESDeployConfig):
    ssh_host:str
    ssh_user:str
    ssh_passwd:str
    ssh_port:str
    es_tgz_path:str
    es_base_path:str
    yml_config:dict
    jvm_heap:str

    def install_check(self):
        return True

def get_yml_value(obj:dict,*attrs):
    if none_null_stringNone(attrs):
        return obj
    if  none_null_stringNone(obj):
        return None
    for i in range(1,len(attrs)+1):
        s = get_yml_value(obj.get('.'.join(attrs[0:i]),None),*attrs[i:])
        if not none_null_stringNone(s):
            return s
    return None