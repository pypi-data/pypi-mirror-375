#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup file for TASauria

This allows any dynamic data required for this build to be collected.
At the moment this is just the version number, which is autodetected from source to reduce redundancy.
"""

import pathlib
import re
from setuptools import setup


ROOT = pathlib.Path(__file__).parent
VERSION_REGEX = re.compile(r'VersionInfo\(major=(\d+), minor=(\d+), micro=(\d+)\)', re.MULTILINE)


def detect_version() -> str:
    """
    Detect the TASauria python package version by detecting it in the source file.
    """

    with open(ROOT / 'tasauria' / '__init__.py', 'r', encoding='utf-8') as f:
        version_match = VERSION_REGEX.search(f.read())

        if not version_match:
            raise RuntimeError('version is not set or could not be located')

        version = '.'.join([version_match.group(1), version_match.group(2), version_match.group(3)])

    if not version:
        raise RuntimeError('version is not set')

    return version


setup(version=detect_version())
