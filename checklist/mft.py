from .abstract_test import AbstractTest
from .expect import Expect

class MFT(AbstractTest):
    def __init__(self, data, expect=None, labels=None, meta=None, agg_fn='all', templates=None):
        super().__init__()
        # print(super())
        self.data = data
        self.expect = expect
        self.labels = labels
        self.meta = meta
        self.templates = templates
        if labels is None and expect is None:
            raise(Exception('Must specify either \'expect\' or \'labels\''))
        if labels is not None and expect is None:
            self.expect = Expect.eq()
        self.agg_fn = agg_fn
        self.print_first = False
# expect(data, labels=None, meta=None)
