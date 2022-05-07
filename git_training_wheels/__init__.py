# -*- coding: utf-8 -*-
"""Sets the package version and bootstraps the app.

Raises:
    SystemExit: If python version is less than 3.8
"""
from sys import version_info

# Python 3.8 or later needed
if version_info < (3, 8, 0, "final", 0):
    raise SystemExit("Python 3.8 or later is required!")

from . import _version

__version__ = _version.get_versions()["version"]  # type: ignore[no-untyped-call]
