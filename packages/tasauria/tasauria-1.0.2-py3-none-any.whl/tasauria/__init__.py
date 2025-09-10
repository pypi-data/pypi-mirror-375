"""
TASauria Python Library
~~~~~~~~~~~~~~~~~~~~~~~~

The Python interface library for TASauria, a plugin for remotely controlling the BizHawk emulator.

:copyright: (c) 2025-present Devon (scarletcafe) R.
:license: MIT, see LICENSE for more details.

"""

from typing import NamedTuple

from tasauria.client import TASauria


class VersionInfo(NamedTuple):
    """
    NamedTuple of the version info, in the style of sys.version_info
    """

    major: int
    minor: int
    micro: int


version_info: VersionInfo = VersionInfo(major=1, minor=0, micro=2)

__title__ = 'tasauria'
__author__ = 'scarletcafe'
__license__ = 'MIT'
__copyright__ = 'Copyright (c) 2025-present Devon (scarletcafe) R.'
__version__ = f'{version_info.major}.{version_info.minor}.{version_info.micro}'

__all__ = [
    "TASauria",
    "VersionInfo",
    "version_info"
]
