from abc import ABC, abstractmethod
from munch import Munch
import pickle
import numpy as np

class AbstractTest(ABC):
    def __init__(self):
        self.preds = None
        self.labels = None
        self.meta = None
        self.confs = None
    def save(self):
        pass

    def load(self):
        pass

    def set_expect(self, expect):
        self.expect = expect
        self.update_expect()

    def update_expect(self):
        if hasattr(self, 'results') and self.results:
            self.results.passed = self.expect(self)
        else:
            raise(Exception('No results. Run run() first'))

    def run(self, predict_and_confidence_fn, overwrite=False):
        if hasattr(self, 'results') and self.results and not overwrite:
            raise(Exception('Results exist. To overwrite, set overwrite=True'))

        self.results = Munch()
        if type(self.data[0]) == list:
            all = [(i, y) for i, x in enumerate(self.data) for y in x]
            result_indexes, examples = map(list, list(zip(*all)))
        else:
            examples = self.data
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
