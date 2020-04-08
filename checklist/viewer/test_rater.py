import ipywidgets as widgets
from traitlets import Unicode, List, Dict
from collections import defaultdict
import os
import typing
import random

try:
    from IPython.core.display import display, Javascript
except:
    raise Exception("This module must be run in IPython.")
DIRECTORY = os.path.abspath(os.path.dirname(__file__))


# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

from typing import NamedTuple
"""
def TestExample(NamedTuple):
    instance: typing.List[typing.Dict[str, str]]
    result: str
    expect: str
    tags: typing.List[str]

def TestExample(NamedTuple):
    nTested: int
    nFailed: int
"""

@widgets.register
class TestRater(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('TestRaterView').tag(sync=True)
    _model_name = Unicode('TestRaterModel').tag(sync=True)
    _view_module = Unicode('viewer').tag(sync=True)
    _model_module = Unicode('viewer').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    condition = Unicode('').tag(sync=True)
    test_names = List([]).tag(sync=True)
    summarizer = Dict({}).tag(sync=True)
    stats = Dict({}).tag(sync=True)
    examples = List([]).tag(sync=True)

    def __init__(self, 
        # C1, C2, C3
        condition: str,
        tests: typing.List["Test"], 
        get_rate_func: typing.Callable,
        get_survey_func: typing.Callable, **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        # save the result
        self.get_rate_func = get_rate_func
        self.get_survey_func = get_survey_func
        # set the info that's needed for the test summarizer
        self.max_return = 10
        self.tests = tests
        self.test_names = [t.name for t in tests]
        # set the test
        self.switch_test(test_idx=0)
        # set the rate
        self.condition = condition
        # set the examples
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
            curr_idx = content.get("idx", 0)
            self.switch_test(curr_idx)
        elif content.get('event', '') == 'set_rate':
            scores = content.get("rates", [])
            reasons = content.get("reasons", [])
            testnames = content.get("testnames", [])
            self.get_rate_func(testnames, scores, reasons)
        elif content.get('event', '') == 'set_survey':
            scores = content.get("scores", [])
            surveys = content.get("surveys", [])
            freetext = content.get("freetext", "")
            self.get_survey_func(surveys, scores, freetext)

    def switch_test(self, test_idx: int) -> None:
        if test_idx >= 0 and test_idx < len(self.tests):
            self.summarizer = self.tests[test_idx].serialize()
            self.all_examples = self.tests[test_idx].serialize_all_examples()
            self.search(filter_tags=[], is_fail_case=True)
        else:
            self.summarizer = {}
            self.all_examples = []

    def render(self):
        """
        Customized renderer. Directly load the bundled index.
        """
        display(Javascript(open(os.path.join(DIRECTORY, 'static', 'index.js')).read()))

    def compute_stats_result(self, candidate_examples):
        self.stats = {
            "nTested": 0,
            "nFailed": 0
        }
        self.stats = {
            "nTested": len(candidate_examples),
            "nFailed": len([ e for e in candidate_examples if e["status"] == "fail" ])
        }

    def is_satisfy_filter(self, example, 
        filter_tags: typing.List[str], 
        is_fail_case: bool) -> bool:
        example_tags = example["tags"]
        is_succeed = example["status"] == "success"
        texts = [t["text"] for t in example["instance"]]
        def raw_text_search(tag, example_tags, texts):
            text_searched = any([tag in text.lower() for text in texts])
            return tag in example_tags or text_searched
        is_tag_filtered = all([raw_text_search(t, example_tags, texts) for t in filter_tags])
        is_failured_filtered = not (is_fail_case and is_succeed )
        return is_tag_filtered and is_failured_filtered

    def search(self, filter_tags: typing.List[str], is_fail_case: bool):
        self.examples = []
        self.candidate_examples = [
            e for e in self.all_examples if \
            self.is_satisfy_filter(e, filter_tags, is_fail_case) 
        ]
        candidate_examples_for_not_fail = [
            e for e in self.all_examples if \
            self.is_satisfy_filter(e, filter_tags, False) 
        ]
        self.compute_stats_result(candidate_examples_for_not_fail)
        self.to_slice_idx = 0
        self.fetch_example()

    def fetch_example(self):
        if self.to_slice_idx >= len(self.candidate_examples):
            self.examples = []
        else:
            new_examples = self.candidate_examples[self.to_slice_idx : self.to_slice_idx+self.max_return]
            self.to_slice_idx += len(new_examples)
            self.examples = [e for e in new_examples]
