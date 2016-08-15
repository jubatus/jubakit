#!/bin/bash -uex

cd "$(dirname ${0})"

sphinx-apidoc -f -M -H "API Reference" -o source/api ../jubakit ../jubakit/test
mv -f source/api/modules.rst source/api/index.rst

# A dirty workaround to remove unnecessary "Subpackages" / "Submodules" header...
for FILE in source/api/jubakit*.rst; do
  perl -pi -e 'BEGIN {undef $/;} s/Sub(packages|modules)\n\-+\n//g' "${FILE}"
done

PYTHONPATH=.. make clean html
