import ipywidgets as widgets
from traitlets import Unicode, List, Dict
import os
import typing
from spacy.lang.en import English
from copy import deepcopy
try:
    from IPython.core.display import display, Javascript
except:
    raise Exception("This module must be run in IPython.")
DIRECTORY = os.path.abspath(os.path.dirname(__file__))

from .test_summarizer import TestSummarizer

@widgets.register
class SuiteSummarizer(TestSummarizer):
    """An testcase widget."""
    _view_name = Unicode('SuiteSummarizerView').tag(sync=True)
    _model_name = Unicode('SuiteSummarizerModel').tag(sync=True)
    _view_module = Unicode('viewer').tag(sync=True)
    _model_module = Unicode('viewer').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    test_infos = List([]).tag(sync=True)

    def __init__(self, 
        test_infos: typing.Dict, 
        select_test_fn: typing.Callable, \
        **kwargs):
        TestSummarizer.__init__(self, test_summary=None, testcases=[], **kwargs)
        self.test_infos = test_infos
        self.select_test_fn = select_test_fn
        self.on_msg(self.handle_events)

    def handle_events(self, _, content, buffers):
        """
        Event handler. Users trigger python functions through the frontend interaction.
        """
        if content.get('event', '') == 'apply_filter':
            filter_tags = content.get("filter_tags", [])
            is_fail_case = content.get("filter_fail_case", [])
            self.search(filter_tags, is_fail_case)
        elif content.get('event', '') == 'fetch_example':
            self.fetch_example()
        elif content.get('event', '') == 'switch_test':
            testname = content.get("testname", "")
            self.on_select_test(testname)

    def on_select_test(self, testname: str) -> None:
        if not self.select_test_fn:
            summary, testcases = None, []
        else:
            summary, testcases = self.select_test_fn(testname)
        self.reset_summary(summary)
        self.reset_testcases(testcases)