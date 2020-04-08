import ipywidgets as widgets
from traitlets import Unicode, List, Dict
import os
import typing
import itertools
from nltk.tokenize import MWETokenizer, word_tokenize
from copy import deepcopy

try:
    from IPython.core.display import display, Javascript
except:
    raise Exception("This module must be run in IPython.")
DIRECTORY = os.path.abspath(os.path.dirname(__file__))

# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

@widgets.register
class MaskEditor(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('MaskEditorView').tag(sync=True)
    _model_name = Unicode('MaskEditorModel').tag(sync=True)
    _view_module = Unicode('viewer').tag(sync=True)
    _model_module = Unicode('viewer').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    ori_str = Unicode('', help="The original sentence that needs to be tested.").tag(sync=True)
    tokens = List([], help="The token arr of ori_str.").tag(sync=True)
    masked_tokens = List([], help="The token list, with edited masks.").tag(sync=True)
    suggest_dict = Dict({}, help="The suggested tokens").tag(sync=True)

    def __init__(self, ori_str: str, suggest_fn, return_list, **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        self.return_list = return_list
        self.set_ori_str(ori_str)
        self.fn = suggest_fn
        #super(TemplateCtrler, self).__init__(**kwargs)
        # #print(value)
        # Configures message handler
        self.on_msg(self.handle_events)

    def handle_events(self, _, content, buffers):
        """
        Event handler. Users trigger python functions through the frontend interaction.
        """
        if content.get('event', '') == 'get_suggest':
            tokens = content.get("masked_tokens", None)
            self.get_suggestions(tokens)
            #logger.info( self.masked_tokens, self.suggest_dict)
        elif content.get('event', '') == 'change_mask':
            self.masked_tokens = content.get("masked_tokens", None)
            self.suggest_dict = {}
        elif content.get('event', '') == 'confirm_fillin':
            fillins = content.get("fillin_dict", None)
            self.return_list.clear()
            output_test_results = self.run_test(self.masked_tokens, fillins)
            self.return_list.extend(output_test_results)
            # logger.info(output_test_results)
        elif content.get('event', '') == 'reset':
            self.masked_tokens = [s for s in self.tokens]
            self.suggest_dict = {}

    def _tokenizer(self, string: str) -> typing.List[str]:
        """
        A customized tokenizer. To make sure [MASK] would be treated as a whole.
        """
        mwtokenizer = MWETokenizer([('[', 'MASK', ']')], separator='')
        return mwtokenizer.tokenize(word_tokenize(string))

    def render(self):
        """
        Customized renderer. Directly load the bundled index.
        """
        display(Javascript(open(os.path.join(DIRECTORY, 'static', 'index.js')).read()))

    def set_ori_str(self, ori_str: str) -> None:
        """
        Update the tested str.
        """
        self.ori_str = ori_str
        # set the token
        self.tokens = self._tokenizer(self.ori_str)
        # also set a masked token
        self.masked_tokens = [s for s in self.tokens]
        self.suggest_dict = {}

    def get_suggestions(self, tokens: typing.List[str]) -> None:
        """
        The function that gets the suggestions from the backend.
        """
        self.suggest_dict = self.fn(self.masked_tokens)
        # suggest_dict = {}
        # for idx, token in enumerate(self.masked_tokens):
        #     if token == "[MASK]":
                # suggest_dict[idx] = [f'suggest-{i}' for i in range(idx)]
        # self.suggest_dict = suggest_dict

    def run_test(self,
        masked_tokens: typing.List[str],
        fillin_dict: typing.Dict[str, typing.List[str]]) -> typing.List[str]:
        outputs = []
        combinations = []
        for idx, fillins in fillin_dict.items():
            combinations.append([ (idx, fillin) for fillin in fillins ])

        fillin_combines = itertools.product(*combinations)

        for combine in itertools.product(*combinations):
            # combine: [(idx, word)]
            combined_dict = {int(x[0]): x[1] for x in combine}
            o = [ combined_dict[i] if i in combined_dict else w for i, w in enumerate(masked_tokens) ]
            o = ' '.join(o)
            o = o.replace("[MASK]", "")
            outputs.append(o)
        return outputs
