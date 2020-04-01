from .abstract_test import AbstractTest
from .expect import Expect, iter_with_optional
import numpy as np

class Inv(AbstractTest):
    def __init__(self, data, expect=None, threshold=0.1, meta=None, agg_fn='all_except_first'):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta
        self.agg_fn = agg_fn
        self.print_first = True
        if expect is None:
            self.expect = Expect.inv(threshold)


class Dir(AbstractTest):
    def __init__(self, data, expect, meta=None, agg_fn='all_except_first'):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta
        self.agg_fn = agg_fn
        self.print_first = True
