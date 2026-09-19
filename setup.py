#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Python Setuptools for Mathics3 core

For the easiest installation:

    pip install -e .

For full installation:

    pip install -e .[full]


This will install the library in the default location. For instructions on
how to customize the install procedure read the output of:

    python setup.py --help install

In addition, there are some other commands:

    python setup.py clean -> will clean all trash (*.pyc and stuff)

To get a full list of available commands, read the output of:

    python setup.py --help-commands

"""

import logging
from setuptools import setup

log = logging.getLogger(__name__)


setup(
    # don't pack Mathics3 in egg because of media files, etc.
    zip_safe=False,
)
