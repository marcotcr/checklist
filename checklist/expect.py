import numpy as np
import itertools

def iter_with_optional(data, preds, confs, labels, meta):
    # If this is a single example
    if type(data) not in [list, np.array]:
        return [(data, preds, confs, labels, meta)]
    if type(meta) not in [list, np.array]:
        meta = itertools.repeat(meta)
    else:
        if len(meta) != len(data):
            raise(Exception('If meta is list, length must match data'))
    if type(labels) not in [list, np.array]:
        labels = itertools.repeat(labels)
    else:
        if len(labels) != len(data):
            raise(Exception('If labels is list, length must match data'))
    return zip(data, preds, confs, labels, meta)



class Expect:
    @staticmethod
    def test(fn):
        # fn must take (data, preds, confs, labels=None, meta=None)
        # returns list of lists or list of np.arrays, representing results for
        # examples inside a testcase
        # each list must be of np.array of integers, bools or None, where:
        #    > 0 means passed,
        #    <= 0 or False means fail, and (optionally) the magnitude of the
        #      failure, indicated by distance from 0, e.g. -10 is worse than -1
        #    None means the test does not apply, and this should not be counted
        def expect(self):
            return fn(self.data, self.results.preds, self.results.confs, self.labels, self.meta)
        return expect

    @staticmethod
    def testcase(fn):
        # fn must take (x, pred, conf, labels=None, meta=None),
        # x: single example or group of examples
        # pred: single prediction or group of predictions
        # label: single label
        # Returns:
        # list of np.array of integers, bools or None, where:
        #    > 0 means passed,
        #    <= 0 or False means fail, and (optionally) the magnitude of the
        #      failure, indicated by distance from 0, e.g. -10 is worse than -1
        #    None means the test does not apply, and this should not be counted
        def expect(self):
            zipped = iter_with_optional(self.data, self.results.preds, self.results.confs, self.labels, self.meta)
            return [fn(x, pred, confs, labels, meta) for x, pred, confs, labels, meta in zipped]
        # return np.array([fn(x, pred, conf, label, meta) for x, pred, conf, label, meta in iter_with_optional(data, preds, confs, labels, meta)])
        return expect


    @staticmethod
    def aggregate(data, agg_fn='all'):
        # data is a list of lists or list of np.arrays
        return np.array([Expect.aggregate_testcase(x, agg_fn) for x in data])

    @staticmethod
    def aggregate_testcase(expect_results, agg_fn='all'):
        if agg_fn == 'all':
            agg_fn = Expect.all()
        if agg_fn == 'all_except_first':
            agg_fn = Expect.all(ignore_first=True)
        if expect_results is None:
            return None
        r = [x for x in expect_results if x is not None]
        if not r:
            return None
        else:
            return agg_fn(np.array(r))

    @staticmethod
    def aggregate_and_wrap(individual_expect_fn, agg_fn='all'):
        """
        individual_expect_fn acts on a test case, i.e:
            input: (xs, preds, confs, labels=None, meta=None)
            output: np.array of True, False, or None
        agg_fn acts on the output of individual_expect_fn and aggregates it into a single True, False or None, i.e.:
            input: np.array of True, False, or None
            output: True, False, or None
        can take string value of 'all'
        if individual_expect_fn returns a few Nones, they are removed. If it returns all Nones, the return is None independent of agg_fn
        """
        save_agg_fn = agg_fn
        def expectz(xs, preds, confs, labels=None, meta=None):
            agg_fn = save_agg_fn
            r = individual_expect_fn(xs, preds, confs, labels, meta)
            if agg_fn == 'all':
                agg_fn = Expect.all()
            r = [x for x in r if x is not None]
            if not r:
                return None
            return agg_fn(np.array(r))
        return Expect.testcase(expectz)

    @staticmethod
    def single(fn):
        # fn must take (x, pred, conf, label=None, meta=None),
        # x: single example
        # pred: single prediction
        # conf: single conf
        # label: single label
        # Must return float or bool, where:
        #    > 0 means passed,
        #    <= 0 or False means fail, and (optionally) the magnitude of the
        #      failure, indicated by distance from 0, e.g. -10 is worse than -1
        #    None means the test does not apply, and this should not be counted
        def expect_fn(xs, preds, confs, label=None, meta=None):
            return np.array([fn(x, p, c, l, m) for x, p, c,  l, m in iter_with_optional(xs, preds, confs, label, meta)])
        return Expect.testcase(expect_fn)#, agg_fn)

    @staticmethod
    def pairwise(fn):
        # fn takes (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
        # assuming first example is orig
        # Must return float or bool, where:
        #    > 0 means passed,
        #    <= 0 or False means fail, and (optionally) the magnitude of the
        #      failure, indicated by distance from 0, e.g. -10 is worse than -1
        #    None means the test does not apply, and this should not be counted
        def expect_fn(xs, preds, confs, labels=None, meta=None):
            orig_pred = preds[0]
            orig_conf = confs[0]
            return np.array([fn(orig_pred, p, orig_conf, c, l, m) for _, p, c, l, m in iter_with_optional(xs, preds, confs, labels, meta)] )
        # if agg_fn == 'all':
        #     agg_fn = Expect.all(ignore_first=True)
        return Expect.testcase(expect_fn)#, agg_fn)

    @staticmethod
    def wrap_slice(expect_fn, slice_fn, agg_fn='all'):
        def wrapped(*args, **kwargs):
            ret = expect_fn(*args, **kwargs)
            sliced = Expect.aggregate(slice_fn(*args, **kwargs), agg_fn)
            for i in np.where(sliced != True)[0]:
                if type(ret[i]) in [list, np.array]:
                    ret[i] = [None for _ in ret[i]]
                else:
                    ret[i] = None
            return ret
        return wrapped


    @staticmethod
    def slice_testcase(expect_fn, slice_fn, agg_fn='all'):
        # expect_fn takes a Test object (this is a wrapper on top)
        # slice_fn must take (x, pred, conf, labels=None, meta=None),
        # x: single example or group of examples
        # pred: single prediction or group of predictions
        # label: single label
        # Must return True or False, will slice out (None) whatever is not True
        wrapped_slice = Expect.testcase(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def slice_single(expect_fn, slice_fn, agg_fn='all'):
        # fn must take (x, pred, conf, label=None, meta=None),
        # x: single example
        # pred: single prediction
        # conf: single conf
        # label: single label
        # Must return True, False, or None (does not apply)
        # agg: how to aggregate the results, e.g. if you get [True, False, True]
        # options: 'all', or a function that takes in (xs, preds, confs, labels=None, meta=None) and returns True, False or None
        wrapped_slice = Expect.single(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def slice_orig(expect_fn, slice_fn, agg_fn='all'):
        # slice_fn takes (orig_pred, orig_conf)
        new_fn = lambda orig, pred, *args, **kwargs: slice_fn(orig, pred)
        return Expect.slice_pairwise(expect_fn, new_fn, agg_fn)


    @staticmethod
    def slice_pairwise(expect_fn, slice_fn, agg_fn='all_except_first'):
        # slice_fn takes (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
        # assuming first example is orig
        # must return True, False or None
        # agg: how to aggregate the results, e.g. if you get [True, False, True]
        # options: 'all', or a function that takes in (xs, preds, confs, labels=None, meta=None) and returns True, False or None
        wrapped_slice = Expect.pairwise(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def all(ignore_first=False):
        def tmp_fn(results):
            # results: np.array of float or bool, where
            #    > 0 means passed,
            #    <= 0 or False means fail, and (optionally) the magnitude of the
            #      failure, indicated by distance from 0, e.g. -10 is worse than -1
            #    None means the test does not apply, and this should not be counted
            if ignore_first:
                results = results[1:]
            return np.all(results > 0)
        return tmp_fn
        # def expect(xs, preds, confs, labels=None, meta=None):
        #     r = fn(xs, preds, confs, labels, meta)
        #     if ignore_first:
        #         r = r[1:]
        #     return np.all(r)
        # return expect

    @staticmethod
    def eq(val=None):
        # If val is None, check label
        def ret_fn(x, pred, conf, label=None, meta=None):
            gt = val if val is not None else label
            softmax = type(conf) in [np.array, np.ndarray]
            conf = conf[gt] if softmax else -conf
            conf_viol = -(1 - conf)
            if pred == gt:
                return True
            else:
                return conf_viol
        return Expect.single(ret_fn)

    @staticmethod
    def inv(tolerance=0):
        def expect(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            softmax = type(orig_conf) in [np.array, np.ndarray]
            if pred == orig_pred:
                return True
            if softmax:
                orig_conf = orig_conf[orig_pred]
                conf = conf[orig_pred]
                if np.abs(conf - orig_conf) <= tolerance:
                    return True
                else:
                    return -np.abs(conf - orig_conf)
            else:
                # This is being generous I think
                if conf + orig_conf <= tolerance:
                    return True
                else:
                    return -(conf + orig_conf)
        return Expect.pairwise(expect)

    @staticmethod
    def monotonic(label=None, increasing=True, tolerance=0.):
        keep_label = label
        def expect(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            label = keep_label
            softmax = type(orig_conf) in [np.array, np.ndarray]
            if not softmax and label is not None:
                raise(Exception('Need prediction function to be softmax for monotonic if you specify label'))
            if label is None:
                label = orig_pred
            if softmax:
                orig_conf = orig_conf[label]
                conf = conf[label]
                conf_diff = conf - orig_conf
            else:
                if pred == orig_pred:
                    conf_diff = conf - orig_conf
                else:
                    conf_diff = orig_conf + conf
            # can't fail
            if increasing and orig_conf <= tolerance:
                return None
            if not increasing and orig_conf >= 1 - tolerance:
                return None

            if increasing:
                if conf_diff + tolerance >= 0:
                    return True
                else:
                    return conf_diff + tolerance
                # return conf + tolerance >= orig_conf
            else:
                if conf_diff - tolerance <= 0:
                    return True
                else:
                    return -(conf_diff - tolerance)
                # return conf - tolerance <= orig_conf
        return Expect.pairwise(expect)
