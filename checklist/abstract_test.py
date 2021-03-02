from abc import ABC, abstractmethod
import dill
from munch import Munch
import numpy as np
import inspect
from .expect import iter_with_optional, Expect

from .viewer.test_summarizer import TestSummarizer

def load_test(file):
    dill._dill._reverse_typemap['ClassType'] = type
    with open(file, 'rb') as infile:
        return dill.load(infile)

def read_pred_file(path, file_format=None, format_fn=None, ignore_header=False):
    f = open(path, 'r', encoding='utf-8')
    if ignore_header:
        f.readline()
    preds = []
    confs = []
    if file_format is None and format_fn is None:
        file_format = 'pred_and_softmax'
    if file_format == 'pred_only':
        format_fn = lambda x: (x, 1)
    elif file_format == 'binary_conf':
        def formatz(x):
            conf = float(x)
            confs = np.array([1 - conf, conf])
            pred = int(np.argmax(confs))
            return pred, confs
        format_fn = formatz
    elif file_format == 'softmax':
        def formatz(x):
            confs = np.array([float(y) for y in x.split()])
            pred = int(np.argmax(confs))
            return pred, confs
        format_fn = formatz
    elif file_format == 'pred_and_conf':
        def formatz(x):
            pred, conf = x.split()
            if pred.isdigit():
                pred = int(pred)
            return pred, float(conf)
        format_fn = formatz
    elif file_format == 'pred_and_softmax':
        def formatz(x):
            allz = x.split()
            pred = allz[0]
            confs = np.array([float(x) for x in allz[1:]])
            if pred.isdigit():
                pred = int(pred)
            return pred, confs
        format_fn = formatz
    elif file_format is None:
        pass
    else:
        raise(Exception('file_format %s not suported. Accepted values are pred_only, softmax, binary_conf, pred_and_conf, pred_and_softmax' % file_format))
    for l in f:
        l = l.strip('\n')
        p, c = format_fn(l)
        preds.append(p)
        confs.append(c)
    if file_format == 'pred_only' and all([x.isdigit() for x in preds]):
        preds = [int(x) for x in preds]
    return preds, confs

