from .abstract_test import AbstractTest, default_format_example
from .expect import Expect
import numpy as np

class MFT(AbstractTest):
    def __init__(self, data, expect=None, labels=None, meta=None, agg_fn='all',
                 templates=None, name=None, capability=None, description=None):
        """Minimum Functionality Test

        Parameters
        ----------
        data : list
            List or list(lists) of whatever the model takes as input. Strings, tuples, etc.
        expect : function
            Expectation function, takes an AbstractTest (self) as parameter
            see expect.py for details
        labels : single value (int, str, etc) or list
            If list, must be the same length as data
        meta : list
            metadata for examples, must be the same length as data
        agg_fn : function, or string in ['all', 'all_except_first']
            Aggregation function for expect function, if each element in data is a list.
            Takes as input a numpy array, outputs a boolean.
        templates : list(tuple)
            Parameters used to generate the data. Use ret.templates from editor.template
        name : str
            test name
        capability : str
            test capability
        description : str
            test description
        """
        if labels is None and expect is None:
            raise(Exception('Must specify either \'expect\' or \'labels\''))
        if labels is not None and expect is None:
            expect = Expect.eq()
        super().__init__(data, expect, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, print_first=False, name=name,
                         capability=capability, description=description)

class INV(AbstractTest):
    def __init__(self, data, expect=None, threshold=0.1, meta=None,
                 agg_fn='all_except_first', templates=None, name=None,
                 capability=None, description=None, labels=None):
        """Invariance Test

        Parameters
        ----------
        data : list
            List or list(lists) of whatever the model takes as input. Strings, tuples, etc.
        expect : function
            Expectation function, takes an AbstractTest (self) as parameter
            see expect.py for details. If None, will be Invariance with threshold
        threshold : float
            Prediction probability threshold for invariance. Will consider
            pairs invariant even if prediction is the same when difference in
            probability is smaller than threshold.
        meta : list
            metadata for examples, must be the same length as data
        agg_fn : function, or string in ['all', 'all_except_first']
            Aggregation function for expect function, if each element in data is a list.
            Takes as input a numpy array, outputs a boolean.
        templates : list(tuple)
            Parameters used to generate the data. Use ret.templates from editor.template
        name : str
            test name
        capability : str
            test capability
        description : str
            test description
        labels : single value (int, str, etc) or list
            If list, must be the same length as data
        """
        if expect is None:
            expect = Expect.inv(threshold)
        super().__init__(data, expect, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, print_first=True, name=name,
                         capability=capability, description=description)

class DIR(AbstractTest):
    def __init__(self, data, expect, meta=None, agg_fn='all_except_first',
                 templates=None, name=None, labels=None, capability=None, description=None):
        """Directional Expectation Test

        Parameters
        ----------
        data : list
            List or list(lists) of whatever the model takes as input. Strings, tuples, etc.
        expect : function
            Expectation function, takes an AbstractTest (self) as parameter
            see expect.py for details.
        meta : list
            metadata for examples, must be the same length as data
        agg_fn : function, or string in ['all', 'all_except_first']
            Aggregation function for expect function, if each element in data is a list.
            Takes as input a numpy array, outputs a boolean.
        templates : list(tuple)
            Parameters used to generate the data. Use ret.templates from editor.template
        name : str
            test name
        labels : single value (int, str, etc) or list
            If list, must be the same length as data
        capability : str
            test capability
        description : str
            test description
        """
        super().__init__(data, expect, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, print_first=True, name=name,
                         capability=capability, description=description)

class GroupEquality(MFT):
    def __init__(self, data, measure_fn, group_fn, labels=None, meta=None, agg_fn='all',
                 templates=None, name=None, capability=None, description=None):
        """
        TODO
        both group_fn and measure_fn are expect fns? seems cleaner
        """
        self.group_fn = group_fn
        super().__init__(data, measure_fn, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, name=name,
                         capability=capability, description=description)
    def summary(self, n=3, print_fn=None, format_example_fn=None, n_per_testcase=3, group_measure_fn=None, group_print_fn=None):
        if group_measure_fn is None:
            group_measure_fn = lambda x: (x.mean(), x.std())
        if group_print_fn is None:
            group_print_fn = lambda v, g: print('%.3f +- %.2f %s' % (v[0], v[1], g))
        self._check_results()
        all_groups = set([x for y in self.results.groups for x in y])
        group_results = {}
        max_len = max([len(x) for x in self.results.groups])
        groups = np.array([np.pad(x, (0, max_len - len(x)), 'constant', constant_values=None) for x in self.results.groups])
        # return groups
        results = np.array([np.pad(x, (0, max_len - len(x)), 'constant') for x in self.results.expect_results])
        # results = np.array(self.results.expect_results)
        # return groups, results
        for g in all_groups:
            r = results[groups==g]
            group_results[g] = group_measure_fn(r)
        print('Average measurement per group:')
        for g, v in sorted(group_results.items(), key=lambda x:x[1]):
            group_print_fn(v, g)

        if not n:
            return
        if print_fn is None:
            print_fn = self.print
        if format_example_fn is None:
            format_example_fn = default_format_example
        d_idx = 3
        diffs = []
        # compute max difference per testcase
        for group, r in zip(groups, results):
            max_r = -1000000000
            min_r = 10000000000
            for g in set(group):
                tr = group_measure_fn(r[group == g])[0]
                max_r = max(tr, max_r)
                min_r = min(tr, min_r)
            diffs.append(max_r - min_r)
        top_percentile = np.argsort(diffs)[int(len(diffs) * .9)-1:]
        fails = np.random.choice(top_percentile, min(len(top_percentile), n), replace=False)
        # fails = np.random.choice(range(len(results)), min(results.shape[0], n), replace=False)
        print()
        print('Examples:')
        for f in fails:
            d_idx = f if self.run_idxs is None else self.run_idxs[f]
            # should be format_fn
            label, meta = self._label_meta(d_idx)
            # print(label, meta)
            print_fn(self.data[d_idx], self.results.preds[d_idx],
                     self.results.confs[d_idx], -self.results.expect_results[f],
                     label, meta, format_example_fn, nsamples=n_per_testcase, only_include_fail=False)

    def update_expect(self):
        self._check_results()
        self.results.expect_results = self.expect(self)
        self.results.groups = self.group_fn(self)
