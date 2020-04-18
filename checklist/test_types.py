from .abstract_test import AbstractTest
from .expect import Expect

class MFT(AbstractTest):
    def __init__(self, data, expect=None, labels=None, meta=None, agg_fn='all',
                 templates=None, name=None, capability=None, description=None):
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
        if expect is None:
            expect = Expect.inv(threshold)
        super().__init__(data, expect, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, print_first=True, name=name,
                         capability=capability, description=description)

class DIR(AbstractTest):
    def __init__(self, data, expect, meta=None, agg_fn='all_except_first',
                 templates=None, name=None, labels=None, capability=None, description=None):
        super().__init__(data, expect, labels=labels, meta=meta, agg_fn=agg_fn,
                         templates=templates, print_first=True, name=name,
                         capability=capability, description=description)
