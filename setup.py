#!/usr/bin/env python
# -*- coding: utf-8 -*-

import versioneer

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools

    use_setuptools()
    from setuptools import setup

if __name__ == "__main__":
    setup(version=versioneer.get_version(), cmdclass=versioneer.get_cmdclass())  # type: ignore[no-untyped-call]
