from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install

def enable_visual_interface():
    import notebook
    notebook.nbextensions.install_nbextension_python(
        "checklist.viewer", user=True, overwrite=True, symlink=True)
    notebook.nbextensions.enable_nbextension_python(
        "checklist.viewer")

class PostDevelopCommand(develop):
    """Pre-installation for development mode."""
    def run(self):
        develop.run(self)
        enable_visual_interface()

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        enable_visual_interface()
        # Install the

setup(name='checklist',
      version='0.0.2',
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
        'transformers>=2.8',
        'pattern>=3.6'
      ],
      cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
     },
      include_package_data=True,
      zip_safe=False
)
