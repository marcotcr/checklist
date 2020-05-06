# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys

sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))
sys.path.insert(0, os.path.abspath('../checklist'))

autodoc_mock_imports = [
    'spacy', 'spacy.cli', 'nltk', 'nltk.corpus', 'nltk.tree', 'pattern'
    'numpy', 'np', 'spacy.syntax.nn_parser.array', '__reduce_cython__',
    'numpy.dtype', 'spacy.syntax.nn_parser.array.__reduce_cython__', '_ARRAY_API', 
    'BertForMaskedLM'
]
# -- Project information -----------------------------------------------------

project = 'checklist'
copyright = '2020, Marco Tulio Ribeiro'
author = 'Marco Tulio Ribeiro'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.linkcode',
    'sphinx.ext.mathjax',
    'sphinx.ext.autosummary',
    'sphinx.ext.coverage',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', "static"]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']



# make github links resolve
def linkcode_resolve(domain, info):
    """
    Determine the URL corresponding to Python object
    This code is from
    https://github.com/numpy/numpy/blob/master/doc/source/conf.py#L290
    and https://github.com/Lasagne/Lasagne/pull/262
    """
    if domain != 'py':
        return None

    modname = info['module']
    fullname = info['fullname']

    submod = sys.modules.get(modname)
    if submod is None:
        return None

    obj = submod
    for part in fullname.split('.'):
        try:
            obj = getattr(obj, part)
        except:
            return None

    try:
        fn = inspect.getsourcefile(obj)
    except:
        fn = None
    if not fn:
        return None

    try:
        source, lineno = inspect.getsourcelines(obj)
    except:
        lineno = None

    if lineno:
        linespec = "#L%d-L%d" % (lineno, lineno + len(source) - 1)
    else:
        linespec = ""

    filename = info['module'].replace('.', '/')
    return "https://github.com/marcotcr/checklist/blob/master/%s.py%s" % (filename, linespec)