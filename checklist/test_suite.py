import collections
from collections import defaultdict, OrderedDict
import dill
import json
from .abstract_test import load_test, read_pred_file
from .test_types import MFT, INV, DIR

from .viewer.suite_summarizer import SuiteSummarizer

class TestSuite:
    def __init__(self, format_example_fn=None, print_fn=None):
        self.tests = OrderedDict()
        self.info = defaultdict(lambda: defaultdict(lambda: ''))
        self.format_example_fn = format_example_fn
        self.print_fn = print_fn

    @staticmethod
    def from_file(path):
        """Loads suite from file

        Parameters
        ----------
        path : string
            pickled (dill) file

        Returns
        -------
        TestSuite
            the suite

        """
        return load_test(path)

    def add(self, test, name=None, capability=None, description=None, format_example_fn=None, print_fn=None, overwrite=False):
        """Adds a test to suite

        Parameters
        ----------
        test : AbstractTest
            test
        name : string
            test name. If test has test.name, this is optional.
        capability : string
            test capability. If test has test.capability, this is optional.
        description : string
            test description. If test has test.capability, this is optional.
        format_example_fn : function
            If not None, use this to print a failed example within a test case
            Arguments: (x, pred, conf, label=None, meta=None)
        print_fn : function
            If not None, use this to print a failed test case.
            Arguments: (xs, preds, confs, expect_results, labels=None, meta=None)
        overwrite : bool
            If False, will raise exception if test with same name is already in suite.

        """
        if name is None and test.name is None:
            raise(Exception('If test does not have test.name, you must specify a name'))
        if capability is None and test.capability is None:
            raise(Exception('If test does not have test.capabiliy, you must specify a capability'))
        if name is None:
            name = test.name
        if capability is None:
            capability = test.capability
        if description is None:
            description = test.description
        if name in self.tests and not overwrite:
            raise(Exception('There is already a test named %s suite. Run with overwrite=True to overwrite' % name))
        if name in self.info:
            del self.info[name]
        type_map = {
            MFT: 'MFT',
            INV: 'INV',
            DIR: 'DIR',
        }
        typez = type_map[type(test)]
        self.tests[name] = test
        self.info[name]['capability'] = capability
        self.info[name]['type'] = typez
        if description:
            self.info[name]['description'] = description
        if format_example_fn:
            self.info[name]['format_example_fn'] = format_example_fn
        if print_fn:
            self.info[name]['print_fn'] = format_example_fn

    def remove(self, name):
        """Removes test from suite

        Parameters
        ----------
        name : string
            test name

        """
        if name not in self.tests:
            raise(Exception('%s not in suite.' % name))
        del self.tests[name]
        del self.info[name]

    def to_raw_file(self, path, file_format=None, format_fn=None, header=None, n=None, seed=None):
        """Flatten all tests into individual examples and print them to file.
        Indices of example to test case will be stored in each test.
        If n is not None, test.run_idxs will store the test case indexes.
        The line ranges for each test will be saved in self.test_ranges.

        Parameters
        ----------
        path : string
            File path
        file_format : string, must be one of 'jsonl', 'squad', 'qqp_test', or None
            None just calls str(x) for each example in self.data
            squad assumes x has x['question'] and x['passage'], or that format_fn does this
        format_fn : function or None
            If not None, call this function to format each example in self.data
        header : string
            If not None, first line of file
        n : int
            If not None, number of samples to draw
        seed : int
            Seed to use if n is not None

        """
        ret = ''
        self.test_ranges = {}
        all_examples = []
        add_id = False
        if file_format == 'qqp_test':
            add_id = True
            file_format = 'tsv'
            header = 'id\tquestion1\tquestion2'
        if header is not None:
            ret += header.strip('\n') + '\n'
        current_idx = 0
        for name, t in self.tests.items():
            examples = t.to_raw_examples(file_format=file_format, format_fn=format_fn, n=n, seed=seed)
            self.test_ranges[name] = (current_idx, current_idx + len(examples))
            if add_id and file_format == 'tsv':
                examples = ['%d\t%s' % (i, x) for i, x in zip(range(current_idx, current_idx + len(examples)), examples)]
            current_idx += len(examples)
            all_examples.extend(examples)
        if file_format == 'squad':
            ret_map = {'version': 'fake',
                       'data': []}
            for i, x in enumerate(all_examples):
                r = {'title': '',
                     'paragraphs': [{
                        'context': x['passage'],
                        'qas': [{'question' : x['question'],
                                 'id': str(i)
                                 }]
                      }]
                    }
                ret_map['data'].append(r)
            ret = json.dumps(ret_map)
        else:
            ret += '\n'.join(all_examples)
        f = open(path, 'w')
        f.write(ret)
        f.close()

    def run_from_file(self, path, file_format=None, format_fn=None, ignore_header=False, overwrite=False):
        """Update test.results (run tests) for every test, from a prediction file

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
        preds, confs = read_pred_file(path, file_format=file_format,
                                 format_fn=format_fn,
                                 ignore_header=ignore_header)
        for n, t in self.tests.items():
            p = preds[slice(*self.test_ranges[n])]
            c = confs[slice(*self.test_ranges[n])]
            t.run_from_preds_confs(p, c, overwrite=overwrite)

    def run(self, predict_and_confidence_fn, verbose=True, **kwargs):
        """Runs all tests in the suite
        See run in abstract_test.py .

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
        for n, t in self.tests.items():
            if verbose:
                print('Running', n)
            t.run(predict_and_confidence_fn, verbose=verbose, **kwargs)

    def summary(self, types=None, capabilities=None, **kwargs):
        """Print stats and example failures for each test.
        See summary in abstract_test.py

        Parameters
        ----------
        types : list(string)
            If not None, will only show tests of these test types.
            Options are MFT, INV, and DIR
        capabilities : list(string)
            If not None, will only show tests with these capabilities.
        **kwargs : type
            Will be passed as arguments to each test.summary()

        """
        vals = collections.defaultdict(lambda: 100, {'MFT': 0, 'INV': 1, 'DIR': 2})
        tests = self.tests.keys()
        capability_order = ['Vocabulary', 'Taxonomy', 'Robustness', 'NER',  'Fairness', 'Temporal', 'Negation', 'Coref', 'SRL', 'Logic']
        cap_order = lambda x:capability_order.index(x) if x in capability_order else 100
        caps = sorted(set([x['capability'] for x in self.info.values()]), key=cap_order)
        for capability in caps:
            if capabilities is not None and capability not in capabilities:
                continue
            print(capability)
            print()
            tests = [x for x in self.tests if self.info[x]['capability'] == capability]
            for n in tests:
                if types is not None and self.info[n]['type'] not in types:
                    continue
                print(n)
                if 'format_example_fn' not in kwargs:
                    kwargs['format_example_fn'] = self.info[n].get('format_example_fn', self.format_example_fn)
                if 'print_fn' not in kwargs:
                    kwargs['print_fn'] = self.info[n].get('print_fn', self.print_fn)
                self.tests[n].summary(**kwargs)
                print()
                print()
            print()
            print()

    def visual_summary_by_test(self, testname):
        """Displays visual summary for a single test.

        Parameters
        ----------
        testname : string
            name of the test

        Returns
        -------
        test.visual_summary
            summary

        """
        if not testname in self.tests:
            raise(Exception(f"There's no test named {testname} in the suite!"))
        test, info = self.tests[testname], self.info[testname]
        return test.visual_summary(
            name=testname,
            capability=info["capability"] if "capability" in info else None,
            description=info["description"] if "description" in info else None
        )

    def _on_select_test(self, testname: str):
        if not testname:
            test_info, testcases = {}, []
        else:
            if not testname in self.tests:
                raise(Exception(f"There's no test named {testname} in the suite!"))
            test, info = self.tests[testname], self.info[testname]
            test_info = test.form_test_info(
                name=testname,
                capability=info["capability"] if "capability" in info else None,
                description=info["description"] if "description" in info else None
            )
            n = 1 if self.info[testname]['type'] == 'MFT' else 2
            testcases = test.form_testcases(n_per_testcase=n)
        return test_info, testcases

    def visual_summary_table(self, types=None, capabilities=None):
        """Displays a matrix visualization of the test suite

        Parameters
        ----------
        types : list(string)
            If not None, will only show tests of these test types.
            Options are MFT, INV, and DIR
        capabilities : list(string)
            If not None, will only show tests with these capabilities.

        Returns
        -------
        SuiteSummarizer
            jupyter visualization

        """
        print("Please wait as we prepare the table data...")
        test_infos = []
        for testname in self.tests.keys():
            test, info = self.tests[testname], self.info[testname]

            local_info = test.form_test_info(
                name=testname,
                capability=info["capability"] if "capability" in info else None,
                description=info["description"] if "description" in info else None
            )
            if (not capabilities or local_info["capability"] in capabilities) and \
                (not types or local_info["type"] in types):
                test_infos.append(local_info)

        capability_order = ['Vocabulary', 'Taxonomy', 'Robustness', 'NER',  'Fairness', 'Temporal', 'Negation', 'Coref', 'SRL', 'Logic']
        cap_order = lambda x: capability_order.index(x["capability"]) if x in capability_order else 100
        test_infos = sorted(test_infos, key=cap_order)
        return SuiteSummarizer(
            test_infos=test_infos,
            select_test_fn=self._on_select_test
        )

    def save(self, path):
        """Serializes the suite and saves it to a file

        Parameters
        ----------
        path : string
            output file path

        """
        dill.dump(self, open(path, 'wb'), recurse=True)
