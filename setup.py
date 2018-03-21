#!/usr/bin/env python

# Setup script for PyPI; use CMakeFile.txt to build extension modules

from setuptools import setup



setup(
    name='pyutils',
    packages=['pyutils'],
    classifiers=[
        'License :: OSI Approved :: BSD License'
    ],
    entry_points={
          'console_scripts': [
              'get_space = pyutils.get_space:main',
              'killprocs = pyutils.killprocs:main'
          ]
    },
    keywords='C++11, Python bindings',
    long_description="""pybind11""")
