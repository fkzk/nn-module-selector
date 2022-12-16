#!/usr/bin/bash
sphinx-apidoc -e -f -o docs/source .
cd docs
make html
cd - >/dev/null