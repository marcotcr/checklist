import numpy as np
import itertools

def iter_with_optional(data, preds, confs, labels, meta, idxs=None):
    # If this is a single example
    if type(data) not in [list, np.array, np.ndarray]:
        return [(data, preds, confs, labels, meta)]
    if type(meta) not in [list, np.array, np.ndarray]:
        meta = itertools.repeat(meta)
    else:
        if len(meta) != len(data):
            raise(Exception('If meta is list, length must match data'))
    if type(labels) not in [list, np.array, np.ndarray]:
        labels = itertools.repeat(labels)
    else:
        if len(labels) != len(data):
            raise(Exception('If labels is list, length must match data'))
    ret = zip(data, preds, confs, labels, meta)
    if idxs is not None:
        ret = list(ret)
        ret = [ret[i] for i in idxs]
    return ret



class Expect:
    """Helpers for writing expectation functions over tests.
    Each test has a list of testcases, and each testcase has a list of examples.
    Expectation function will act on whole tests, testcases, individual examples, or pairs of examples.
    In any of these, the output of an expectation function for a single example
    is an integer, float, bool, or None, where:
        > 0 (or True) means passed,
        <= 0 or False means fail, and (optionally) the magnitude of the
          failure, indicated by distance from 0, e.g. -10 is worse than -1
        None means the test does not apply, and this should not be counted
    """
    @staticmethod
    def test(fn):
        """Expectation over a whole test

        Parameters
        ----------
        fn : function
            Arguments: (data, preds, confs, labels=None, meta=None), all of
            which are potentially lists of lists
            Returns: list of np.arrays, representing results for
             examples inside a testcase. See docstring for the Expect class
             for what different values in the output mean.
        Returns
        -------
        function
            Arguments: AbstractTest
            Returns: List of np.arrays
        """
        def expect(self):
            return fn(self.data, self.results.preds, self.results.confs, self.labels, self.meta, self.run_idxs)
        return expect

    @staticmethod
    def testcase(fn):
        """Expectation over a single testcase (may have multiple examples)

        Parameters
        ----------
        fn : function
            Arguments: (xs, preds, confs, labels=None, meta=None)
            Returns: np.array, representing results for the examples inside the
            testcase. See docstring for the Expect class for what different
            values in the output mean.
        Returns
        -------
        function
            Arguments: AbstractTest
            Returns: List of np.arrays
        """
        def expect(self):
            zipped = iter_with_optional(self.data, self.results.preds, self.results.confs, self.labels, self.meta, self.run_idxs)
            return [fn(x, pred, confs, labels, meta) for x, pred, confs, labels, meta in zipped]
        return expect

    @staticmethod
    def single(fn):
        """Expectation over a single example

        Parameters
        ----------
        fn : function
            Arguments: (x, pred, conf, label=None, meta=None)
            Returns: bool, float, or int. See docstring for the Expect class
            for what different values in the output mean.
        Returns
        -------
        function
            Arguments: AbstractTest
            Returns: List of np.arrays
        """
        def expect_fn(xs, preds, confs, label=None, meta=None):
            return np.array([fn(x, p, c, l, m) for x, p, c,  l, m in iter_with_optional(xs, preds, confs, label, meta)])
        return Expect.testcase(expect_fn)#, agg_fn)

    @staticmethod
    def pairwise(fn):
        """Expectation over pairs of examples, suitable for perturbation tests

        Parameters
        ----------
        fn : function
            Arguments: (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
                Orig_pred and orig_conf are the prediction and the confidence
                of the first example in the test case
            Returns: bool, float, or int. See docstring for the Expect class
            for what different values in the output mean.
        Returns
        -------
        function
            Arguments: AbstractTest
            Returns: List of np.arrays
        """
        def expect_fn(xs, preds, confs, labels=None, meta=None):
            orig_pred = preds[0]
            orig_conf = confs[0]
            return np.array([fn(orig_pred, p, orig_conf, c, l, m) for _, p, c, l, m in iter_with_optional(xs, preds, confs, labels, meta)] )
        return Expect.testcase(expect_fn)


    @staticmethod
    def aggregate(data, agg_fn='all'):
        """aggregates expectation results for all examples in each test case

        Parameters
        ----------
        data : type
            list of np.arrays
        agg_fn : function or string in 'all', 'all_except_first'
            Arguments: np.array
            Returns: bool, float, or int. See docstring for the Expect class
            for what different values in the output mean.

        Returns
        -------
        np.array
            Of bool, float, or int. See docstring for the Expect class
            for what different values in the output mean.
        """
        # data is a list of lists or list of np.arrays
        return np.array([Expect.aggregate_testcase(x, agg_fn) for x in data])

    @staticmethod
    def aggregate_testcase(expect_results, agg_fn='all'):
        """See docstring for aggregate"""
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
    def all(ignore_first=False):
        """Aggregate such that all have to be True
        See docstring for "aggregate", this is an aggregation function

        Parameters
        ----------
        ignore_first : bool
            If True, do not require first example to be True (useful for perturbation tests)

        Returns
        -------
        function
            aggregation function

        """
        def tmp_fn(results):
            if ignore_first:
                results = results[1:]
            return np.all(results > 0)
        return tmp_fn

    @staticmethod
    def wrap_slice(expect_fn, slice_fn, agg_fn='all'):
        """Wraps an expectation function with a slice function to discard certain testcases.

        Parameters
        ----------
        expect_fn : function
            an expectation function
        slice_fn : function
            A slice function, slices testcases.
            Arguments: the same as the expectation function
            Returns: np.array where True means 'keep' and False means 'discard'
        agg_fn : function
            Aggregates examples within a test case. See aggregate_testcase

        Returns
        -------
        function
            The expect function, but now returning None for discarded examples

        """
        def wrapped(*args, **kwargs):
            ret = expect_fn(*args, **kwargs)
            sliced = Expect.aggregate(slice_fn(*args, **kwargs), agg_fn)
            for i in np.where(sliced != True)[0]:
                if type(ret[i]) in [list, np.array, np.ndarray]:
                    ret[i] = [None for _ in ret[i]]
                else:
                    ret[i] = None
            return ret
        return wrapped


    @staticmethod
    def slice_testcase(expect_fn, slice_fn, agg_fn='all'):
        """Wraps an expectation function with a slice function to discard certain testcases.
        Slice function acts on testcase.

        Parameters
        ----------
        expect_fn : function
            an expectation function, where argument is a Test
        slice_fn : function
            A slice function, slices testcases.
            Arguments: (xs, preds, confs, labels=None, meta=None)
            Returns: np.array where True means 'keep' and False means 'discard'
        agg_fn : function
            Aggregates examples within a test case. See aggregate_testcase

        Returns
        -------
        function
            The expect function, but now returning None for discarded examples

        """
        wrapped_slice = Expect.testcase(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def slice_single(expect_fn, slice_fn, agg_fn='all'):
        """Wraps an expectation function with a slice function to discard certain testcases.
        Slice function acts on single examples.

        Parameters
        ----------
        expect_fn : function
            an expectation function, where argument is a Test
        slice_fn : function
            A slice function, slices testcases.
            Arguments: (x, pred, conf, label=None, meta=None)
            Returns: True ('keep') or False ('discard')
        agg_fn : function
            Aggregates examples within a test case. See aggregate_testcase

        Returns
        -------
        function
            The expect function, but now returning None for discarded examples

        """

        wrapped_slice = Expect.single(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def slice_orig(expect_fn, slice_fn, agg_fn='all'):
        """Wraps an expectation function with a slice function to discard certain testcases.
        Slice function acts on the original example in a perturbation test.

        Parameters
        ----------
        expect_fn : function
            an expectation function, where argument is a Test
        slice_fn : function
            A slice function, slices original examples for perturbation tests.
            Arguments: (orig_pred, orig_conf)
            Returns: True ('keep') or False ('discard')
        agg_fn : function
            Aggregates examples within a test case. See aggregate_testcase

        Returns
        -------
        function
            The expect function, but now returning None for discarded examples

        """
        new_fn = lambda orig, pred, *args, **kwargs: slice_fn(orig, pred)
        return Expect.slice_pairwise(expect_fn, new_fn, agg_fn)


    @staticmethod
    def slice_pairwise(expect_fn, slice_fn, agg_fn='all_except_first'):
        """Wraps an expectation function with a slice function to discard certain testcases.
        Slice function acts on pairs.

        Parameters
        ----------
        expect_fn : function
            an expectation function, where argument is a Test
        slice_fn : function
            A slice function, slices testcases.
            Arguments: (orig_pred, pred, orig_conf, conf, labels=None, meta=None)
            Returns: np.array where True means 'keep' and False means 'discard'
        agg_fn : function
            Aggregates examples within a test case. See aggregate_testcase

        Returns
        -------
        function
            The expect function, but now returning None for discarded examples

        """
        wrapped_slice = Expect.pairwise(slice_fn)
        return Expect.wrap_slice(expect_fn, wrapped_slice, agg_fn)

    @staticmethod
    def combine(expect_fn1, expect_fn2, combine_fn, ignore_none=True):
        """Creates a wrapper that combines two expectation functions

        Parameters
        ----------
        expect_fn1 : function
            an expectation function, where argument is a Test
        expect_fn2 : function
            an expectation function, where argument is a Test
        combine_fn : function
            Arguments: (x1, x2), the output of (expect_fn1, expect_fn2)
            Returns: bool, float, or int. See docstring for the Expect class
            for what different values in the output mean.
        ignore_none : bool
            If True, will take x1 if x2 is None and vice versa. If both are Nones,
            will return None without calling combine_fn.

        Returns
        -------
        function
            wrapped expectation function

        """
        # each expect_fn takes 'self' as input (i.e. wrapped by Expect.test or Expect.testcase)
        # combine_fn takes (x1, x2), where each is an output from expect_fn1 or
        # 2 (a single example within a testcase, which is a float, a bool, or
        # None) and combines them into a float, a bool, or None if
        # ignore_none=True, will take one of the inputs if the other is None
        # without passing them to the combine_fn (and return None if both are
        # Nones. otherwise, combine_fn must handle Nones)
        def tmp_fn(self):
            e1 = expect_fn1(self)
            e2 = expect_fn2(self)
            ret = []
            for list1, list2 in zip(e1, e2):
                r = []
                for z1, z2 in zip(list1, list2):
                    if ignore_none:
                        if z1 == None:
                            r.append(z2)
                            continue
                        elif z2 == None:
                            r.append(z1)
                            continue
                    r.append(combine_fn(z1, z2))
                ret.append(np.array(r))
            return ret
        return tmp_fn

    @staticmethod
    def combine_and(expect_fn1, expect_fn2):
        """Combines two expectation functions with the 'and' function
        See 'combine' for more details.
        """
        def combine_fn(x1, x2):
            return min(x1, x2)
        return Expect.combine(expect_fn1, expect_fn2, combine_fn)

    @staticmethod
    def combine_or(expect_fn1, expect_fn2):
        """Combines two expectation functions with the 'or' function
        See 'combine' for more details.
        """
        def combine_fn(x1, x2):
            return max(x1, x2)
        return Expect.combine(expect_fn1, expect_fn2, combine_fn)

    # SAMPLE EXPECTATION FUNCTION

    @staticmethod
    def eq(val=None):
        """Expect predictions to be equal to a value.
        See documentation for Expect.single

        Parameters
        ----------
        val : whatever or None
            If None, expect prediction to be equal to label. Otherwise, to be equal to val

        Returns
        -------
        function
            an expectation function

        """
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
        """Expect predictions not to change, with a tolerance threshold
        See documentation for Expect.pairwise.

        Parameters
        ----------
        tolerance : float
            If prediction changes but prediction probability is within the tolerance,
            will not consider it a failure.

        Returns
        -------
        function
            an expectation function

        """
        def expect(orig_pred, pred, orig_conf, conf, labels=None, meta=None):
            softmax = type(orig_conf) in [np.array, np.ndarray]
            try:
                if pred == orig_pred:
                    return True
            except ValueError: # np.array output
                if (pred == orig_pred).all():
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
        """Expect predictions to be monotonic
        See documentation for Expect.pairwise.

        Parameters
        ----------
        label : None or integer (only allowed if conf is softmax)
            If None, the original prediction label
        increasing : bool
            Whether we want monotonically increasing or decreasing
        tolerance : float
            If confidence goes down (up) for monotonically increasing
            (decreasing) by less than tolerance, will not be considered a failure.

        Returns
        -------
        function
            an expectation function

        """
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
                    conf_diff = -(orig_conf + conf)
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
