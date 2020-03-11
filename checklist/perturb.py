import numpy as np
class Perturb:
    @staticmethod
    def perturb(data, perturb_fn, keep_original=True):
        ret = []
        for d in data:
            t = []
            if keep_original:
                t.append(d)
            p = perturb_fn(d)
            if type(p) in [np.array, list]:
                t.extend(p)
            else:
                t.append(p)
            ret.append(t)
        return ret
