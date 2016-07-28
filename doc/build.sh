#!/bin/sh

sphinx-apidoc -f -M -e -H "API Reference" -o source ../jubakit ../jubakit/test
PYTHONPATH=.. make html
