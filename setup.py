#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
A setuptools-based setup module.

See:
   https://packaging.python.org/en/latest/distributing.html
   https://github.com/pypa/sampleproject

Docs on the setup function kwargs:
   https://packaging.python.org/distributing/#setup-args

"""

from __future__ import absolute_import, print_function
from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import splitext
from os.path import abspath
from setuptools import find_packages
from setuptools import setup
from codecs import open # Use a consistent encoding.

current_dir = abspath(dirname(__file__))

# Get the long description from the README.rst file.
with open(join(current_dir, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="pytest-helper",
    version="15.10", # Versions should comply with PEP440.
    description="Automatically set the __PACKAGE__ attribute of a script.",
    long_description=long_description,
    author="Allen Barker",
    author_email="Allen.L.Barker@gmail.com",
    #url="https://github.com/pypa/sampleproject",

    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    include_package_data=True,
    zip_safe=False,

    license="MIT",
    classifiers=[
        # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
        # Development Status: Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        "Development Status :: 4 - Beta",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        # uncomment if you test on these interpreters:
        # 'Programming Language :: Python :: Implementation :: IronPython',
        # 'Programming Language :: Python :: Implementation :: Jython',
        # 'Programming Language :: Python :: Implementation :: Stackless',
        'Topic :: Utilities',
    ],

    keywords=["pytest", "unit tests", "unit test", "testing", "running tests"],
    install_requires=["pytest>=2.0"],
)

