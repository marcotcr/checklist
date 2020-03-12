import numpy as np
import itertools

def iter_with_optional(data, preds, confs, labels, meta):
    if type(meta) != list or len(meta) != len(data):
        meta = itertools.repeat(meta)
    if type(labels) not in [list, np.array]:
        labels = itertools.repeat(labels)
    else:
        if len(labels) != len(data):
            raise(Exception('If labels is list, length must match data'))
    return zip(data, preds, confs, labels, meta)


class Expect:
    @staticmethod
    # TODO: add confidences?
    def wrap(fn):
        # fn must take (x, pred, conf, labels=None, meta=None),
        # x: single example or group of examples
        # pred: single prediction or group of predictions
        # label: single label
        # Must return True or False
        def expect(self):
            zipped = iter_with_optional(self.data, self.results.preds, self.results.confs, self.labels, self.meta)
            return np.array([fn(x, pred, confs, labels, meta) for x, pred, confs, labels, meta in zipped])
        # return np.array([fn(x, pred, conf, label, meta) for x, pred, conf, label, meta in iter_with_optional(data, preds, confs, labels, meta)])
        return expect

    @staticmethod
    def single_to_group(fn):
        # fn must take (x, pred, conf, label=None, meta=None),
        # x: single example
        # pred: single prediction
        # conf: single conf
        # label: single label
        # Must return True or False
        def expect(xs, preds, confs, label=None, meta=None):
            return np.array([fn(x, p, c, l, m) for x, p, c,  l, m in iter_with_optional(xs, preds, confs, label, meta)])
        return expect

    @staticmethod
    def all(fn, ignore_first=False):
        # fn must take (xs, preds, confs, labels=None, meta=None),
        # xs:list of examples
        # preds: predictions
        # confs: confs
        # labels: labels
        # Must return np.array of True or False
        def expect(xs, preds, confs, labels=None, meta=None):
            r = fn(xs, preds, confs, labels, meta)
            if ignore_first:
                r = r[1:]
            return np.all(r)
        return expect

    @staticmethod
    def eq(x, pred, conf, label=None, meta=None):
        return pred == label

    @staticmethod
    def pairwise_to_group(fn):
        # fn takes (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
        # assuming first example is orig
        def expect(xs, preds, confs, labels=None, meta=None):
            orig_pred = preds[0]
            orig_conf = confs[0]
            return np.array([fn(orig_pred, p, orig_conf, c, l, m) for _, p, c, l, m in iter_with_optional(xs, preds, confs, labels, meta)] )
        return expect

    @staticmethod
    def inv(tolerance=0):
        def expect(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            softmax = type(orig_conf) in [np.array, np.ndarray]
            if pred == orig_pred:
                return True
            if tolerance == 0:
                return False
            if softmax:
                orig_conf = orig_conf[orig_pred]
                conf = conf[orig_pred]
                return np.abs(conf - orig_conf) <= tolerance
            else:
                # This is being generous I think
                return conf + orig_conf <= tolerance
        return expect

    @staticmethod
    def monotonic_label(label, increasing=True, tolerance=0.):
        def expect(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            softmax = type(orig_conf) in [np.array, np.ndarray]
            if not softmax:
                raise(Exception('Need prediction function to be softmax for monotonic_label'))
            orig_conf = orig_conf[label]
            conf = conf[label]
            if increasing:
                return conf + tolerance >= orig_conf
            else:
                return conf - tolerance <= orig_conf
        return expect
