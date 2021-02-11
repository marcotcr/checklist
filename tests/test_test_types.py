"""unit tests for test suite creation with different test types"""
from unittest import TestCase
from checklist.test_types import MFT, DIR, INV
from checklist.editor import Editor
from checklist.expect import Expect


class TestTestTypes(TestCase):
    editor = Editor()
    dummy_test_data = editor.template(
        templates=["example 1", "example 2"], meta=False, labels=["label1", "label2"])
    test_id = "100"

    def test_mft_w_test_id(self):
        mft_test = MFT(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="mft test with test id",
                       test_id=self.test_id)
        assert mft_test.test_id == self.test_id

    def test_mft_wo_test_id(self):
        mft_test = MFT(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="mft test without test id")
        assert mft_test.test_id is None

    def test_dir_w_test_id(self):
        dir_test = DIR(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="dir test with test id",
                       test_id=self.test_id)
        assert dir_test.test_id == self.test_id

    def test_dir_wo_test_id(self):
        dir_test = DIR(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="dir test without test id")
        assert dir_test.test_id is None

    def test_inv_w_test_id(self):
        inv_test = INV(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="inv test with test id",
                       test_id=self.test_id)
        assert inv_test.test_id == self.test_id

    def test_inv_wo_test_id(self):
        inv_test = INV(**self.dummy_test_data,
                       expect=Expect.eq(),
                       name="inv test without test id")
        assert inv_test.test_id is None
