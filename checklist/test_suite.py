import collections
from collections import defaultdict, OrderedDict
import dill
from .abstract_test import load_test, read_pred_file
from .test_types import MFT, INV, DIR

class TestSuite:
    def __init__(self, format_example_fn=None, print_fn=None):
        self.tests = OrderedDict()
        self.info = defaultdict(lambda: defaultdict(lambda: ''))
        self.format_example_fn = format_example_fn
        self.print_fn = print_fn

    @staticmethod
    def from_file(path):
        return load_test(path)

    def add(self, test, name, capability, description=None, format_example_fn=None, print_fn=None, overwrite=False):
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
        if name not in self.tests:
            raise(Exception('%s not in suite.' % name))
        del self.tests[name]
        del self.info[name]

    def to_raw_file(self, path, file_format=None, format_fn=None, header=None, n=None, seed=None):
        ret = ''
        if header is not None:
            ret += header.strip('\n') + '\n'
        self.test_ranges = {}
        all_examples = []
        current_idx = 0
        for name, t in self.tests.items():
            examples = t.to_raw_examples(file_format=file_format, format_fn=format_fn, n=n, seed=seed)
            self.test_ranges[name] = (current_idx, current_idx + len(examples))
            current_idx += len(examples)
            all_examples.extend(examples)
        ret += '\n'.join(all_examples)
        f = open(path, 'w')
        f.write(ret)
        f.close()

    def run_from_file(self, path, file_format=None, format_fn=None, ignore_header=False, overwrite=False):
        # file_format can be 'pred_only' (only preds, conf=1), TODO
        # Format_fn takes a line in the file and outputs (pred, conf)
        preds, confs = read_pred_file(path, file_format=file_format,
                                 format_fn=format_fn,
                                 ignore_header=ignore_header)
        for n, t in self.tests.items():
            p = preds[slice(*self.test_ranges[n])]
            c = confs[slice(*self.test_ranges[n])]
            t.run_from_preds_confs(p, c, overwrite=overwrite)

    def run(self, predict_and_confidence_fn, verbose=True, **kwargs):
        for n, t in self.tests.items():
            if verbose:
                print('Running', n)
            t.run(predict_and_confidence_fn, verbose=verbose, **kwargs)

    def summary(self, types=None, capabilities=None, **kwargs):
        vals = collections.defaultdict(lambda: 100, {'MFT': 0, 'INV': 1, 'DIR': 2})
        tests = self.tests.keys()
        capability_order = ['Vocabulary', 'Taxonomy', 'Robustness', 'Temporal', 'Fairness', 'SRL', 'Coref', 'Negation', 'Logic']
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
    def save(self, file):
        dill.dump(self, open(file, 'wb'), recurse=True)
