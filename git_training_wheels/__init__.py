# -*- coding: utf-8 -*-
from sys import version_info

# Python 3.8 or later needed
if version_info < (3, 8, 0, "final", 0):
    raise SystemExit("Python 3.8 or later is required!")

__version__ = "0.1.0"
