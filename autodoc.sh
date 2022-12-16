#!/usr/bin/bash
sphinx-apidoc -e -f -o docs/source nn_module_selector
cd docs
make html
cd - >/dev/null