#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

with open('jubakit/_version.py') as f:
  exec(f.read())

setup(name='jubakit',
      version='.'.join(str(x) for x in VERSION),
      description='Jubatus Toolkit',
      author='PFN & NTT',
      author_email='jubatus-team@googlegroups.com',
      url='http://jubat.us',
      license='MIT License',
      packages=find_packages(exclude=['jubakit.test']),
      install_requires=[
          'jubatus>=0.8.0',
          'psutil',
      ],
      classifiers=[
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python',
          'Topic :: Scientific/Engineering :: Information Analysis'
      ],
      test_suite = 'jubakit.test',
)
