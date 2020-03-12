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
        'numpy',
        'spacy',
        'munch',
      ],
      include_package_data=True,
      zip_safe=False)
