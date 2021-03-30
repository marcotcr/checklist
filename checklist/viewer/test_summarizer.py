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

@widgets.register
class TestSummarizer(widgets.DOMWidget):
    """An testcase widget."""
    _view_name = Unicode('TestSummarizerView').tag(sync=True)
    _model_name = Unicode('TestSummarizerModel').tag(sync=True)
    _view_module = Unicode('viewer').tag(sync=True)
    _model_module = Unicode('viewer').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    stats = Dict({}).tag(sync=True)
    testcases = List([]).tag(sync=True)
    summarizer = Dict({}).tag(sync=True)

    def __init__(self, 
        test_summary: typing.Dict, 
        testcases: typing.List,
        **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)

        nlp = English()
        # ONLY do tokenization here (compatible with spaCy 2.3.x and 3.x.x)
        self.tokenizer = nlp.tokenizer

        self.max_return = 10
        self.reset_summary(test_summary)
        self.reset_testcases(testcases)
        self.on_msg(self.handle_events)
    
    def reset_summary(self, test_summary=None):
        self.summarizer = test_summary if test_summary else {}
    
    def reset_testcases(self, testcases=None):
        self.filtered_testcases = testcases if testcases else []
        self.tokenize_testcases()
        self.search(filter_tags=[], is_fail_case=True)
        
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

    def tokenize_testcases(self):
        for testcase in self.filtered_testcases:
            for e in testcase["examples"]:
                for tag in ["old", "new"]:
                    if not e[tag]:
                        continue
                    tokens = []
                    if type(e[tag]["text"]) != list:
                        e[tag]["tokens"] = [str(e[tag]["text"])]
                    else:
                        e[tag]["tokens"] = [str(s) for s in e[tag]["text"]]
                    for sentence in e[tag]["tokens"]:
                        tokens.append([t.text for t in self.tokenizer(sentence)])
                    e[tag]["tokens"] = tokens

    def render(self):
        """
        Customized renderer. Directly load the bundled index.
        """
        display(Javascript(open(os.path.join(DIRECTORY, 'static', 'index.js')).read()))

    def compute_stats_result(self, candidate_testcases):
        nfailed = len([ e for e in candidate_testcases if e["succeed"] == 0 ])
        self.stats = {
            "npassed": len(candidate_testcases) - nfailed,
            "nfailed": nfailed,
            "nfiltered": 0
        }

    def is_satisfy_filter(self, testcase, 
        filter_tags: typing.List[str], 
        is_fail_case: bool) -> bool:
        testcase_tags = testcase["tags"]
        texts = []
        for e in testcase["examples"]:
            for tag in ["old", "new"]:
                    if not e[tag]:
                        continue
                    for tokens in e[tag]["tokens"]:
                        texts += tokens
        def raw_text_search(tag, testcase_tags, text):
            text_searched = tag in text.lower()
            return tag in testcase_tags or text_searched
        is_tag_filtered = all([raw_text_search(t, testcase_tags, " ".join(texts)) for t in filter_tags])
        is_failured_filtered = not (is_fail_case and testcase["succeed"] == 1)
        return is_tag_filtered and is_failured_filtered

    def search(self, filter_tags: typing.List[str], is_fail_case: bool):
        self.testcases = []
        candidate_testcases_not_fail = [
            e for e in self.filtered_testcases if \
            self.is_satisfy_filter(e, filter_tags, False) 
        ]
        self.candidate_testcases = [
            e for e in candidate_testcases_not_fail if \
                not (is_fail_case and e["succeed"] == 1) 
        ]
        self.compute_stats_result(candidate_testcases_not_fail)
        self.to_slice_idx = 0
        self.fetch_example()

    def fetch_example(self):
        if self.to_slice_idx >= len(self.candidate_testcases):
            self.testcases = []
        else:
            new_examples = self.candidate_testcases[self.to_slice_idx : self.to_slice_idx+self.max_return]
            self.to_slice_idx += len(new_examples)
            self.testcases = [e for e in new_examples]