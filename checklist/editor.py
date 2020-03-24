import itertools
import string
import numpy as np

def recursive_format(obj, mapping):
    if type(obj) in [str, bytes]:
        return obj.format(**(mapping))
    elif type(obj) == tuple:
        return tuple(recursive_format(list(obj), mapping))
    elif type(obj) == list:
        return [recursive_format(o, mapping) for o in obj]
    elif type(obj) == dict:
        return {k: recursive_format(v, mapping) for k, v in obj.items()}
    else:
        return obj

def find_all_keys(obj):
    ret = set()
    if type(obj) in [str, bytes]:
        f = string.Formatter()
        ret = ret.union([x[1] for x in (f.parse(obj))])
    elif type(obj) in [tuple, list, dict]:
        if type(obj) == dict:
            obj = obj.values()
        k = [find_all_keys(x) for x in obj]
        k = [x for x in k if x]
        for x in k:
            ret = ret.union(x)
    return set([x for x in ret if x])

class Editor(object):
    def __init__(self):
        self.lexicons = {}
    def template(self, templates, return_meta=False, nsamples=None, product=True, remove_duplicates=False, **kwargs):
    # 1. go through object, find every attribute inside brackets
    # 2. check if they are in kwargs and self.attributes
    # 3. generate keys and vals
    # 4. go through object, generate
        all_keys = find_all_keys(templates)
        items = {}
        for k in all_keys:
            # TODO: process if ends in number
            # TODO: process if is a:key to add article
            if k in kwargs:
                items[k] = kwargs[k]
            elif k in self.lexicons:
                items[k] = self.lexicons[k]
            else:
                raise(Exception('Error: key "%s" not in items or lexicons' % k))
        keys = [x[0] for x in items.items()]
        vals = [[x[1]] if type(x[1]) not in [list, tuple] else x[1] for x in items.items()]
        if nsamples is not None:
            v = [np.random.choice(x, nsamples) for x in vals]
            vals = zip(*v)
        else:
            if not product:
                vals = zip(*vals)
            else:
                vals = itertools.product(*vals)
        ret = []
        ret_maps = []
        for v in vals:
            if remove_duplicates and len(v) != len(set(v)):
                continue
            mapping = dict(zip(keys, v))
            ret.append(recursive_format(templates, mapping))
            ret_maps.append(mapping)
        if return_meta:
            return ret, ret_maps
        return ret
