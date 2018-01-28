#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (c) 2017 - cologler <skyoflw@gmail.com>
# ----------
#
# ----------

import os
from setuptools import setup, find_packages

VERSION = '0.1.3.0'
DESCRIPTION = ''

long_description = None

if os.path.isfile('README.md'):
    with open('README.md') as f:
        long_description = f.read()

long_description = long_description or DESCRIPTION

setup(
    name = 'dependencyinjection',
    version = VERSION,
    description = DESCRIPTION,
    long_description = long_description or DESCRIPTION,
    classifiers = [],
    keywords = ['python', 'dependencyinjection', 'di', 'ioc'],
    author = 'cologler',
    author_email='skyoflw@gmail.com',
    url = 'https://github.com/Cologler/dependencyinjection-python',
    license = 'MIT',
    packages = find_packages(),
    include_package_data = True,
    zip_safe = False,
    install_requires = [ 'overload' ],
    entry_points = {},
)
