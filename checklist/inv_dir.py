from .abstract_test import AbstractTest
from .expect import Expect

class Inv(AbstractTest):
    def __init__(self, data, expect=None, threshold=0.1, meta=None):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta
        if expect is None:
            self.expect = Expect.wrap(Expect.all(Expect.pairwise_to_group(Expect.inv(threshold))))


class Dir(AbstractTest):
    def __init__(self, data, expect, meta=None):
        self.data = data
        self.expect = expect
        self.labels = None
        self.meta = meta
# expect(data, labels=None, meta=None)
