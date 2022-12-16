#!/usr/bin/bash
sphinx-apidoc -e -f -o docs/source/api nn_module_selector
cd docs
make clean
make html
cd - >/dev/null