#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from setuptools import setup, find_packages

def _read(filename):
  with open(filename) as f:
    return f.read()

# Load package version.
exec(_read('jubakit/_version.py'))

def get_extras_requires():
  if sys.version_info < (2, 7):
    extras_requires = {
      'test': ['numpy<=1.10.3', 'scipy<=0.16.1',
               'scikit-learn', 'tweepy', 'jq'],
    }
  else:
    extras_requires = {
      'test': ['numpy', 'scipy',
               'scikit-learn', 'tweepy', 'jq'],
    }
  return extras_requires

setup(name='jubakit',
      version='.'.join(str(x) for x in VERSION),
      description='Jubatus Toolkit',
      long_description=_read('README.rst'),
      url='http://jubat.us',
      author='PFN & NTT',
      author_email='jubatus-team@googlegroups.com',
      license='MIT',
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'Topic :: Scientific/Engineering :: Information Analysis',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Programming Language :: Python :: 2',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
      ],
      packages=find_packages(exclude=['jubakit.test']),
      entry_points={
          'console_scripts': [
            'jubash=jubakit.shell:_main',
            'jubamodel=jubakit.model:_main',
          ],
      },
      install_requires=[
          'jubatus>=0.8.0',
          'psutil',
      ],
      extras_require=get_extras_requires(),
      test_suite = 'jubakit.test',
)
