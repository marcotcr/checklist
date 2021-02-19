##
## Copyright (c) Microsoft Corporation.
## Licensed under the MIT license.
##
# ---- update tools everything ----
pip install --user --upgrade setuptools wheel twine keyring artifacts-keyring
pip install -e .

# ---- remove previous build directories ----
rm -rf dist
rm -rf build
rm -rf checklist.egg-info

# ---- build SOURCE DIST (*.tar.gz) and WHEEL (*.whl) ----
python setup.py sdist bdist_wheel

# ---- updload file from DIST folder to PYPI ----
python -m twine upload --repository-url https://pkgs.dev.azure.com/aether-prototyping-incubation/_packaging/aether-prototyping-incubation/pypi/simple/ dist/*

