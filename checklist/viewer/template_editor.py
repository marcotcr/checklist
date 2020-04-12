import ipywidgets as widgets
from traitlets import Unicode, List, Dict
import os
import typing
import itertools
from spacy.attrs import LEMMA, ORTH, NORM
from spacy.lang.en import English

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

    templates = List([], help="The template list, with tags and masks.").tag(sync=True)
    bert_suggests = List([], help="The BERT suggestion list").tag(sync=True)

    def __init__(self, \
        template_strs: typing.List[str], \
        tagged_keys: typing.List[str], \
        tag_dict: typing.Dict[str, str], \
        bert_suggests: typing.List[typing.Union[str, tuple]], \
        format_fn: typing.Callable, \
        select_suggests_fn: typing.Callable, \
        **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        self.format_fn = format_fn
        self.select_suggests_fn = select_suggests_fn

        nlp = English()
        # ONLY do tokenization here
        self.tokenizer = nlp.Defaults.create_tokenizer(nlp)
        self.bert_suggests = bert_suggests
        self.templates = [
            self.tokenize_template_str(s, tagged_keys, tag_dict) for \
            s in template_strs]
        self.on_msg(self.handle_events)
    
    def tokenize_template_str(self, template_str, tagged_keys, tag_dict, max_count=3):
        tagged_keys = list(tagged_keys)
        trans_keys = ["{" + key + "}" for key in tagged_keys]
        #keys = list(fillins.keys()) + [bert_key]
        for idx, key in enumerate(tagged_keys):
            case = [{LEMMA: key.split(":")[-1], NORM: key, ORTH: trans_keys[idx] }]
            self.tokenizer.add_special_case(trans_keys[idx], case)
        tokens = self.tokenizer(template_str)
        template_tokens = []
        item_keys = [x[0] for x in tag_dict.items()]
        item_vals = [[x[1][:max_count]] if type(x[1][:max_count]) not in [list, tuple] else x[1] for x in tag_dict.items()]
        local_items = []
        for item_val in itertools.product(*item_vals):
            if len(item_val) != len(set([str(x) for x in item_val])):
                continue
            local_item = {item_keys[i]: item_val[i] for i, _ in enumerate(item_val)}
            local_items.append(local_item)                    

        for t in tokens:
            if t.norm_ in tagged_keys:
                tag = t.norm_
                texts = list()
                for local_item in local_items:
                    try:
                        text = self.format_fn(["{" + t.lemma_  +"}"], local_item)[0]
                        texts.append(text)
                    except:
                        pass
                template_tokens.append((texts, t.norm_))
            else:
                template_tokens.append(t.text)
        return template_tokens

    def handle_events(self, _, content, buffers):
        """
        Event handler. Users trigger python functions through the frontend interaction.
        """
        if content.get('event', '') == 'select_suggests':
            idxes = content.get("idxes", [])
            selected_suggests = [self.bert_suggests[i] for i in idxes]
            if self.select_suggests_fn:
                self.select_suggests_fn(selected_suggests)

    def render(self):
        """
        Customized renderer. Directly load the bundled index.
        """
        display(Javascript(open(os.path.join(DIRECTORY, 'static', 'index.js')).read()))