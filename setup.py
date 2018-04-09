#!/usr/bin/env python

import sys, os
import e340py

from setuptools import setup, find_packages

version_file = open(os.path.join('e340py', 'VERSION'))
version = version_file.read().strip()

setup(
    name = "e340py",
    packages=find_packages(),
    version=version,
    include_package_data=True,
    package_data={'e340py': ['VERSION']},
    entry_points={
          'console_scripts': [
              'dump_comments = e340py.dump_comments:main',
              'find_links = e340py.find_links:main',
              'add_points = e340py.add_points:main'
          ]
    },
)

