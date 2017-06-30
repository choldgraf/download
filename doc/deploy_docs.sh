#!/bin/sh

# Installs
pip install codecov sphinx sphinx-gallery

# Code coverage
codecov

# Deploy doctr
pip install matplotlib pandas pillow
set -e
cd doc
make html
cd ..
pip install doctr
doctr deploy . --built-docs doc/_build/html
