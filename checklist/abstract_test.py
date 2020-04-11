from abc import ABC, abstractmethod
import dill
from munch import Munch
import numpy as np
import inspect
from .expect import iter_with_optional, Expect

def load_test(file):
    dill._dill._reverse_typemap['ClassType'] = type
    return dill.load(open(file, 'rb'))

class AbstractTest(ABC):
    def __init__(self):
        self.data = None
        self.labels = None
        self.meta = None
        self.print_first = None
    def save(self, file):
        try:
            if not hasattr(self, 'inspect_source'):
                self.inspect_source = inspect.getsource(self.expect)
        except Exception as e:
            print('Warning: could not save inspect sourcecode')
            print(str(e))
        try:
            if type(self.agg_fn) != str and not hasattr(self, 'agg_source'):
                self.agg_source = inspect.getsource(self.agg_fn)
        except Exception as e:
            print('Warning: could not save agg_fn sourcecode')
            print(str(e))
        # expect = dill.dumps(self.expect, recurse=True)
        # self.expect = None
        dill.dump(self, open(file, 'wb'), recurse=True)

    @staticmethod
    def from_file(file):
        return load_test(file)
        # test, expect = load_test(file)
        # test.expect = dill.loads(expect)
        # return test
    
    def _extract_examples_per_testcase(
        self, xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=True):
        iters = list(iter_with_optional(xs, preds, confs, labels, meta))
        idxs = [0] if self.print_first else []
        idxs = [i for i in np.argsort(expect_results) if not only_include_fail or expect_results[i] <= 0]
        if self.print_first:
            if 0 in idxs:
                idxs.remove(0)
            idxs.insert(0, 0)
        idxs = idxs[:nsamples]
        iters = [iters[i] for i in idxs]
        return idxs, iters, [expect_results[i] for i in idxs]

    def print(self, xs, preds, confs, expect_results, labels=None, meta=None, format_example_fn=None, nsamples=3):
        idxs, iters, _ = self._extract_examples_per_testcase(
            xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=True)

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
        self.results.expect_results = self.expect(self)
        self.results.passed = Expect.aggregate(self.results.expect_results, self.agg_fn)

    def example_list_and_indices(self):
        if type(self.data[0]) in [list, np.array]:
            all = [(i, y) for i, x in enumerate(self.data) for y in x]
            result_indexes, examples = map(list, list(zip(*all)))
        else:
            examples = self.data
            result_indexes = list(range(len(self.data)))
        return examples, result_indexes

    def example_indices(self):
        if type(self.data[0]) in [list, np.array]:
            all = [(i, '') for i, x in enumerate(self.data) for y in x]
            result_indexes, examples = map(list, list(zip(*all)))
            return result_indexes
        else:
            return list(range(len(self.data)))

    def update_results_from_preds(self, preds, confs):
        result_indexes = self.example_indices()
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

    def to_raw_file(self, path, file_format=None, format_fn=str, header=None):
        # file_format can be jsonl, TODO
        # format_fn takes an example and outputs a line in the file
        if file_format == 'jsonl':
            import json
            format_fn = lambda x: json.dumps(x)
        ret = ''
        if header is not None:
            ret += header.strip('\n') + '\n'
        examples, indices = self.example_list_and_indices()
        examples = [format_fn(x).strip('\n') for x in examples]
        ret += '\n'.join(examples)
        f = open(path, 'w')
        f.write(ret)
        f.close()

    def _check_create_results(self, overwrite):
        if hasattr(self, 'results') and self.results and not overwrite:
            raise(Exception('Results exist. To overwrite, set overwrite=True'))
        self.results = Munch()

    def run_from_file(self, path, file_format=None, format_fn=None, ignore_header=False, overwrite=False):
        # file_format can be 'pred_only' (only preds, conf=1), TODO
        # Format_fn takes a line in the file and outputs (pred, conf)
        self._check_create_results(overwrite)
        f = open(path, 'r')
        if ignore_header:
            f.readline()
        preds = []
        confs = []
        if file_format == 'pred_only':
            format_fn = lambda x: (int(x), 1) if x.isdigit() else (x, 1)
        if file_format == 'pred_and_conf':
            def formatz(x):
                pred, conf = x.split()
                if pred.isdigit():
                    pred = int(pred)
                return pred, float(conf)
            format_fn = formatz
        elif file_format is None:
            pass
        else:
            raise(Exception('file_format %s not suported. Accepted values are pred_only, pred_and_conf' % file_format))
        for l in f:
            l = l.strip('\n')
            p, c = format_fn(l)
            preds.append(p)
            confs.append(c)
        self.update_results_from_preds(preds, confs)
        self.update_expect()



    def run(self, predict_and_confidence_fn, overwrite=False, verbose=True):
        self._check_create_results(overwrite)
        examples, result_indexes = self.example_list_and_indices()
        if verbose:
            print('Predicting %d examples' % len(examples))
        preds, confs = predict_and_confidence_fn(examples)
        self.update_results_from_preds(preds, confs)
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

    def summary(self, n=None, print_fn=None, format_example_fn=None, n_per_testcase=3):
        # print_fn_fn takes (xs, preds, confs, expect_results, labels=None, meta=None)
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
            print_fn(self.data[f], self.results.preds[f],
                     self.results.confs[f], self.results.expect_results[f],
                     label, meta, format_example_fn, nsamples=n_per_testcase)

    def _form_examples_per_testcase_for_viz(
        self, xs, preds, confs, expect_results, labels=None, meta=None, nsamples=3):
        idxs, iters, expect_results_sample = self._extract_examples_per_testcase(
            xs, preds, confs, expect_results, labels, meta, nsamples, only_include_fail=False)
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
        try:
            conf = example[2][example[1]]
        except:
            conf = None
        examples = [{
            "new": {"text": example[0], "pred": str(example[1]), "conf": conf},
            "old": old_example,
            "label": example[3],
            "succeed": expect_results_sample[start_idx:][idx] > 0
        } for idx, example in enumerate(iters[start_idx:]) ]
        return examples

    def _form_test_info(self):
        n = len(self.data)
        fails = self.fail_idxs().shape[0]
        filtered = self.filtered_idxs().shape[0]
        return {
            "name": "TESTNAME_PLACEHOLDER",
            "type": self.__class__.__name__.lower(),
            "expect_meta": {},
            "tags": [],
            "stats": {"nFailed": fails, "nTested": n - filtered, "nFiltered": filtered}
        }

    def visual_summary(self, n_per_testcase=3):
        self.check_results()
        # get the test meta
        test_info = self._form_test_info()
        testcases = []
        nonfiltered_idxs = np.where(self.results.passed != None)[0]
        for f in nonfiltered_idxs:
            # should be format_fn
            label, meta = self.label_meta(f)
            # print(label, meta)
            succeed = self.results.passed[f]
            if succeed is not None:
                examples = self._form_examples_per_testcase_for_viz(
                    self.data[f], self.results.preds[f],
                    self.results.confs[f], self.results.expect_results[f],
                    label, meta, nsamples=n_per_testcase)
            else:
                examples = []
            testcases.append({
                "examples": examples,
                "succeed": succeed,
                "tags": []
            })
        return test_info, testcases