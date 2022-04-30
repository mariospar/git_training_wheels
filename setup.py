# -*- coding: utf-8 -*-
from os import name as os_name
from os import path, walk
from sys import version_info
from typing import List

from setuptools import find_packages, setup

name = "git_training_wheels"

rootdir = path.abspath(path.dirname(__file__))

# Python 3.8 or later needed
if version_info < (3, 8, 0, "final", 0):
    raise SystemExit("Python 3.8 or later is required!")

# Build a list of all project modules
packages = [
    dirname.replace("/", ".")
    for dirname, dirnames, filenames in walk(name)
    if "__init__.py" in filenames
]

# Scripts
scripts: List[str] = []
for dirname, dirnames, filenames in walk("scripts"):
    scripts.extend(
        path.join(dirname, filename) for filename in filenames if not filename.endswith(".bat")
    )

# Provide bat executables in the tarball (always for Win)
if os_name in {"ce", "nt"}:
    scripts.extend(f"{script}.bat" for script in scripts[:])

# Data_files (e.g. docs) need (directory, files-in-this-directory) tuples
data_files = []
for dirname, dirnames, filenames in walk("docs"):
    fileslist = []
    for filename in filenames:
        fullname = path.join(dirname, filename)
        fileslist.append(fullname)
    data_files.append((f"share/{name}/{dirname}", fileslist))

classifiers = [
    "Development Status :: 1 - Planning" "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Intended Audience :: Education",
    "Natural Language :: English",
    "Operating System :: OS Independent",
    "Topic :: Education",
    "Topic :: Software Development :: Version Control :: Git"
    "License :: OSI Approved :: MIT License",
]

extras_require = {
    "tests": [
        "tox >= 2.6.0",
        "pytest >= 3.0.3",
    ],
    "dev": [
        "check-manifest >= 0.35",
        "readme-renderer >= 16.0",
    ],
}

kw = {
    "name": name,
    "version": "0.1.0",
    "description": "Get to know git from the CLI!",
    "long_description": open(path.join(rootdir, "README.md"), encoding="utf-8").read(),
    "long_description_content_type": "text/markdown",
    "author": "Marios Paraskevas",
    "author_email": "mariosparaskevas00@gmail.com",
    "license": "MIT License",
    "url": "https://github.com/mariospar/git_training_wheels",
    "keywords": "git git-training-wheels git-tutorial",
    "classifiers": classifiers,
    "zip_safe": True,
    "scripts": scripts,
    "data_files": data_files,
    "packages": find_packages(),
    "extras_require": extras_require,
    "install_requires": "poetry-core",
}

print(kw)

if __name__ == "__main__":
    setup(**kw)
