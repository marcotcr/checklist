from abc import ABC, abstractmethod
from munch import Munch
import pickle
import numpy as np
from .expect import iter_with_optional

class AbstractTest(ABC):
    def __init__(self):
        self.data = None
        self.labels = None
        self.meta = None
    def save(self):
        pass

    def load(self):
        pass

    def print(self, xs, preds, confs, labels=None, meta=None, format_example_fn=None):
        iters = list(iter_with_optional(xs, preds, confs, labels, meta))
        idxs = list(range(min(len(iters), 3)))
        if type(xs) in [list, np.array]:
            if labels:
                idxs = np.where(np.array(preds) != np.array(labels))[0][:3]
        iters = [iters[i] for i in idxs]
        for x, pred, conf, label, meta in iters:
            print(format_example_fn(x, pred, conf, label, meta))
        if type(preds) in [np.array, np.ndarray, list] and len(preds) > 1:
            print()
        print('----')


    def check_results(self):
        if not hasattr(self, 'results') or not self.results:
            raise(Exception('No results. Run run() first'))

    def set_expect(self, expect):
        self.expect = expect
        self.update_expect()

    def update_expect(self):
        self.check_results()
        self.results.passed = self.expect(self)

    def run(self, predict_and_confidence_fn, overwrite=False):
        if hasattr(self, 'results') and self.results and not overwrite:
            raise(Exception('Results exist. To overwrite, set overwrite=True'))

        self.results = Munch()
        if type(self.data[0]) == list:
            all = [(i, y) for i, x in enumerate(self.data) for y in x]
            result_indexes, examples = map(list, list(zip(*all)))
        else:
            examples = self.data
        print('Predicting %d examples' % len(examples))
        preds, confs = predict_and_confidence_fn(examples)
        if type(self.data[0]) == list:
            self.results.preds = [[] for _ in self.data]
            self.results.confs  = [[] for _ in self.data]
            for i, p, c in zip(result_indexes, preds, confs):
                self.results.preds[i].append(p)
                self.results.confs[i].append(c)
            for i in range(len(self.results.preds)):
                self.results.preds[i] = np.array(self.results.preds[i])
                self.results.confs[i] = np.array(self.results.confs[i])
        else:
            self.results.preds = preds
            self.results.confs = confs
        self.update_expect()

    def fail_idxs(self):
        self.check_results()
        return np.where(self.results.passed == False)[0]

    def filtered_idxs(self):
        self.check_results()
        return np.where(self.results.passed == None)[0]

    def print_stats(self):
        self.check_results()
        n = len(self.data)
        fails = self.fail_idxs().shape[0]
        filtered = self.filtered_idxs().shape[0]
        nonfiltered = n - filtered
        print('Test cases:      %d' % n)
        if filtered:
            print('After filtering: %d (%.1f%%)' % (nonfiltered, 100 * nonfiltered / n))
        print('Fails (rate):    %d (%.1f%%)' % (fails, 100 * fails / nonfiltered))

    def label_meta(self, i):
        if self.labels is None:
            label = None
        else:
            label = self.labels if type(self.labels) not in [list, np.array] else self.labels[i]
        if self.meta is None:
            meta = None
        else:
            meta = self.meta if type(self.meta) not in [list, np.array] else self.meta[i]
        return label, meta

    def summary(self, n=None, print_fn=None, format_example_fn=None):
        # print_fn_fn takes (xs, preds, confs, labels=None, meta=None)
        # format_example_fn takes (x, pred, conf, label=None, meta=None)
        # i.e. it prints a single test case
        self.print_stats()
        if n is None:
            return
        if print_fn is None:
            print_fn = self.print
        def default_format_example(x, pred, conf, *args, **kwargs):
            softmax = type(conf) in [np.array, np.ndarray]
            binary = False
            if softmax:
                if conf.shape[0] == 2:
                    binary = True
                    conf = conf[1]
                else:
                    conf = conf[pred]
            if binary:
                return '%.1f %s' % (conf, str(x))
            else:
                return '%s (%.1f) %s' % (pred, conf, str(x))

        if format_example_fn is None:
            format_example_fn = default_format_example
        fails = self.fail_idxs()
        if fails.shape[0] == 0:
            return
        print()
        print('Example fails:')
        fails = np.random.choice(fails, min(fails.shape[0], n), replace=False)
        for f in fails:
            # should be format_fn
            label, meta = self.label_meta(f)
            # print(label, meta)
            print_fn(self.data[f], self.results.preds[f], self.results.confs[f], label, meta, format_example_fn)
