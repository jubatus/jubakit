#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

"""
This program runs all *.py files under example/ directory.
Mainly intended for testing purpose.
"""

import sys
import os
import glob
import bz2

try:
  # Python 2
  from urllib import urlopen
except ImportError:
  # Python 3
  from urllib.request import urlopen

# Accept exceptions in following examples.
BLACK_LIST = ['classifier_twitter.py']

def download_bzip2(path, url):
  if os.path.exists(path): return
  print("Downloading {0} from {1}...".format(path, url))
  response = urlopen(url)
  with open(path, 'wb') as f:
    f.write(bz2.decompress(response.read()))

if __name__ == '__main__':
  # Go to example directory.
  os.chdir('example')

  # Prepare news20 dataset.
  download_bzip2('news20', 'https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/news20.bz2')
  download_bzip2('news20.t', 'https://www.csie.ntu.edu.tw/~cjlin/libsvmtools/datasets/multiclass/news20.t.bz2')

  # Run example codes.
  for example_py in glob.glob('*.py'):
    with open(example_py) as f:
      print('--- {0} -----------------------------'.format(example_py))
      try:
        exec(compile(f.read(), example_py, 'exec'))
      except:
        if example_py in BLACK_LIST:
          print("***** Exception raised in example (ignored as this example is blacklisted) *****")
        else:
          raise
      print()
