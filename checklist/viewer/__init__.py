def _jupyter_nbextension_paths():
    return [{
        'section': 'notebook',
        'src': 'static',
        'dest': 'viewer',
        'require': 'viewer/extension'
    }]
