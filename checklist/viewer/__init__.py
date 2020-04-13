from .template_editor import TemplateEditor
from .test_summarizer import TestSummarizer

def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'viewer',
        'require': 'viewer/extension'
    }]
