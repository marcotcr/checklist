import numpy as np
class Perturb:
    @staticmethod
    def perturb(data, perturb_fn, keep_original=True, meta=None, returns_additional=False):
        ret = []
        ret_add = []
        for d in data:
            t = []
            add = []
            if keep_original:
                tp = type(d)
                if tp in [list, np.array, tuple]:
                    org = tp([str(x) for x in d])
                else:
                    org = str(d)
                t.append(org)
                add.append({})
            p = perturb_fn(d)
            a = []
            x = []
            if not p:
                continue
            if returns_additional:
                p, a = p
            if type(p) in [np.array, list]:
                t.extend(p)
                add.extend(a)
            else:
                t.append(p)
                add.append(a)
            ret.append(t)
            ret_add.append(add)
        if returns_additional:
            return ret, ret_add
        return ret
