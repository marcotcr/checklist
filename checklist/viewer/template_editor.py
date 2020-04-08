import ipywidgets as widgets
from traitlets import Unicode, List, Dict
from collections import defaultdict
import os
import typing
import itertools
from nltk.tokenize import MWETokenizer, word_tokenize
from copy import deepcopy

from .template import Template
from .token import Token
from .fake_data import candidate_dict

try:
    from IPython.core.display import display, Javascript
except:
    raise Exception("This module must be run in IPython.")
DIRECTORY = os.path.abspath(os.path.dirname(__file__))


# import logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)  # pylint: disable=invalid-name

@widgets.register
class TemplateEditor(widgets.DOMWidget):
    """An example widget."""
    _view_name = Unicode('TemplateEditorView').tag(sync=True)
    _model_name = Unicode('TemplateEditorModel').tag(sync=True)
    _view_module = Unicode('viewer').tag(sync=True)
    _model_module = Unicode('viewer').tag(sync=True)
    _view_module_version = Unicode('^0.1.0').tag(sync=True)
    _model_module_version = Unicode('^0.1.0').tag(sync=True)

    ori_str = Unicode('', help="The original sentence that needs to be tested.").tag(sync=True)
    masked_tokens = List([], help="The token list, with edited masks.").tag(sync=True)
    sources = List([], help="The name of the candidates lists").tag(sync=True)
    suggest_dict = Dict({}, help="The suggested tokens, for each sentence").tag(sync=True)

    def __init__(self, \
        sentences: typing.Dict[str, str], \
        sources: typing.List[str], \
        suggest_fn: typing.Callable, \
        get_testcase_fn: typing.Callable, \
        add_word_list_fn: typing.Callable, \
        processor,
        allowed_sources: typing.List[str]=None,
        **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        self.processor = processor
        self.add_word_list_fn = add_word_list_fn
        self.allowed_sources = allowed_sources if allowed_sources else None
        #sources = self.set_allowed_resources(allowed_sources, sources)
        self.set_resources(sources)
        self.set_ori_tokens(sentences)
        self.suggest_fn = suggest_fn
        self.get_testcase_fn = get_testcase_fn
        #super(TemplateCtrler, self).__init__(**kwargs)
        # #print(value)
        # Configures message handler
        self.on_msg(self.handle_events)

    def set_allowed_resources(self, allowed_sources, sources):
        if type(allowed_sources) == list:
            self.allowed_sources = allowed_sources
        elif type(allowed_sources) == dict:
            for name, word_list in allowed_sources.items():
                self.add_word_list_fn(name, word_list)
                if name not in sources:
                    sources.append(name)
            self.allowed_sources = list(allowed_sources.keys())
        else:
            self.allowed_sources = []
        return sources

    def set_resources(self, sources):
        if self.allowed_sources is not None:
            self.sources = [s for s in self.allowed_sources if s in sources]
        else:
            self.sources = sources

    def create_templates(self, sentences):
        self.templates = []
        for sentence in sentences:
            tokens = [Token(**t) for t in sentence["tokens"]]
            self.templates.append(Template(tokens=tokens, target=sentence["target"]))

    def _tokenizer(self, string: str) -> typing.List[str]:
        """
        A customized tokenizer. To make sure [MASK] would be treated as a whole.
        """
        version_dict = defaultdict(int)
        doc = self.processor(string)
        tokens = []
        for t in doc:
            if True or t.ent_type_ == "":
                tokens.append((t.text, ""))
            else:
                version_dict[t.ent_type_] += 1
                tokens.append((t.text, f"{t.ent_type_}{version_dict[t.ent_type_]}"))
        return tokens

    def handle_events(self, _, content, buffers):
        """
        Event handler. Users trigger python functions through the frontend interaction.
        """
        if content.get('event', '') == 'get_suggest':
            masked_tokens = content.get("masked_tokens", [])
            self.create_templates(masked_tokens)
            self.get_suggestions(self.templates)
        elif content.get('event', '') == 'confirm_fillin':
            fillins = content.get("fillin_dict", {})
            masked_tokens = content.get("masked_tokens", [])
            self.create_templates(masked_tokens)
            self.gen_test_cases(self.templates, fillins)
            # logger.info(output_test_results)
        elif content.get('event', '') == 'add_new_wordlist':
            name = content.get("name", None)
            word_list = content.get("word_list", None)
            if self.add_word_list_fn is not None:
                sources, new_source = self.add_word_list_fn(name, word_list)
                # logger.info(output_test_results)
                if new_source and self.allowed_sources is not None:
                    self.allowed_sources.append(new_source)
                self.set_resources(sources)



    def render(self):
        """
        Customized renderer. Directly load the bundled index.
        """
        display(Javascript(open(os.path.join(DIRECTORY, 'static', 'index.js')).read()))

    def set_ori_tokens(self, sentences: typing.Dict[str, str]) -> None:
        """
        Update the tested str.
        """
        self.suggest_dict = { }
        self.masked_tokens = [
            {
                "target" : target,
                "tokens": self._tokenizer(sentence) if type(sentence) == str else sentence
            } for target, sentence in sentences.items() ]

    def get_suggestions(self, sentence_tokens: typing.Dict[str, typing.List[str]]) -> None:
        """
        The function that gets the suggestions from the backend.
        """
        self.suggest_dict = { }
        self.suggest_dict = self.suggest_fn(sentence_tokens)

    def gen_test_cases(self,
        templates: typing.List[Template],
        fillin_dicts: typing.Dict[str, typing.List[str]]) -> typing.List[typing.Dict[str, str]]:
        self.get_testcase_fn(templates, fillin_dicts)
