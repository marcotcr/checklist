from .abstract_test import AbstractTest
from .expect import Expect, iter_with_optional
import numpy as np

def pairwise_print_fn(fail_criterion, sort_criterion):
    # fail_criterion takes (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
    # sort_criterion takes (orig_pred, pred, orig_conf, conf, labels=None, meta=None), returns a value
    # sort criterion takes (xs, preds, confs, labels=None, meta=None)
    def print_fn(xs, preds, confs, labels=None, meta=None, format_example_fn=None):
        orig = preds[0]
        orig_conf = confs[0]
        softmax = type(confs[0]) in [np.array, np.ndarray]
        fails = np.array([fail_criterion(orig, p, orig_conf, c, l, m) for _, p, c, l, m in iter_with_optional(xs, preds, confs, labels, meta)] )
        fails = np.where(fails == True)[0]
        sort_values = np.array([sort_criterion(orig, p, orig_conf, c, l, m) for _, p, c, l, m in iter_with_optional(xs, preds, confs, labels, meta)] )
        fails = sorted(fails, key=lambda x:sort_values[x])
        binary = False
        if softmax:
            if orig_conf.shape[0] == 2:
                confs = confs[:, 1]
                binary = True
            else:
                confs = confs[:, orig]
        if 0 in fails:
            fails.remove(0)
        for f in [0] + fails[:2]:
            label = None if labels is None else labels[f]
            metaz = None if meta is None else meta[f]
            print(format_example_fn(xs[f], preds[f], confs[f], label, metaz))
        print()
    return print_fn
class Inv(AbstractTest):
    def __init__(self, data, expect=None, threshold=0.1, meta=None):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta
        if expect is None:
            self.expect = Expect.pairwise(Expect.inv(threshold))
        def fail_cr(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            return orig_pred != pred
        def sort_cr(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            softmax = type(orig_conf) in [np.array, np.ndarray]
            if softmax:
                orig_conf = orig_conf[orig_pred]
                conf = conf[orig_pred]
            return np.abs(conf - orig_conf)
        self.print = pairwise_print_fn(fail_cr, sort_cr)

    # def print(self, xs, preds, confs, labels=None, meta=None, format_example_fn=None):
    #     orig = preds[0]
    #     orig_conf = confs[0]
    #     softmax = type(confs[0]) in [np.array, np.ndarray]
    #     binary = False
    #     if softmax:
    #         if orig_conf.shape[0] == 2:
    #             confs = confs[:, 1]
    #             binary = True
    #         else:
    #             confs = confs[:, orig]
    #         orig_conf = confs[0]
    #         conf_dist = np.abs(confs - orig_conf)
    #     else:
    #         conf_dist = confs
    #     fails = np.where(preds != orig)[0]
    #     fails = sorted(fails, key=lambda x:conf_dist[x], reverse=True)
    #     for f in [0] + fails[:2]:
    #         if binary:
    #             print('%.1f %s' % (confs[f], format_example_fn(xs[f])))
    #         else:
    #             print('%s (%.1f) %s' % (preds[f], confs[f], format_example_fn(xs[f])))
    #     print()


class Dir(AbstractTest):
    def __init__(self, data, expect, meta=None):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta

    def set_monotonic_print(self, label=None, increasing=True):
        def get_conf(conf, orig, pred):
            softmax = type(conf) in [np.array, np.ndarray]
            if softmax:
                return conf[orig] if label is None else conf[label]
            else:
                return conf if orig == pred else -conf
        def fail_cr(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            orig_conf = get_conf(orig_conf, orig_pred, orig_pred)
            conf = get_conf(conf, orig_pred, pred)
            # print(orig_conf, conf)
            return conf < orig_conf if increasing else conf > orig_conf
        def sort_cr(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            orig_conf = get_conf(orig_conf, orig_pred, orig_pred)
            conf = get_conf(conf, orig_pred, pred)
            return conf if increasing else -conf
        self.print = pairwise_print_fn(fail_cr, sort_cr)


        # def print_fn(xs, preds, confs, labels=None, meta=None, format_example_fn=None):
        #     orig = preds[0]
        #     orig_conf = confs[0]
        #     softmax = type(confs[0]) in [np.array, np.ndarray]
        #     binary = False
        #     if softmax:
        #         if orig_conf.shape[0] == 2:
        #             binary = True
        #         if label == None:
        #             confs = confs[:, orig]
        #         else:
        #             confs = confs[:, label]
        #         orig_conf = confs[0]
        #     nconfs = confs.copy()
        #     if not softmax:
        #         nconfs[preds != orig] = -nconfs[preds != orig]
        #     fails = np.where(confs < orig_conf)[0] if increasing else np.where(confs > orig_conf)[0]
        #     fails = sorted(fails, key=lambda x:nconfs[x], reverse=(not increasing))
        #     for f in [0] + fails[:2]:
        #         if binary:
        #             print('%.1f %s' % (confs[f], format_example_fn(xs[f])))
        #         else:
        #             print('%s (%.1f) %s' % (preds[f], confs[f], format_example_fn(xs[f])))
        #     print()
        # self.print = print_fn


# expect(data, labels=None, meta=None)
