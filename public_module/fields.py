from functools import  partial

from public_module.utils import none_null_stringNone


def getx(cname,iself):
    return iself._attributes.get(cname,None)

def setx(cname,cself, value):
    cls = cself.__class__.__annotations__[cname]
    if value == None:
        cself._attributes[cname] = None
        return
    if isinstance(cls,int) or cls == int:
        if not none_null_stringNone(value):
            cself._attributes[cname] = int(value)
    elif isinstance(cls,(list,tuple)) or cls in (list,tuple):
        if not isinstance(value,(list,tuple)) and not none_null_stringNone(value):
            cself._attributes[cname] = value.split(',')
        elif isinstance(value,(list,tuple)):
            cself._attributes[cname] = value
        else:
            cself._attributes[cname] = (value,)
    elif isinstance(cls,dict) or cls == dict:
        if not isinstance(value,dict):
            if not getattr(cself._attributes,cname,None):
                cself._attributes[cname] = {}
            for item in value.split(','):
                if str(item).find(':') > 0:
                    cself._attributes[cname][item.split(':')[0]] = item.split(':')[1]
        else:
            cself._attributes[cname] = value
    elif isinstance(cls,bool) or cls == bool:
        cself._attributes[cname] = True if value and str(value).upper() == 'TRUE' else False
    else:
        cself._attributes[cname] = value


class FieldMeta(type):
    def __new__(cls,clsname,bases,dicts):
        def _addBaseAnnotations(parents):
            for parent in parents:
                if not parent.__name__ == 'object' and not parent.__name__ == 'type':
                    if hasattr(parent,'__dict__') and parent.__dict__.get('__annotations__',None):
                        for key in  (set(parent.__dict__['__annotations__'].keys()) - set(dicts['__annotations__'].keys())):
                            dicts['__annotations__'][key] = parent.__dict__['__annotations__'][key]
                    if hasattr(parent,'__dict__') and parent.__dict__.get('_attribute_names',None):
                        dicts['_attribute_names'].update(parent.__dict__.get('_attribute_names'))
                    _addBaseAnnotations(parent.__bases__)
        names = []
        # dicts['_attributes'] = dict()
        dicts['_attribute_names'] = set()
        if not dicts.get('__annotations__',None):
            dicts['__annotations__'] = {}
        for name in dicts['__annotations__'].keys():
            if not name.startswith('__') and not name.startswith('_CONS'):
                names.append(name)
        for name in names:
            getter = partial(getx,'_'+name)
            setter = partial(setx,'_'+name)
            dicts[name] = property(getter,setter)
            dicts['_attribute_names'].add(name)
            dicts['__annotations__']['_'+name] = dicts['__annotations__'][name]
        _addBaseAnnotations(bases)
        return type.__new__(cls,clsname,bases,dicts)