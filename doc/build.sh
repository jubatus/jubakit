#!/bin/sh

cd "$(dirname ${0})"

sphinx-apidoc -f -M -H "API Reference" -o source ../jubakit ../jubakit/test

# A dirty workaround to remove unnecessary "Subpackages" / "Submodules" header...
for FILE in source/jubakit*.rst; do
  perl -pi -e 'BEGIN {undef $/;} s/Sub(packages|modules)\n\-+\n//g' "${FILE}"
done

PYTHONPATH=.. make html