class AbstractTest(ABC):
    def __init__(self, data, expect, labels=None, meta=None, agg_fn='all',
                 templates=None, print_first=None, name=None, capability=None,
                 description=None):
        self.data = data
        self.expect = expect
        self.labels = labels
        self.meta = meta
        self.agg_fn = agg_fn
        self.templates = templates
        self.print_first = print_first
        self.run_idxs = None
        self.result_indexes = None
        self.name = name
        self.capability = capability
        self.description = description
    def save(self, file):
        dill.dump(self, open(file, 'wb'), recurse=True)

    @staticmethod
    def from_file(file):
        return load_test(file)

    def _extract_examples_per_testcase(
        self, xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=True):
        iters = list(iter_with_optional(xs, preds, confs, labels, meta))
        idxs = [0] if self.print_first else []
        idxs = [i for i in np.argsort(expect_results) if not only_include_fail or expect_results[i] <= 0]
        if preds is None or (type(preds) == list and len(preds) == 0) or len(idxs) > len(iters):
            return None
        if self.print_first:
            if 0 in idxs:
                idxs.remove(0)
            idxs.insert(0, 0)
        idxs = idxs[:nsamples]
        iters = [iters[i] for i in idxs]
        return idxs, iters, [expect_results[i] for i in idxs]

    def print(self, xs, preds, confs, expect_results, labels=None, meta=None, format_example_fn=None, nsamples=3):
        result = self._extract_examples_per_testcase(
            xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=True)
        if not result:
            return
        idxs, iters, _ = result
        for x, pred, conf, label, meta in iters:
            print(format_example_fn(x, pred, conf, label, meta))
        if type(preds) in [np.array, np.ndarray, list] and len(preds) > 1:
            print()
        print('----')

    def set_expect(self, expect):
        """Sets and updates expectation function

        Parameters
        ----------
        expect : function
            Expectation function, takes an AbstractTest (self) as parameter
            see expect.py for details
        """
        self.expect = expect
        self.update_expect()

    def update_expect(self):
        self._check_results()
        self.results.expect_results = self.expect(self)
        self.results.passed = Expect.aggregate(self.results.expect_results, self.agg_fn)

    def example_list_and_indices(self, n=None, seed=None):
        """Subsamples test cases

        Parameters
        ----------
        n : int
            Number of testcases to sample
        seed : int
            Seed to use

        Returns
        -------
        tuple(list, list)
            First list is a list of examples
            Second list maps examples to testcases.

        For example, let's say we have two testcases: [a, b, c] and [d, e].
        The first list will be [a, b, c, d, e]
        the second list will be [0, 0, 0, 1, 1]

        Also updates self.run_idxs if n is not None to indicate which testcases
        were run. Also updates self.result_indexes with the second list.

        """
        if seed is not None:
            np.random.seed(seed)
        self.run_idxs = None
        idxs = list(range(len(self.data)))
        if n is not None:
            idxs = np.random.choice(idxs, min(n, len(idxs)), replace=False)
            self.run_idxs = idxs
        if type(self.data[0]) in [list, np.array, np.ndarray]:
            all = [(i, y) for i in idxs for y in self.data[i]]
            result_indexes, examples = map(list, list(zip(*all)))
        else:
            examples = [self.data[i] for i in idxs]
            result_indexes = idxs# list(range(len(self.data)))
        self.result_indexes = result_indexes
        return examples, result_indexes

    def update_results_from_preds(self, preds, confs):
        """Updates results from preds and confs
        Assumes that example_lists_and_indices or to_raw_examples or to_raw_file
        was called before, so that self.result_indexes exists
        Parameters
        ----------
        preds : list
            Predictions
        confs : list
            Confidences

        Updates self.results.preds and self.results.confs
        """
        result_indexes = self.result_indexes
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
            self.results.preds = [None for _ in self.data]
            self.results.confs = [None for _ in self.data]
            for i, p, c in zip(result_indexes, preds, confs):
                self.results.preds[i] = p
                self.results.confs[i] = c

    def recover_example_list_and_indices(self):
        """Recovers a previously computed example_list_and_indices"""
        idxs = list(range(len(self.data)))
        if self.run_idxs is not None:
            idxs = self.run_idxs
        if type(self.data[0]) in [list, np.array, np.ndarray]:
            examples = [y for i in idxs for y in self.data[i]]
        else:
            examples = [self.data[i] for i in idxs]
        result_indexes = self.result_indexes
        return examples, result_indexes

    def to_raw_examples(self, file_format=None, format_fn=None, n=None, seed=None, new_sample=True):
        """Flattens all test examples into a single list

        Parameters
        ----------
        file_format : string, must be one of 'jsonl', 'tsv', or None
            None just calls str(x) for each example in self.data
        format_fn : function or None
            If not None, call this function to format each example in self.data
        n : int
            If not None, number of samples to draw
        seed : int
            Seed to use if n is not None
        new_sample: bool
            If False, will rely on a previous sample and ignore the 'n' and 'seed' parameters

        Returns
        -------
        list(string)
            List of all examples. Indices of example to test case will be
            stored in self.result_indexes. If n is not None, self.run_idxs will
            store the test case indexes.
        """
        if file_format == 'jsonl':
            import json
            format_fn = lambda x: json.dumps(x)
        elif file_format == 'tsv':
            format_fn = lambda x: '\t'.join(x).replace('\n', ' ')
        else:
            if format_fn is None:
                format_fn = lambda x: str(x).replace('\n', ' ')
        if new_sample:
            examples, indices = self.example_list_and_indices(n, seed=seed)
        else:
            examples, indices = self.recover_example_list_and_indices()
        examples = [format_fn(x) for x in examples]
        return examples

    def to_raw_file(self, path, file_format=None, format_fn=str, header=None, n=None, seed=None):
        """Flatten test cases into individual examples and print them to file.
        Indices of example to test case will be stored in self.result_indexes.
        If n is not None, self.run_idxs will store the test case indexes.

        Parameters
        ----------
        path : string
            File path
        file_format : string, must be one of 'jsonl', 'tsv', or None
            None just calls str(x) for each example in self.data
        format_fn : function or None
            If not None, call this function to format each example in self.data
        header : string
            If not None, first line of file
        n : int
            If not None, number of samples to draw
        seed : int
            Seed to use if n is not None
        """
        # file_format can be jsonl, TODO
        # format_fn takes an example and outputs a line in the file
        ret = ''
        if header is not None:
            ret += header.strip('\n') + '\n'
        examples = self.to_raw_examples(file_format=file_format, format_fn=format_fn, n=n, seed=seed)
        ret += '\n'.join(examples)
        f = open(path, 'w')
        f.write(ret)
        f.close()

    def _results_exist(self):
        return hasattr(self, 'results') and self.results

    def _check_results(self):
        if not self._results_exist():
            raise(Exception('No results. Run run() first'))

    def _check_create_results(self, overwrite, check_only=False):
        if self._results_exist() and not overwrite:
            raise(Exception('Results exist. To overwrite, set overwrite=True'))
        if not check_only:
            self.results = Munch()

    def run_from_preds_confs(self, preds, confs, overwrite=False):
        """Update self.results (run tests) from list of predictions and confidences

        Parameters
        ----------
        preds : list
            predictions
        confs : list
            confidences
        overwrite : bool
            If False, raise exception if results already exist
        """
        self._check_create_results(overwrite)
        self.update_results_from_preds(preds, confs)
        self.update_expect()

    def run_from_file(self, path, file_format=None, format_fn=None, ignore_header=False, overwrite=False):
        """Update self.results (run tests) from a prediction file

        Parameters
        ----------
        path : string
            prediction file path
        file_format : string
            None, or one of 'pred_only', 'softmax', binary_conf', 'pred_and_conf', 'pred_and_softmax', 'squad',
            pred_only: each line has a prediction
            softmax: each line has prediction probabilities separated by spaces
            binary_conf: each line has the prediction probability of class 1 (binary)
            pred_and_conf: each line has a prediction and a confidence value, separated by a space
            pred_and_softmax: each line has a prediction and all softmax probabilities, separated by a space
            squad: TODO
        format_fn : function
            If not None, function that reads a line in the input file and outputs a tuple of (prediction, confidence)
        ignore_header : bool
            If True, skip first line in the file
        overwrite : bool
            If False, raise exception if results already exist
        """
        # file_format can be 'pred_only' (only preds, conf=1), TODO
        # Format_fn takes a line in the file and outputs (pred, conf)
        # Checking just to avoid reading the file in vain
        self._check_create_results(overwrite, check_only=True)
        preds, confs = read_pred_file(path, file_format=file_format,
                                 format_fn=format_fn,
                                 ignore_header=ignore_header)
        self.run_from_preds_confs(preds, confs, overwrite=overwrite)



    def run(self, predict_and_confidence_fn, overwrite=False, verbose=True, n=None, seed=None):
        """Runs test

        Parameters
        ----------
        predict_and_confidence_fn : function
            Takes as input a list of examples
            Outputs a tuple (predictions, confidences)
        overwrite : bool
            If False, raise exception if results already exist
        verbose : bool
            If True, print extra information
        n : int
            If not None, number of samples to draw
        seed : int
            Seed to use if n is not None

        """
        # Checking just to avoid predicting in vain, will be created in run_from_preds_confs
        self._check_create_results(overwrite, check_only=True)
        examples, result_indexes = self.example_list_and_indices(n, seed=seed)

        if verbose:
            print('Predicting %d examples' % len(examples))
        preds, confs = predict_and_confidence_fn(examples)
        self.run_from_preds_confs(preds, confs, overwrite=overwrite)

    def fail_idxs(self):
        self._check_results()
        return np.where(self.results.passed == False)[0]

    def filtered_idxs(self):
        self._check_results()
        return np.where(self.results.passed == None)[0]

    def get_stats(self):
        stats = Munch()
        self._check_results()
        n_run = n = len(self.data)
        if self.run_idxs is not None:
            n_run = len(self.run_idxs)
        fails = self.fail_idxs().shape[0]
        filtered = self.filtered_idxs().shape[0]
        nonfiltered = n_run - filtered
        stats.testcases = n
        if n_run != n:
            stats.testcases_run = n_run
        if filtered:
            stats.after_filtering = nonfiltered
            stats.after_filtering_rate = 100 * nonfiltered / n_run
        if nonfiltered != 0:
            stats.fails = fails
            stats.fail_rate = 100 * fails / nonfiltered
        return stats


    def print_stats(self):
        stats = self.get_stats()
        print('Test cases:      %d' % stats.testcases)
        if 'testcases_run' in stats:
            print('Test cases run:  %d' % stats.testcases_run)
        if 'after_filtering' in stats:
            print('After filtering: %d (%.1f%%)' % (stats.after_filtering, stats.after_filtering_rate))
        if 'fails' in stats:
            print('Fails (rate):    %d (%.1f%%)' % (stats.fails, stats.fail_rate))

    def _label_meta(self, i):
        if self.labels is None:
            label = None
        else:
            label = self.labels if type(self.labels) not in [list, np.array, np.ndarray] else self.labels[i]
        if self.meta is None:
            meta = None
        else:
            meta = self.meta if type(self.meta) not in [list, np.array, np.ndarray] else self.meta[i]
        return label, meta

    def summary(self, n=3, print_fn=None, format_example_fn=None, n_per_testcase=3):
        """Print stats and example failures

        Parameters
        ----------
        n : int
            number of example failures to show
        print_fn : function
            If not None, use this to print a failed test case.
            Arguments: (xs, preds, confs, expect_results, labels=None, meta=None)
        format_example_fn : function
            If not None, use this to print a failed example within a test case
            Arguments: (x, pred, conf, label=None, meta=None)
        n_per_testcase : int
            Maximum number of examples to show for each test case
        """
        self.print_stats()
        if not n:
            return
        if print_fn is None:
            print_fn = self.print
        def default_format_example(x, pred, conf, *args, **kwargs):
            softmax = type(conf) in [np.array, np.ndarray]
            binary = False
            if softmax:
                if conf.shape[0] == 2:
                    conf = conf[1]
                    return '%.1f %s' % (conf, str(x))
                elif conf.shape[0] <= 4:
                    confs = ' '.join(['%.1f' % c for c in conf])
                    return '%s %s' % (confs, str(x))
                else:
                    conf = conf[pred]
                    return '%s (%.1f) %s' % (pred, conf, str(x))
            else:
                return '%s %s' % (pred, str(x))

        if format_example_fn is None:
            format_example_fn = default_format_example
        fails = self.fail_idxs()
        if fails.shape[0] == 0:
            return
        print()
        print('Example fails:')
        fails = np.random.choice(fails, min(fails.shape[0], n), replace=False)
        for f in fails:
            d_idx = f if self.run_idxs is None else self.run_idxs[f]
            # should be format_fn
            label, meta = self._label_meta(d_idx)
            # print(label, meta)
            print_fn(self.data[d_idx], self.results.preds[d_idx],
                     self.results.confs[d_idx], self.results.expect_results[f],
                     label, meta, format_example_fn, nsamples=n_per_testcase)

    def _form_examples_per_testcase_for_viz(
        self, xs, preds, confs, expect_results, labels=None, meta=None, nsamples=3):
        result = self._extract_examples_per_testcase(
            xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=False)
        if not result:
            return []
        idxs, iters, expect_results_sample = result
        if not iters:
            return []
        start_idx = 1 if self.print_first else 0
        if self.print_first:
            base = iters[0]
            try:
                conf = base[2][base[1]]
            except:
                conf = None
            old_example = {"text": base[0], "pred": str(base[1]), "conf": conf}
        else:
            old_example = None

        examples = []
        for idx, e in enumerate(iters[start_idx:]):
            try:
                conf = e[2][e[1]]
            except:
                conf = None
            example = {
                "new": {"text": e[0], "pred": str(e[1]), "conf": conf},
                "old": old_example,
                "label": e[3],
                "succeed": int(expect_results_sample[start_idx:][idx] > 0)
            }
            examples.append(example)
        return examples

    def form_test_info(self, name=None, description=None, capability=None):
        n_run = n = len(self.data)
        if self.run_idxs is not None:
            n_run = len(self.run_idxs)
        fails = self.fail_idxs().shape[0]
        filtered = self.filtered_idxs().shape[0]
        return {
            "name": name if name else self.name,
            "description": description if description else self.description,
            "capability": capability if capability else self.capability,
            "type": self.__class__.__name__.lower(),
            "tags": [],
            "stats": {
                "nfailed": fails,
                "npassed": n_run - filtered - fails,
                "nfiltered": filtered
            }
        }
    def form_testcases(self, n_per_testcase=3):
        self._check_results()
        testcases = []
        nonfiltered_idxs = np.where(self.results.passed != None)[0]
        for f in nonfiltered_idxs:
            d_idx = f if self.run_idxs is None else self.run_idxs[f]
             # should be format_fn
            label, meta = self._label_meta(d_idx)
             # print(label, meta)
            succeed = self.results.passed[f]
            if succeed is not None:
                examples = self._form_examples_per_testcase_for_viz(
                    self.data[d_idx], self.results.preds[d_idx],
                    self.results.confs[d_idx], self.results.expect_results[f],
                    label, meta, nsamples=n_per_testcase)
            else:
                examples = []
            if examples:
                testcases.append({
                    "examples": examples,
                    "succeed": int(succeed),
                    "tags": []
                })
        return testcases

    def visual_summary(self, name=None, description=None, capability=None, n_per_testcase=3):
        self._check_results()
        # get the test meta
        test_info = self.form_test_info(name, description, capability)
        testcases = self.form_testcases(n_per_testcase)
        return TestSummarizer(test_info, testcases)
