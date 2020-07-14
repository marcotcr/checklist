import ipywidgets as widgets
from traitlets import Unicode, List, Dict
import os
import typing
import itertools

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
        mask_suggests: typing.List[typing.Union[str, tuple]], \
        format_fn: typing.Callable, \
        select_suggests_fn: typing.Callable, \
        tokenizer, \
        **kwargs):
        widgets.DOMWidget.__init__(self, **kwargs)
        self.format_fn = format_fn
        self.select_suggests_fn = select_suggests_fn
        # ONLY do tokenization here
        self.tokenizer = tokenizer
        self.bert_suggests = mask_suggests
        self.templates = [
            self.tokenize_template_str(s, tagged_keys, tag_dict) for \
            s in template_strs]
        self.on_msg(self.handle_events)


    def tokenize_template_str(self, template_str, tagged_keys, tag_dict, max_count=5):
        tagged_keys = list(tagged_keys)
        trans_keys = ["{" + key + "}" for key in tagged_keys]
        item_keys = [x[0] for x in tag_dict.items()]
        item_vals = [[x[1][:max_count]] if type(x[1]) not in [list, tuple] else x[1][:max_count] for x in tag_dict.items()]
        local_items = []
        for idx, key in enumerate(tagged_keys):
            self.tokenizer.add_tokens(trans_keys[idx])
        for item_val in itertools.product(*item_vals):
            if len(item_val) != len(set([str(x) for x in item_val])):
                continue
            local_item = {item_keys[i]: item_val[i] for i, _ in enumerate(item_val)}
            local_items.append(local_item)
            
        def _tokenize(text):
            tokens = [self.tokenizer.decode(x) for x in self.tokenizer.encode(text, add_special_tokens=False)]
            return [t for t in tokens if t]
        def get_meta(text):
            if text in trans_keys:
                idx = trans_keys.index(text)
                norm = tagged_keys[idx]
                lemma = norm.split(":")[-1]
                normalized_key = lemma.split('[')[0].split('.')[0]
                texts = list()
                for local_item in local_items:
                    try:
                        texts.append(self.format_fn(["{" + lemma  +"}"], local_item)[0])
                    except:
                        pass
                return (texts, norm, normalized_key)
            else:
                return text
        
        template_tokens = [get_meta(t) for t in _tokenize(template_str)]
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
