from setuptools import setup, find_packages

setup(name='checklist',
      version='0.1',
      description='Beyond Accuracy: Behavioral Testing of NLP Models with CheckList',
      url='http://github.com/marcotcr/checklist',
      author='Marco Tulio Ribeiro',
      author_email='marcotcr@gmail.com',
      license='MIT',
      packages= find_packages(exclude=['js', 'node_modules', 'tests']),
      install_requires=[
        'numpy>=1.18',
        'spacy>=2.2',
        'munch>=2.5',
        'dill>=0.3.1',
        'jupyter>=1.0',
        'ipywidgets>=7.5',
        'transformers>=2.8'
      ],
      include_package_data=True,
      zip_safe=False
)

import notebook

notebook.nbextensions.install_nbextension_python(
    "checklist.viewer", user=True, overwrite=True, symlink=True)

notebook.nbextensions.enable_nbextension_python(
  "checklist.viewer")