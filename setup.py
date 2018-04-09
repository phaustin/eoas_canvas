#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name = "e340py",
    version='0.0.5',
    packages=find_packages(),
    entry_points={
          'console_scripts': [
              'dump_comments = e340py.dump_comments:main',
              'find_links = e340py.find_links:main',
              'add_points = e340py.add_points:main'
          ]
    },
)

